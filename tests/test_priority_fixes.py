"""Isolated API-contract regressions. No real Vectorworks import or automatic entrypoints run."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

SRC = Path(__file__).resolve().parents[1] / 'src'


def load_functions(filename, vs):
    tree = ast.parse((SRC / filename).read_text(encoding='utf-8'))
    # Keep definitions/constants only: never import vs or execute tool entrypoints.
    tree.body = [node for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.Assign))]
    namespace = {'vs': vs}
    exec(compile(tree, filename, 'exec'), namespace)
    return namespace


class ResourceSafetyTests(unittest.TestCase):
    def setUp(self):
        self.vs = SimpleNamespace(
            IsResourceReferenced=Mock(return_value=(False, '')),
            GetObjectVariableBoolean=Mock(return_value=False),
            GetName=Mock(side_effect=lambda h: h))
        self.ns = load_functions('1 RESOURCE AUDITOR v2.7.1.py', self.vs)

    def test_documented_reference_tuple(self):
        self.assertIs(self.ns['is_referenced']('local'), False)
        self.vs.IsResourceReferenced.return_value = (True, '/reference.vwx')
        self.assertIs(self.ns['is_referenced']('ref'), True)
        self.assertEqual(self.ns['modification_block']('ref'), 'referenced')
        self.vs.GetObjectVariableBoolean.assert_not_called()

    def test_unknown_reference_status_fails_closed(self):
        for result in [False, None, (), (False,), (False, '', 3),
                       ('false', ''), (0, ''), (False, None), [False, '']]:
            with self.subTest(result=result):
                self.vs.IsResourceReferenced.return_value = result
                self.assertIsNone(self.ns['is_referenced']('h'))
                self.assertEqual(self.ns['modification_block']('h'), 'unknown')
        self.vs.IsResourceReferenced.side_effect = RuntimeError('unsupported')
        self.assertEqual(self.ns['modification_block']('h'), 'unknown')
        del self.vs.IsResourceReferenced
        self.assertEqual(self.ns['modification_block']('h'), 'unknown')

    def test_locked_resources_still_blocked(self):
        self.vs.GetObjectVariableBoolean.return_value = True
        self.assertEqual(self.ns['modification_block']('h'), 'locked')
        self.vs.GetObjectVariableBoolean.assert_called_with('h', 700)
        self.vs.GetObjectVariableBoolean.side_effect = RuntimeError('no lock status')
        self.assertEqual(self.ns['modification_block']('h'), 'unknown')

    def test_audit_only_local_unlocked_resources_are_editable(self):
        states = {'local': None, 'ref': 'referenced', 'lock': 'locked', 'bad': 'unknown'}
        self.ns.update(resources_of_type=lambda _: list(states),
                       qualifies=lambda *args: True,
                       attached_record_names=lambda _: [],
                       modification_block=lambda h: states[h])
        audit = self.ns['audit_resources'](16, [], 'ALL', ['Record'])
        for bucket, handle in [('missing', 'local'), ('referenced_missing', 'ref'),
                               ('locked_missing', 'lock'), ('unknown_missing', 'bad')]:
            self.assertEqual(audit[bucket], [(handle, handle, ['Record'])])

    def configure_find_add(self, status_sequence):
        self.vs.StrDialog = Mock(side_effect=['16', '', 'Record'])
        self.vs.DidCancel = Mock(return_value=False)
        self.vs.YNDialog = Mock(return_value=True)
        self.vs.AlrtDialog = Mock()
        self.vs.SetRecord = Mock()
        self.ns.update(show_available_records=lambda: None,
                       record_format_handle=lambda _: 'format',
                       resources_of_type=lambda _: ['resource'],
                       attached_record_names=lambda _: [],
                       modification_block=Mock(side_effect=status_sequence))

    def test_unknown_status_reports_skip_without_writing(self):
        self.configure_find_add(['unknown'])
        self.ns['run_find_add']()
        self.vs.SetRecord.assert_not_called()
        text = self.vs.AlrtDialog.call_args.args[0]
        self.assertIn('Unknown reference/lock status skipped: 1', text)
        self.assertNotIn('already good', text)

    def test_safety_rechecked_after_confirmation(self):
        self.configure_find_add([None, 'locked', 'locked'])
        self.ns['run_find_add']()
        self.vs.SetRecord.assert_not_called()
        text = self.vs.AlrtDialog.call_args.args[0]
        self.assertIn('Skipped: locked', text)
        self.assertNotIn('is now good', text)

    def test_local_unlocked_resource_receives_verified_record(self):
        safety_check = self.ns['modification_block']
        self.configure_find_add([])
        self.ns['modification_block'] = safety_check
        records = []
        self.ns['attached_record_names'] = lambda _: list(records)
        self.vs.SetRecord.side_effect = lambda h, name: records.append(name)
        self.ns['run_find_add']()
        self.vs.SetRecord.assert_called_once_with('resource', 'Record')
        self.assertEqual(records, ['Record'])
        self.assertEqual(self.vs.IsResourceReferenced.call_count, 2)
        self.assertEqual(self.vs.GetObjectVariableBoolean.call_count, 2)
        text = self.vs.AlrtDialog.call_args.args[0]
        self.assertIn('Records I tried to add: 1', text)
        self.assertIn('Successfully added: 1', text)
        self.assertIn('Could not add: 0', text)
        self.assertIn('Still missing after double-checking: 0', text)
        self.assertIn('Everything you asked me to check is now good.', text)


class FixtureMoveTests(unittest.TestCase):
    def setUp(self):
        self.parents = {'success': 'old', 'false': 'old', 'exception': 'old',
                        'unverified': 'old', 'already': 'new', 'none': 'old'}
        def set_parent(h, layer):
            if h == 'exception':
                raise RuntimeError('cannot move')
            if h == 'success':
                self.parents[h] = layer
                return True
            return {'false': False, 'unverified': True, 'none': None}[h]
        self.vs = SimpleNamespace(GetParent=Mock(side_effect=self.parents.get),
                                  SetParent=Mock(side_effect=set_parent))
        self.ns = load_functions('6 FIXTURE TYPE TO NEW LAYER v1.2.1.py', self.vs)

    def test_only_verified_success_counts(self):
        for handle, expected in [('success', 'moved'), ('false', 'failed'),
                                 ('exception', 'failed'), ('unverified', 'failed'),
                                 ('none', 'failed'), ('already', 'already')]:
            with self.subTest(handle=handle):
                self.assertEqual(self.ns['move_to_layer'](handle, 'new'), expected)
        self.assertNotIn(('already', 'new'), [c.args for c in self.vs.SetParent.call_args_list])

    def test_counts_per_type_and_continues_after_failure(self):
        counts = self.ns['move_groups']({
            'a': {'items': ['exception', 'success', 'already']},
            'b': {'items': ['false', 'unverified']}}, {'a': 'new', 'b': 'new'})
        self.assertEqual(counts, {'a': {'moved': 1, 'failed': 1, 'already': 1},
                                  'b': {'moved': 0, 'failed': 2, 'already': 0}})

    def test_unavailable_parent_check_does_not_claim_success(self):
        self.vs.GetParent.side_effect = RuntimeError('unavailable')
        self.assertEqual(self.ns['move_to_layer']('success', 'new'), 'failed')
        self.vs.SetParent.assert_not_called()

    def configure_main(self, groups):
        handles = [h for group in groups.values() for h in group['items']]
        types = {h: group['raw'] for group in groups.values() for h in group['items']}
        self.ns.update(seed_selected_lds=lambda: handles,
                       get_type=lambda h: types[h],
                       ensure_layer=Mock(return_value='new'))
        self.vs.YNDialog = Mock(return_value=True)
        self.vs.StrDialog = Mock(return_value='LD - Type: ')
        self.vs.GetLName = Mock(return_value='Destination')
        self.vs.AlrtDialog = Mock()
        self.vs.ReDrawAll = Mock()
        self.vs.UndoBegin = Mock()
        self.vs.UndoEnd = Mock()

    def test_main_reports_mixed_totals_and_per_type_counts(self):
        self.configure_main({
            'a': {'raw': 'Alpha', 'items': ['exception', 'success', 'already']},
            'b': {'raw': 'Beta', 'items': ['false', 'unverified']}})
        self.ns['main']()
        self.vs.AlrtDialog.assert_called_once()
        text = self.vs.AlrtDialog.call_args.args[0]
        self.assertIn('Moved 1 Lighting Devices.', text)
        self.assertIn('Failed or could not verify: 3', text)
        self.assertIn('Already on target layer: 1', text)
        self.assertIn('Alpha → Destination (1 moved, 1 failed/unverified, 1 already there)', text)
        self.assertIn('Beta → Destination (0 moved, 2 failed/unverified, 0 already there)', text)
        self.vs.UndoBegin.assert_called_once_with()
        self.vs.UndoEnd.assert_called_once_with()
        self.vs.ReDrawAll.assert_called_once_with()

    def test_main_reports_zero_success_when_set_parent_returns_false(self):
        self.configure_main({'b': {'raw': 'Beta', 'items': ['false']}})
        self.ns['main']()
        self.vs.SetParent.assert_called_once_with('false', 'new')
        text = self.vs.AlrtDialog.call_args.args[0]
        self.assertIn('Moved 0 Lighting Devices.', text)
        self.assertIn('Failed or could not verify: 1', text)
        self.assertIn('Already on target layer: 0', text)
        self.assertIn('Beta → Destination (0 moved, 1 failed/unverified, 0 already there)', text)


class BoundingBoxTests(unittest.TestCase):
    def test_documented_nested_points(self):
        vs = SimpleNamespace(GetBBox=Mock(return_value=((-1, 2.5), (3, 4))))
        ns = load_functions('2 MINDREADER v5.0.1.py', vs)
        self.assertEqual(ns['bbox_text']('h'), '(-1.0000, 2.5000) to (3.0000, 4.0000)')

    def test_unavailable_fallback(self):
        vs = SimpleNamespace(GetBBox=Mock())
        ns = load_functions('2 MINDREADER v5.0.1.py', vs)
        for result in [None, (), (1, 2, 3, 4), ((1,), (2, 3)), (('bad', 1), (2, 3))]:
            vs.GetBBox.return_value = result
            self.assertEqual(ns['bbox_text']('h'), '<unavailable>')
        vs.GetBBox.side_effect = RuntimeError('unsupported')
        self.assertEqual(ns['bbox_text']('h'), '<unavailable>')


if __name__ == '__main__':
    unittest.main()
