# F.I.N.G. v1.0 -- File Inventory Normalization Governor
# Standalone Vectorworks Python palette script; targets 2026 Update 6.
# Uses the XML Use-flag mechanism tested with Mike's North/South inventories.
# This is a manual inventory switch, not automatic document-switch monitoring.
# Run after changing files and before issuing inventory-dependent paperwork.
# Backups: Vectorworks user folder / _FING / backups.
# UNASSOCIATED is disabled pending verification of native source records.
import os
import re
import json
import hashlib
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import vs

FLAG = re.compile(rb'(<IsUsedThisInventory>\s*<Use>)(True|False)(</Use>\s*</IsUsedThisInventory>)')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def flag_value(data):
    root = ET.fromstring(data)
    nodes = root.findall('./IsUsedThisInventory/Use')
    matches = list(FLAG.finditer(data))
    if root.tag != 'Inventory' or len(nodes) != 1 or len(matches) != 1:
        raise ValueError('Unsupported or ambiguous inventory flag structure.')
    if nodes[0].text not in ('True', 'False'):
        raise ValueError('Unsupported inventory flag value.')
    return nodes[0].text


def flag_bytes(data, value):
    flag_value(data)
    return FLAG.sub(lambda m: m[1] + value.encode('ascii') + m[3], data, count=1)


def atomic_write(path, data):
    fd, name = tempfile.mkstemp(prefix='fing_', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, str(path))
    finally:
        if os.path.exists(name):
            os.unlink(name)


def apply_batch(changes):
    # Validate all originals before the first write. Check again at each write.
    for path, before, after in changes:
        if path.read_bytes() != before:
            raise RuntimeError('File changed since inspection: ' + path.name)
    written = []
    try:
        for path, before, after in changes:
            if path.read_bytes() != before:
                raise RuntimeError('Concurrent change: ' + path.name)
            atomic_write(path, after)
            written.append((path, before, after))
        for path, before, after in written:
            if path.read_bytes() != after:
                raise RuntimeError('Read-back mismatch: ' + path.name)
    except Exception as error:
        issues = []
        for path, before, after in reversed(written):
            try:
                current = path.read_bytes()
                if current == after:
                    atomic_write(path, before)
                elif current != before:
                    issues.append(path.name + ': concurrent edit; not overwritten')
            except Exception as undo_error:
                issues.append(path.name + ': ' + str(undo_error))
        raise RuntimeError(str(error) + '\nRollback issues: ' + ('; '.join(issues) or 'none'))


REC = '__FING_DOCUMENT_BINDING'
FIELD = 'InventoryName'


def binding():
    h = vs.GetObject(REC)
    if not h:
        return ''
    if vs.GetTypeN(h) != 47:
        raise RuntimeError('The document contains a different resource named ' + REC)
    names = [vs.GetFldName(h, i) for i in range(1, vs.NumFields(h) + 1)]
    if FIELD not in names:
        raise RuntimeError('The FING binding record is missing its InventoryName field.')
    return vs.GetRField(h, REC, FIELD)


def store_binding(name):
    old = binding()
    h = vs.GetObject(REC)
    if not h:
        vs.NewField(REC, FIELD, '', 4, 0)
        h = vs.GetObject(REC)
        if not h or vs.GetTypeN(h) != 47:
            raise RuntimeError('Cannot create the document binding record.')
        vs.SetObjectVariableBoolean(h, 900, False)
    try:
        vs.SetRField(h, REC, FIELD, name)
        if binding() != name:
            raise RuntimeError('Document binding read-back failed.')
    except Exception:
        vs.SetRField(h, REC, FIELD, old)
        raise


def discover(folder):
    rows = []
    def walk_error(error):
        raise error
    for base, dirs, files in os.walk(str(folder), onerror=walk_error):
        dirs.sort()
        for name in sorted(files):
            if not name.lower().endswith('.xml'):
                continue
            p = Path(base) / name
            p.resolve().relative_to(folder.resolve())
            data = p.read_bytes()
            try:
                state = flag_value(data)
            except Exception as error:
                raise RuntimeError('Cannot safely read inventory ' + name + ': ' + str(error))
            relative = p.relative_to(folder).as_posix()
            rows.append({'path':p, 'data':data, 'state':state,
                         'id':relative, 'name':relative[:-4]})
    if not rows:
        raise RuntimeError('No inventory XML files found in ' + str(folder))
    return sorted(rows, key=lambda r:r['name'].casefold())


def find_bound(rows, saved):
    # Exact relative identity; accepts the earlier probe's name-without-extension.
    matches = [r for r in rows if saved in (r['id'], r['name'])]
    return matches[0] if saved and len(matches) == 1 else None


def choose(rows, saved):
    bound = find_bound(rows, saved)
    active = [r['name'] for r in rows if r['state'] == 'True']
    d = vs.CreateLayout('F.I.N.G. 1.0', True, 'THIS IS MY INVENTORY', 'CANCEL')
    vs.CreateStaticText(d, 10, 'File Inventory Normalization Governor', 58)
    vs.CreateStaticText(d, 11, 'This file: ' + (bound['name'] if bound else (saved + ' (missing)' if saved else 'No inventory bound')), 58)
    vs.CreateStaticText(d, 12, 'Enabled in inventory files: ' + (', '.join(active) if active else 'None'), 58)
    vs.CreateStaticText(d, 13, 'Choose inventory:', 58)
    vs.CreatePullDownMenu(d, 14, 52)
    vs.CreateCheckBox(d, 15, 'Remember this inventory for this file')
    vs.CreatePushButton(d, 16, 'REBIND')
    vs.CreateStaticText(d, 17, 'Restore the bound inventory and update this file\'s keys.', 58)
    vs.CreatePushButton(d, 18, 'UNASSOCIATED')
    vs.CreateStaticText(d, 19, 'Source-assignment selection is not available in this version.', 58)
    vs.CreateStaticText(d, 20, 'Inventory activation is global. Run FING after switching files.\nSave the drawing after setting its binding.', 58)
    vs.SetFirstLayoutItem(d, 10)
    for a,b in zip(range(10,20),range(11,21)):
        vs.SetBelowItem(d,a,b,0,4)
    for item, help_text in [(1,'Apply the chosen inventory and update all Summary Keys in this file. Remember it when the checkbox is selected.'),
                            (16,'Apply the saved document binding, regardless of the picker selection.'),
                            (2,'Close without making changes.'),
                            (18,'Requires verified native equipment source data; currently disabled.')]:
        vs.SetHelpText(d,item,help_text)
    result = {}
    def handler(item, data):
        if item == 12255 or item == 2255:
            for i,r in enumerate(rows):
                vs.AddChoice(d,14,r['name'],i)
            default = rows.index(bound) if bound else next((i for i,r in enumerate(rows) if r['state']=='True'),0)
            vs.SelectChoice(d,14,default,True)
            vs.SetBooleanItem(d,15,True)
            vs.EnableItem(d,16,bound is not None)
            vs.EnableItem(d,18,False)
        elif item == 16:
            if bound:
                result.update(target=bound['id'], remember=False)
                return 1
        elif item == 1:
            i,label = vs.GetSelectedChoiceInfo(d,14,0)
            if not (0 <= i < len(rows)):
                vs.AlrtDialog('Choose an inventory first.')
                return -1
            result.update(target=rows[i]['id'], remember=bool(vs.GetBooleanItem(d,15)))
        return item
    code = vs.RunLayoutDialog(d,handler)
    return result if code == 1 and result else None


def collect_keys():
    keys=[]
    def collect(h):
        if vs.GetTypeN(h)==86:
            r=vs.GetParametricRecord(h)
            if r and vs.GetName(r)=='Summary Key':
                keys.append(h)
    # All drawing layers, including keys inside groups and viewport annotations.
    # Symbol definitions excluded: do not change resource definitions.
    vs.ForEachObject(collect, "((INOBJECT & INVIEWPORT & (PON='Summary Key')))")
    return keys


def run():
    raw = vs.GetFolderPath(-330)
    user = vs.GetFolderPath(12)
    if not raw or not user:
        raise RuntimeError('Vectorworks did not return the inventory/user folder.')
    folder = Path(raw)
    if not folder.is_dir():
        raise RuntimeError('Inventory folder is unavailable: ' + raw)
    pending = Path(user)/'_FING_PROBE'/'06_pending_restore.json'
    if pending.exists():
        raise RuntimeError('An unfinished probe 06 is still recorded. Run 06 and RESTORE once before using FING.')
    rows = discover(folder)
    saved = binding()
    choice = choose(rows,saved)
    if not choice:
        return
    # Re-read after the user closes the dialog; no stale whole-file overwrites.
    rows = discover(folder)
    target = next((r for r in rows if r['id']==choice['target']),None)
    if target is None:
        raise RuntimeError('Chosen inventory is no longer available.')
    keys=collect_keys()
    changes=[]
    for r in rows:
        after=flag_bytes(r['data'],'True' if r['id']==target['id'] else 'False')
        if after!=r['data']:
            changes.append((r['path'],r['data'],after))
    out=Path(user)/'_FING'
    out.mkdir(exist_ok=True)
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    backup=None
    if changes:
        backup=out/'backups'/stamp
        backup.mkdir(parents=True)
        entries=[]
        for p,before,after in changes:
            dest=backup/p.relative_to(folder)
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(before)
            if dest.read_bytes()!=before:
                raise RuntimeError('Backup verification failed: '+p.name)
            entries.append({'inventory':p.relative_to(folder).as_posix(),'before':flag_value(before),'after':flag_value(after)})
        (backup/'manifest.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
    apply_batch(changes)
    try:
        if choice['remember']:
            store_binding(target['id'])
    except Exception as error:
        try:
            apply_batch([(p,after,before) for p,before,after in changes])
        except Exception as undo_error:
            raise RuntimeError('Binding failed: '+str(error)+'\nFlag rollback failed: '+str(undo_error)+'\nBackups: '+str(backup))
        raise RuntimeError('Binding failed; inventory flag changes rolled back. '+str(error))
    failures=[]
    for h in keys:
        try:
            vs.ResetObject(h)
        except Exception as error:
            failures.append(str(error))
    vs.ReDrawAll()
    # Disk verification is deliberately not presented as an in-memory API check.
    verified=discover(folder)
    enabled=[r['id'] for r in verified if r['state']=='True']
    flags_ok=enabled==[target['id']]
    lines=['F.I.N.G. 1.0', 'Inventory: '+target['name'],
           'Document binding: '+binding(),
           'Inventory flags verified: '+str(flags_ok),
           'Changed XML files: '+str(len(changes)),
           'Summary Keys reset without API errors: '+str(len(keys)-len(failures)),
           'Reset errors: '+repr(failures), 'Backup: '+str(backup or 'No XML changes needed'),
           'Native live selection/visual totals are not independently verified by this report.']
    (out/'FING_last_run.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    if not flags_ok or failures:
        vs.AlrtDialog('FING completed with issues.\n\n'+'\n'.join(lines))
    else:
        message=target['name']+' | '+str(len(keys))+' Summary Key(s) requested for refresh.'
        if not keys:
            message+=' No Summary Keys found in this file.'
        if choice['remember']:
            message+=' Save this drawing to keep its binding.'
        vs.Message(message)


try:
    run()
except Exception as error:
    vs.AlrtDialog('FING stopped:\n\n'+str(error))
