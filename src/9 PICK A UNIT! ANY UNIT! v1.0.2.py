# -*- coding: utf-8 -*-
# VWX FAILS - PICK A UNIT! ANY UNIT! v1.0.2
# Lighting Device Selector
# vibed by Chuckles
# Date: 2026-08-30
# Version: v1.0.2
#
# FIXES
# -----
# 1.0.2
# - Corrected the pull-down selection getter. GetChoiceIndex requires an
#   itemText argument; it does NOT return the currently selected index.
# - choice_text() now uses GetSelectedChoiceInfo, which is the proper VW API
#   for retrieving the currently selected pull-down item.
# - This also restores Existing Value population and field validation.
#
# 1.0.1
# - Vectorworks 2026 displayed CreatePullDownSearch controls but did not
#   reliably populate them with AddChoice in the tested environment.
# - Field and Existing Value controls use standard CreatePullDownMenu controls.
#
# UI can be a little stupid. Logic cannot.

import vs
import re


VERSION = "1.0.2"
TITLE = "PICK A UNIT! ANY UNIT! v{}".format(VERSION)
LD_PIO = "Lighting Device"
LD_REC = "Lighting Device"
SETUP_DIALOG = 12255

MODE_SINGLE = "Single Parameter Selection"
MODE_MULTI = "Multi-Parameter Selection"

ACTION_REPLACE = "Replace Selection"
ACTION_ADD = "Add to Selection"
ACTION_REMOVE = "Remove From Selection"

MATCH_ALL = "Match all parameters"
MATCH_ANY = "Match any parameter"

OP_EQUALS = "Equals"
OP_NOT_EQUALS = "Does Not Equal"
OP_CONTAINS = "Contains"
OP_STARTS = "Starts With"
OP_BLANK = "Is Blank"
OP_NOT_BLANK = "Is Not Blank"

OPERATORS = (
    OP_EQUALS,
    OP_NOT_EQUALS,
    OP_CONTAINS,
    OP_STARTS,
    OP_BLANK,
    OP_NOT_BLANK,
)

PSEUDO_CLASS = "@OBJECT_CLASS"
PSEUDO_LAYER = "@OBJECT_LAYER"
CLASS_LABEL = "Class (Object)"
LAYER_LABEL = "Layer (Object)"

MAX_CRITERIA = 4
MAX_VALUE_CHOICES = 2500

FIELD_PRIORITY = {
    "Purpose": 0,
    "System": 1,
    "Position": 2,
    "Universe": 3,
    "DMX Address": 4,
    "Address": 5,
    "Channel": 6,
    "Unit Number": 7,
    "Instrument Type": 8,
    "Inst Type": 9,
    "Fixture Type": 10,
    "Focus": 11,
    "Focus Point": 12,
    "Color": 13,
    "Fixture Mode": 14,
    "Device Type": 15,
    "Circuit Name": 16,
    "Circuit Number": 17,
}

ID_INTRO = 4
ID_MODE_LABEL = 5
ID_MODE = 6
ID_ACTION_LABEL = 7
ID_ACTION = 8
ID_MATCH_LABEL = 9
ID_MATCH = 10
ID_COLUMN_HEADER = 11
ID_NOTE = 12

ROW_BASE = 30
ROW_STRIDE = 10

ALL_LDS = []
FIELD_OPTIONS = []
FIELD_LABEL_TO_KEY = {}
FIELD_KEY_TO_LABEL = {}
VALUES_CACHE = {}
DIALOG = 0

STATE = {
    "mode": MODE_SINGLE,
    "action": ACTION_REPLACE,
    "match": MATCH_ALL,
    "criteria": [],
}


def valid(h):
    if h is None:
        return False
    try:
        return h != vs.Handle()
    except:
        return True


def is_ld(h):
    try:
        if vs.GetTypeN(h) != 86:
            return False
        pr = vs.GetParametricRecord(h)
        return valid(pr) and (vs.GetName(pr) or "") == LD_PIO
    except:
        return False


def all_lds():
    items = []
    seen = set()

    def collect(h):
        if is_ld(h):
            try:
                key = int(h)
            except:
                key = str(h)
            if key not in seen:
                seen.add(key)
                items.append(h)
        return False

    try:
        vs.ForEachObjectInLayer(collect, 0, 0, 1)
    except:
        pass

    return items


def field_names(h):
    try:
        pr = vs.GetParametricRecord(h)
        count = vs.NumFields(pr)
    except:
        return []

    out = []
    for i in range(1, count + 1):
        try:
            name = vs.GetFldName(pr, i)
        except:
            name = ""
        if name:
            out.append(name)
    return out


def field_sort_key(name):
    if name.startswith("User Field "):
        try:
            n = int(name.replace("User Field ", ""))
        except:
            n = 999
        return (1, n, name.casefold())

    if name in FIELD_PRIORITY:
        return (0, FIELD_PRIORITY[name], name.casefold())

    return (2, 0, name.casefold())


def build_field_options():
    if not ALL_LDS:
        return []

    fields = sorted(set(field_names(ALL_LDS[0])), key=field_sort_key)

    options = []
    for name in fields:
        options.append((name, "LD::" + name))

    options.append((CLASS_LABEL, PSEUDO_CLASS))
    options.append((LAYER_LABEL, PSEUDO_LAYER))
    return options


def get_value(h, field_key):
    if field_key == PSEUDO_CLASS:
        try:
            return str(vs.GetClass(h) or "").strip()
        except:
            return ""

    if field_key == PSEUDO_LAYER:
        try:
            layer = vs.GetLayer(h)
            if valid(layer):
                return str(vs.GetLName(layer) or "").strip()
        except:
            pass
        return ""

    if field_key.startswith("LD::"):
        name = field_key[4:]
        try:
            return str(vs.GetRField(h, LD_REC, name) or "").strip()
        except:
            return ""

    return ""


def natural_key(text):
    parts = re.split(r"(\d+)", str(text or ""))
    out = []
    for part in parts:
        if part.isdigit():
            out.append((0, int(part)))
        else:
            out.append((1, part.casefold()))
    return out


def values_for_field(field_key):
    if field_key in VALUES_CACHE:
        return VALUES_CACHE[field_key]

    seen = set()
    values = []

    for h in ALL_LDS:
        value = get_value(h, field_key)
        if not value:
            continue
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            values.append(value)

    values.sort(key=natural_key)

    if len(values) > MAX_VALUE_CHOICES:
        values = values[:MAX_VALUE_CHOICES]

    VALUES_CACHE[field_key] = values
    return values


def row_ids(row_index):
    base = ROW_BASE + (row_index * ROW_STRIDE)
    return {
        "use": base,
        "field": base + 1,
        "op": base + 2,
        "value": base + 3,
        "known": base + 4,
    }


def choice_text(item_id, fallback=""):
    # GetChoiceIndex(dialogID, componentID, itemText) looks up an item BY TEXT.
    # It does not report the currently selected item. For the current selection,
    # Vectorworks provides GetSelectedChoiceInfo(dialogID, componentID, startIndex).
    try:
        idx, text = vs.GetSelectedChoiceInfo(DIALOG, item_id, 0)
        if idx is None or int(idx) < 0:
            return fallback
        return text or fallback
    except:
        # Conservative fallback using the selected-index API plus GetChoiceText.
        try:
            idx = vs.GetSelectedChoiceIndex(DIALOG, item_id, 0)
            if idx is None or int(idx) < 0:
                return fallback
            text = vs.GetChoiceText(DIALOG, item_id, int(idx))
            return text or fallback
        except:
            return fallback


def clear_choices(item_id):
    try:
        count = int(vs.GetChoiceCount(DIALOG, item_id))
    except:
        count = 0

    for idx in range(count - 1, -1, -1):
        try:
            vs.RemoveChoice(DIALOG, item_id, idx)
        except:
            pass


def select_choice_by_text(item_id, wanted):
    if not wanted:
        return False

    try:
        count = int(vs.GetChoiceCount(DIALOG, item_id))
    except:
        count = 0

    target = wanted.casefold()
    for idx in range(count):
        try:
            text = vs.GetChoiceText(DIALOG, item_id, idx) or ""
        except:
            text = ""
        if text.casefold() == target:
            try:
                vs.SelectChoice(DIALOG, item_id, idx, True)
                return True
            except:
                return False
    return False


def preferred_field_label(candidates):
    available = {label.casefold(): label for label, _ in FIELD_OPTIONS}
    for candidate in candidates:
        found = available.get(candidate.casefold())
        if found:
            return found
    return FIELD_OPTIONS[0][0] if FIELD_OPTIONS else ""


def current_field_key(row_index):
    ids = row_ids(row_index)
    label = choice_text(ids["field"], "")
    return FIELD_LABEL_TO_KEY.get(label, "")


def populate_known_values(row_index, copy_first=False):
    ids = row_ids(row_index)
    field_key = current_field_key(row_index)
    previous = choice_text(ids["known"], "")

    clear_choices(ids["known"])
    values = values_for_field(field_key) if field_key else []

    if values:
        for i, value in enumerate(values):
            try:
                vs.AddChoice(DIALOG, ids["known"], value, i)
            except:
                pass

        selected = False
        if previous:
            selected = select_choice_by_text(ids["known"], previous)

        if not selected:
            try:
                vs.SelectChoice(DIALOG, ids["known"], 0, True)
            except:
                pass

        if copy_first:
            try:
                vs.SetItemText(DIALOG, ids["value"], values[0])
            except:
                pass

        try:
            vs.EnableItem(DIALOG, ids["known"], True)
        except:
            pass
    else:
        try:
            vs.AddChoice(DIALOG, ids["known"], "<no non-blank values>", 0)
            vs.SelectChoice(DIALOG, ids["known"], 0, True)
            vs.EnableItem(DIALOG, ids["known"], False)
        except:
            pass


def row_is_available(row_index, mode):
    return row_index == 0 or mode == MODE_MULTI


def refresh_row(row_index):
    ids = row_ids(row_index)
    mode = choice_text(ID_MODE, MODE_SINGLE)
    available = row_is_available(row_index, mode)

    if not available:
        try:
            vs.SetBooleanItem(DIALOG, ids["use"], False)
        except:
            pass

    if row_index == 0 and mode == MODE_SINGLE:
        try:
            vs.SetBooleanItem(DIALOG, ids["use"], True)
        except:
            pass

    try:
        use_row = bool(vs.GetBooleanItem(DIALOG, ids["use"]))
    except:
        use_row = row_index == 0

    active = available and use_row
    op = choice_text(ids["op"], OP_EQUALS)
    needs_value = op not in (OP_BLANK, OP_NOT_BLANK)

    try:
        vs.EnableItem(DIALOG, ids["use"], available and mode == MODE_MULTI)
        vs.EnableItem(DIALOG, ids["field"], active)
        vs.EnableItem(DIALOG, ids["op"], active)
        vs.EnableItem(DIALOG, ids["value"], active and needs_value)

        has_values = bool(values_for_field(current_field_key(row_index))) if active else False
        vs.EnableItem(DIALOG, ids["known"], active and needs_value and has_values)
    except:
        pass


def refresh_dialog():
    mode = choice_text(ID_MODE, MODE_SINGLE)

    try:
        vs.EnableItem(DIALOG, ID_MATCH_LABEL, mode == MODE_MULTI)
        vs.EnableItem(DIALOG, ID_MATCH, mode == MODE_MULTI)
    except:
        pass

    for row in range(MAX_CRITERIA):
        refresh_row(row)

    note = (
        "Single mode uses Parameter 1 only. Multi-Parameter mode can use up to four criteria. "
        "Existing Values are read from Lighting Devices currently in this drawing."
    )
    try:
        vs.SetItemText(DIALOG, ID_NOTE, note)
    except:
        pass


def set_default_field(row_index, candidates):
    ids = row_ids(row_index)
    label = preferred_field_label(candidates)
    if label:
        select_choice_by_text(ids["field"], label)


def dialog_handler(item, data):
    if item == SETUP_DIALOG:
        for i, text in enumerate((MODE_SINGLE, MODE_MULTI)):
            vs.AddChoice(DIALOG, ID_MODE, text, i)

        for i, text in enumerate((ACTION_REPLACE, ACTION_ADD, ACTION_REMOVE)):
            vs.AddChoice(DIALOG, ID_ACTION, text, i)

        for i, text in enumerate((MATCH_ALL, MATCH_ANY)):
            vs.AddChoice(DIALOG, ID_MATCH, text, i)

        try:
            vs.SelectChoice(DIALOG, ID_MODE, 0, True)
            vs.SelectChoice(DIALOG, ID_ACTION, 0, True)
            vs.SelectChoice(DIALOG, ID_MATCH, 0, True)
        except:
            pass

        for row in range(MAX_CRITERIA):
            ids = row_ids(row)

            for i, (label, _) in enumerate(FIELD_OPTIONS):
                try:
                    vs.AddChoice(DIALOG, ids["field"], label, i)
                except:
                    pass

            for i, text in enumerate(OPERATORS):
                vs.AddChoice(DIALOG, ids["op"], text, i)

            try:
                vs.SelectChoice(DIALOG, ids["field"], 0, True)
                vs.SelectChoice(DIALOG, ids["op"], 0, True)
                vs.SetBooleanItem(DIALOG, ids["use"], row == 0)
            except:
                pass

        set_default_field(0, ("Purpose", "Instrument Type", "Inst Type", "Fixture Type"))
        set_default_field(1, ("Universe", "Channel", "DMX Address", "Address"))
        set_default_field(2, ("Instrument Type", "Inst Type", "Fixture Type", "Position"))
        set_default_field(3, ("Position", "Focus", "Focus Point", "System"))

        for row in range(MAX_CRITERIA):
            populate_known_values(row, copy_first=True)

        refresh_dialog()
        return item

    if item == ID_MODE:
        refresh_dialog()
        return item

    for row in range(MAX_CRITERIA):
        ids = row_ids(row)

        if item == ids["field"]:
            populate_known_values(row, copy_first=True)
            refresh_row(row)
            return item

        if item == ids["known"]:
            selected = choice_text(ids["known"], "")
            if selected and not selected.startswith("<no non-blank"):
                try:
                    vs.SetItemText(DIALOG, ids["value"], selected)
                except:
                    pass
            return item

        if item in (ids["use"], ids["op"]):
            refresh_row(row)
            return item

    if item == 1:
        STATE["mode"] = choice_text(ID_MODE, MODE_SINGLE)
        STATE["action"] = choice_text(ID_ACTION, ACTION_REPLACE)
        STATE["match"] = choice_text(ID_MATCH, MATCH_ALL)
        STATE["criteria"] = []

        for row in range(MAX_CRITERIA):
            ids = row_ids(row)
            available = row_is_available(row, STATE["mode"])

            if row == 0 and STATE["mode"] == MODE_SINGLE:
                enabled = True
            else:
                try:
                    enabled = bool(vs.GetBooleanItem(DIALOG, ids["use"]))
                except:
                    enabled = False

            if not available or not enabled:
                continue

            field_label = choice_text(ids["field"], "")
            field_key = FIELD_LABEL_TO_KEY.get(field_label, "")
            op = choice_text(ids["op"], OP_EQUALS)

            try:
                value = str(vs.GetItemText(DIALOG, ids["value"]) or "").strip()
            except:
                value = ""

            STATE["criteria"].append({
                "field_label": field_label,
                "field_key": field_key,
                "operator": op,
                "value": value,
            })

    return item


def build_dialog():
    global DIALOG

    DIALOG = vs.CreateLayout(
        TITLE,
        False,
        "SELECT",
        "Cancel",
    )

    vs.CreateStaticText(
        DIALOG,
        ID_INTRO,
        "Lighting Device Selector - {} Lighting Device(s) found in this drawing.".format(len(ALL_LDS)),
        88,
    )

    vs.CreateStaticText(DIALOG, ID_MODE_LABEL, "Selection mode:", 18)
    vs.CreatePullDownMenu(DIALOG, ID_MODE, 34)

    vs.CreateStaticText(DIALOG, ID_ACTION_LABEL, "Selection action:", 18)
    vs.CreatePullDownMenu(DIALOG, ID_ACTION, 34)

    vs.CreateStaticText(DIALOG, ID_MATCH_LABEL, "Multi-Parameter logic:", 22)
    vs.CreatePullDownMenu(DIALOG, ID_MATCH, 34)

    vs.CreateStaticText(
        DIALOG,
        ID_COLUMN_HEADER,
        "USE     FIELD / PARAMETER                         MATCH                    VALUE                         EXISTING VALUE",
        108,
    )

    for row in range(MAX_CRITERIA):
        ids = row_ids(row)
        vs.CreateCheckBox(DIALOG, ids["use"], "{}".format(row + 1))

        # Standard pulldowns: CreatePullDownSearch displayed an empty
        # searchable popup in VWX 2026 even though AddChoice was called.
        vs.CreatePullDownMenu(DIALOG, ids["field"], 34)

        vs.CreatePullDownMenu(DIALOG, ids["op"], 20)
        vs.CreateEditText(DIALOG, ids["value"], "", 28)

        # Same reliability fix for discovered Existing Values.
        vs.CreatePullDownMenu(DIALOG, ids["known"], 32)

    vs.CreateStaticText(DIALOG, ID_NOTE, "", 108)

    vs.SetFirstLayoutItem(DIALOG, ID_INTRO)
    vs.SetBelowItem(DIALOG, ID_INTRO, ID_MODE_LABEL, 0, 10)
    vs.SetRightItem(DIALOG, ID_MODE_LABEL, ID_MODE, 0, 0)

    vs.SetBelowItem(DIALOG, ID_MODE_LABEL, ID_ACTION_LABEL, 0, 6)
    vs.SetRightItem(DIALOG, ID_ACTION_LABEL, ID_ACTION, 0, 0)

    vs.SetBelowItem(DIALOG, ID_ACTION_LABEL, ID_MATCH_LABEL, 0, 6)
    vs.SetRightItem(DIALOG, ID_MATCH_LABEL, ID_MATCH, 0, 0)

    vs.SetBelowItem(DIALOG, ID_MATCH_LABEL, ID_COLUMN_HEADER, 0, 12)

    previous_anchor = ID_COLUMN_HEADER
    for row in range(MAX_CRITERIA):
        ids = row_ids(row)
        vs.SetBelowItem(DIALOG, previous_anchor, ids["use"], 0, 5)
        vs.SetRightItem(DIALOG, ids["use"], ids["field"], 4, 0)
        vs.SetRightItem(DIALOG, ids["field"], ids["op"], 4, 0)
        vs.SetRightItem(DIALOG, ids["op"], ids["value"], 4, 0)
        vs.SetRightItem(DIALOG, ids["value"], ids["known"], 4, 0)
        previous_anchor = ids["use"]

    vs.SetBelowItem(DIALOG, previous_anchor, ID_NOTE, 0, 12)

    return DIALOG


def text_matches(actual, operator, wanted):
    actual = str(actual or "").strip()
    wanted = str(wanted or "").strip()

    if operator == OP_BLANK:
        return actual == ""

    if operator == OP_NOT_BLANK:
        return actual != ""

    a = actual.casefold()
    w = wanted.casefold()

    if operator == OP_EQUALS:
        return a == w

    if operator == OP_NOT_EQUALS:
        return a != w

    if operator == OP_CONTAINS:
        return w in a

    if operator == OP_STARTS:
        return a.startswith(w)

    return False


def validate_criteria(criteria):
    errors = []

    if not criteria:
        return ["No active selection parameters."]

    for i, criterion in enumerate(criteria, start=1):
        field_label = criterion.get("field_label", "")
        field_key = criterion.get("field_key", "")
        operator = criterion.get("operator", "")
        value = criterion.get("value", "")

        if not field_label or not field_key:
            errors.append("Parameter {} has no field selected.".format(i))

        if operator not in OPERATORS:
            errors.append("Parameter {} has an unknown match operation.".format(i))

        if operator not in (OP_BLANK, OP_NOT_BLANK) and value == "":
            errors.append(
                "Parameter {} ({}) needs a Value, or use Is Blank / Is Not Blank.".format(
                    i,
                    field_label or "field",
                )
            )

    return errors


def handle_matches(h, criteria, match_mode):
    results = []

    for criterion in criteria:
        actual = get_value(h, criterion["field_key"])
        results.append(
            text_matches(
                actual,
                criterion["operator"],
                criterion["value"],
            )
        )

    if not results:
        return False

    if match_mode == MATCH_ANY:
        return any(results)

    return all(results)


def find_matches(criteria, match_mode):
    return [
        h for h in ALL_LDS
        if handle_matches(h, criteria, match_mode)
    ]


def is_selected(h):
    try:
        return bool(vs.Selected(h))
    except:
        return False


def apply_selection(matches, action):
    matched = len(matches)
    changed = 0
    failed = 0

    if action == ACTION_REPLACE:
        try:
            vs.DSelectAll()
        except:
            pass

        for h in matches:
            try:
                vs.SetSelect(h)
                if is_selected(h):
                    changed += 1
                else:
                    failed += 1
            except:
                failed += 1

        return matched, changed, failed

    if action == ACTION_ADD:
        for h in matches:
            was_selected = is_selected(h)
            try:
                vs.SetSelect(h)
                now_selected = is_selected(h)
                if now_selected and not was_selected:
                    changed += 1
                elif not now_selected:
                    failed += 1
            except:
                failed += 1

        return matched, changed, failed

    if action == ACTION_REMOVE:
        for h in matches:
            was_selected = is_selected(h)
            try:
                vs.SetDSelect(h)
                now_selected = is_selected(h)
                if was_selected and not now_selected:
                    changed += 1
                elif now_selected:
                    failed += 1
            except:
                failed += 1

        return matched, changed, failed

    return matched, 0, matched


def criteria_summary(criteria, match_mode):
    parts = []
    for c in criteria:
        if c["operator"] in (OP_BLANK, OP_NOT_BLANK):
            parts.append("{} {}".format(c["field_label"], c["operator"]))
        else:
            parts.append(
                "{} {} '{}'".format(
                    c["field_label"],
                    c["operator"],
                    c["value"],
                )
            )

    joiner = " AND " if match_mode == MATCH_ALL else " OR "
    return joiner.join(parts)


def main():
    global ALL_LDS
    global FIELD_OPTIONS
    global FIELD_LABEL_TO_KEY
    global FIELD_KEY_TO_LABEL

    ALL_LDS = all_lds()

    if not ALL_LDS:
        vs.AlrtDialog(
            TITLE + "\n\n"
            "No Lighting Devices were found in this drawing."
        )
        return

    FIELD_OPTIONS = build_field_options()
    FIELD_LABEL_TO_KEY = {label: key for label, key in FIELD_OPTIONS}
    FIELD_KEY_TO_LABEL = {key: label for label, key in FIELD_OPTIONS}

    if not FIELD_OPTIONS:
        vs.AlrtDialog(
            TITLE + "\n\n"
            "Could not read Lighting Device parameters."
        )
        return

    result = vs.RunLayoutDialog(build_dialog(), dialog_handler)
    if result != 1:
        return

    criteria = STATE.get("criteria", [])
    errors = validate_criteria(criteria)

    if errors:
        vs.AlrtDialog(
            TITLE + "\n\n" + "\n".join("- " + e for e in errors)
        )
        return

    match_mode = STATE.get("match", MATCH_ALL)
    if STATE.get("mode") == MODE_SINGLE:
        match_mode = MATCH_ALL

    matches = find_matches(criteria, match_mode)

    if not matches:
        vs.AlrtDialog(
            TITLE + "\n\n"
            "No Lighting Devices matched:\n\n" +
            criteria_summary(criteria, match_mode)
        )
        return

    action = STATE.get("action", ACTION_REPLACE)
    matched, changed, failed = apply_selection(matches, action)

    try:
        vs.ReDrawAll()
    except:
        pass

    if action == ACTION_REPLACE:
        message = "PICK A UNIT: {} match(es); {} selected.".format(matched, changed)
    elif action == ACTION_ADD:
        message = "PICK A UNIT: {} match(es); {} added to selection.".format(matched, changed)
    else:
        message = "PICK A UNIT: {} match(es); {} removed from selection.".format(matched, changed)

    if failed:
        message += " {} could not be changed (check layer/class visibility and edit options).".format(failed)

    try:
        vs.Message(message)
    except:
        pass


main()
