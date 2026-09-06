# -*- coding: utf-8 -*-
# VWX FAILS - LIGHTING DEVICE ATTRIBUTES v1.5
# vibed by Chuckles
# Date: 2026-08-19
# Version: v1.5

import vs

LD_PIO = "Lighting Device"
LD_REC = "Lighting Device"

TYPE_CANDIDATES = (
    "Instrument Type",
    "Inst Type",
    "Fixture Type",
)

# VWX FAILS compact highlight recipe.
# Desired values as displayed by Vectorworks.
HIGHLIGHT_UNITS = 0
HIGHLIGHT_OFFSET = 0.035
HIGHLIGHT_BLUR = 0.03
HIGHLIGHT_ANGLE = 300.0
HIGHLIGHT_OPACITY = 85

# Confirmed Vectorworks Python shadow-distance compensation.
SHADOW_DISTANCE_COMPENSATION = 25.4

SETUP_DIALOG = 12255

ID_OPERATION_LABEL = 8
ID_OPERATION = 9
ID_SCOPE_LABEL = 10
ID_SCOPE = 11
ID_FIELD_LABEL = 12
ID_FIELD = 13
ID_MATCH_VALUES = 14
ID_SHADOW_HEADER = 15
ID_SHADOW_COLOR_LABEL = 16
ID_SHADOW_COLOR = 17
ID_LEGACY_HEADER = 20
ID_CHANGE_FILL = 21
ID_FILL_COLOR_LABEL = 22
ID_FILL_COLOR = 23
ID_SOLID_FILL = 24
ID_CHANGE_LW = 25
ID_LINE_WEIGHT_LABEL = 26
ID_LINE_WEIGHT = 27
ID_NOTE = 40

OP_HIGHLIGHT = "Highlight Shadow (preserves symbol colors)"
OP_REMOVE_HIGHLIGHT = "Remove Highlight Shadow"
OP_SET = "Legacy: Set Fill / Line Weight"
OP_BY_CLASS = "Make Attributes By Class"

SCOPE_SELECTED = "Selected Lighting Devices"
SCOPE_TYPE = "All matching Instrument Type(s)"
SCOPE_FIELD = "All matching selected field value(s)"

STATE = {
    "operation": OP_HIGHLIGHT,
    "scope": SCOPE_SELECTED,
    "field": "",
    "shadow_color_index": 0,
    "change_fill": False,
    "fill_color_index": 0,
    "solid_fill": False,
    "change_lw": False,
    "line_weight": 0,
}

FIELD_NAMES = []
SEED = []
DIALOG = 0


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

        return (
            valid(pr)
            and (vs.GetName(pr) or "") == LD_PIO
        )

    except:
        return False


def selected_lds():
    """
    Collect actual selected Lighting Devices across all drawing layers.
    """

    items = []
    seen = set()

    try:
        layer = vs.FLayer()
    except:
        layer = None

    while valid(layer):

        try:
            h = vs.FSObject(layer)
        except:
            h = None

        while valid(h):

            try:
                key = int(h)
            except:
                key = str(h)

            if key not in seen:
                seen.add(key)

                if is_ld(h):
                    items.append(h)

            try:
                h = vs.NextSObj(h)
            except:
                break

        try:
            layer = vs.NextLayer(layer)
        except:
            break

    return items


def all_lds():
    items = []

    def collect(h):
        if is_ld(h):
            items.append(h)

        return False

    try:
        vs.ForEachObjectInLayer(
            collect,
            0,
            0,
            1
        )
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
            name = vs.GetFldName(
                pr,
                i
            )
        except:
            name = ""

        if name:
            out.append(name)

    return out


def field_priority(name):
    if name.startswith("User Field "):

        try:
            n = int(
                name.replace(
                    "User Field ",
                    ""
                )
            )
        except:
            n = 99

        return (
            0,
            n,
            name.lower()
        )

    preferred = {
        "System": 0,
        "Purpose": 1,
        "Position": 2,
        "Inst Type": 3,
        "Instrument Type": 4,
        "Fixture Type": 5,
        "Unit Number": 6,
        "Channel": 7,
        "Circuit Name": 8,
        "Circuit Number": 9,
    }

    if name in preferred:
        return (
            1,
            preferred[name],
            name.lower()
        )

    return (
        2,
        0,
        name.lower()
    )


def get_field(h, field):
    if not field:
        return ""

    try:
        return str(
            vs.GetRField(
                h,
                LD_REC,
                field
            ) or ""
        ).strip()
    except:
        return ""


def first_type_field(h):
    available = set(
        field_names(h)
    )

    for name in TYPE_CANDIDATES:

        if name in available:
            return name

    return ""


def distinct_seed_values(
    handles,
    field
):
    values = []
    seen = set()

    for h in handles:

        value = get_field(
            h,
            field
        )

        if not value:
            continue

        key = value.casefold()

        if key not in seen:
            seen.add(key)
            values.append(value)

    return values


def matches_values(
    h,
    field,
    wanted
):
    value = get_field(
        h,
        field
    )

    if not value:
        return False

    wanted_keys = {
        item.casefold()
        for item in wanted
    }

    return (
        value.casefold()
        in wanted_keys
    )


def target_handles(
    scope,
    field
):
    if scope == SCOPE_SELECTED:

        return (
            list(SEED),
            "Selected Lighting Devices",
            []
        )

    universe = all_lds()

    if scope == SCOPE_TYPE:

        type_field = first_type_field(
            SEED[0]
        )

        if not type_field:

            return (
                [],
                "",
                [
                    "No Instrument Type / Inst Type / "
                    "Fixture Type field found."
                ]
            )

        wanted = distinct_seed_values(
            SEED,
            type_field
        )

        if not wanted:

            return (
                [],
                "",
                [
                    "Selected Lighting Devices have no "
                    "Instrument Type value."
                ]
            )

        matches = [
            h
            for h in universe
            if matches_values(
                h,
                type_field,
                wanted
            )
        ]

        return (
            matches,
            "{} = {}".format(
                type_field,
                ", ".join(wanted)
            ),
            []
        )

    if scope == SCOPE_FIELD:

        if not field:

            return (
                [],
                "",
                [
                    "Choose a Lighting Device "
                    "field to match."
                ]
            )

        wanted = distinct_seed_values(
            SEED,
            field
        )

        if not wanted:

            return (
                [],
                "",
                [
                    "Selected Lighting Devices have no "
                    "non-blank values in '{}'.".format(
                        field
                    )
                ]
            )

        matches = [
            h
            for h in universe
            if matches_values(
                h,
                field,
                wanted
            )
        ]

        return (
            matches,
            "{} = {}".format(
                field,
                ", ".join(wanted)
            ),
            []
        )

    return (
        [],
        "",
        ["Unknown scope."]
    )


def initial_fill_color_index(h):
    try:
        r, g, b = vs.GetFillFore(h)

        return vs.RGBToColorIndex(
            r,
            g,
            b
        )

    except:
        return 0


def initial_shadow_color_index():
    try:
        return vs.RGBToColorIndex(
            65535,
            0,
            65535
        )

    except:
        return 0


def initial_line_weight(h):
    try:
        return int(
            vs.GetLW(h)
        )

    except:
        return 0


def drop_shadows_visible():
    try:
        return bool(
            vs.GetPref(597)
        )

    except:
        return True


def choice_text(
    item_id,
    fallback=""
):
    try:
        _, text = vs.GetSelectedChoiceInfo(
            DIALOG,
            item_id,
            0
        )

        return (
            text
            or fallback
        )

    except:
        return fallback


def match_value_text(field):
    if not field:

        return (
            "Selected value(s): "
            "<choose a field>"
        )

    values = distinct_seed_values(
        SEED,
        field
    )

    if not values:

        return (
            "Selected value(s): "
            "<blank>"
        )

    shown = values[:8]

    text = ", ".join(
        shown
    )

    if len(values) > len(shown):
        text += ", ..."

    return (
        "Selected value(s): "
        + text
    )


def refresh_dialog():
    operation = choice_text(
        ID_OPERATION,
        OP_HIGHLIGHT
    )

    scope = choice_text(
        ID_SCOPE,
        SCOPE_SELECTED
    )

    field = choice_text(
        ID_FIELD,
        FIELD_NAMES[0]
        if FIELD_NAMES
        else ""
    )

    field_mode = (
        scope == SCOPE_FIELD
    )

    shadow_mode = (
        operation == OP_HIGHLIGHT
    )

    legacy_mode = (
        operation == OP_SET
    )

    try:
        vs.EnableItem(
            DIALOG,
            ID_FIELD,
            field_mode
        )

        vs.EnableItem(
            DIALOG,
            ID_MATCH_VALUES,
            field_mode
        )

        vs.EnableItem(
            DIALOG,
            ID_SHADOW_COLOR,
            shadow_mode
        )

        vs.EnableItem(
            DIALOG,
            ID_CHANGE_FILL,
            legacy_mode
        )

        vs.EnableItem(
            DIALOG,
            ID_CHANGE_LW,
            legacy_mode
        )

        fill_enabled = (
            legacy_mode
            and bool(
                vs.GetBooleanItem(
                    DIALOG,
                    ID_CHANGE_FILL
                )
            )
        )

        lw_enabled = (
            legacy_mode
            and bool(
                vs.GetBooleanItem(
                    DIALOG,
                    ID_CHANGE_LW
                )
            )
        )

        vs.EnableItem(
            DIALOG,
            ID_FILL_COLOR_LABEL,
            fill_enabled
        )

        vs.EnableItem(
            DIALOG,
            ID_FILL_COLOR,
            fill_enabled
        )

        vs.EnableItem(
            DIALOG,
            ID_SOLID_FILL,
            fill_enabled
        )

        vs.EnableItem(
            DIALOG,
            ID_LINE_WEIGHT_LABEL,
            lw_enabled
        )

        vs.EnableItem(
            DIALOG,
            ID_LINE_WEIGHT,
            lw_enabled
        )

    except:
        pass

    try:
        if field_mode:

            text = match_value_text(
                field
            )

        else:

            text = (
                "Match field is used only with "
                "'All matching selected field value(s)'."
            )

        vs.SetItemText(
            DIALOG,
            ID_MATCH_VALUES,
            text
        )

    except:
        pass

    if operation == OP_HIGHLIGHT:

        note = (
            "Highlight Shadow preserves native symbol colors. "
            "Every target gets the same compact VWX FAILS highlight."
        )

    elif operation == OP_REMOVE_HIGHLIGHT:

        note = (
            "Remove Highlight Shadow disables the native "
            "drop shadow on every target."
        )

    elif operation == OP_SET:

        note = (
            "Legacy mode edits object attributes. "
            "Fill color requires Spotlight > Modify lighting "
            "device color > Object attributes."
        )

    else:

        note = (
            "Make Attributes By Class restores fill, pen, "
            "line weight and line style."
        )

    try:
        vs.SetItemText(
            DIALOG,
            ID_NOTE,
            note
        )

    except:
        pass


def dialog_handler(
    item,
    data
):
    global STATE

    if item == SETUP_DIALOG:

        for i, text in enumerate(
            (
                OP_HIGHLIGHT,
                OP_REMOVE_HIGHLIGHT,
                OP_SET,
                OP_BY_CLASS,
            )
        ):

            vs.AddChoice(
                DIALOG,
                ID_OPERATION,
                text,
                i
            )

        for i, text in enumerate(
            (
                SCOPE_SELECTED,
                SCOPE_TYPE,
                SCOPE_FIELD,
            )
        ):

            vs.AddChoice(
                DIALOG,
                ID_SCOPE,
                text,
                i
            )

        for i, text in enumerate(
            FIELD_NAMES
        ):

            vs.AddChoice(
                DIALOG,
                ID_FIELD,
                text,
                i
            )

        vs.SetColorChoice(
            DIALOG,
            ID_SHADOW_COLOR,
            initial_shadow_color_index()
        )

        vs.SetBooleanItem(
            DIALOG,
            ID_CHANGE_FILL,
            False
        )

        vs.SetColorChoice(
            DIALOG,
            ID_FILL_COLOR,
            initial_fill_color_index(
                SEED[0]
            )
        )

        vs.SetBooleanItem(
            DIALOG,
            ID_SOLID_FILL,
            False
        )

        vs.SetBooleanItem(
            DIALOG,
            ID_CHANGE_LW,
            False
        )

        vs.SetLineWeightChoice(
            DIALOG,
            ID_LINE_WEIGHT,
            initial_line_weight(
                SEED[0]
            )
        )

        refresh_dialog()

    elif item in (
        ID_OPERATION,
        ID_SCOPE,
        ID_FIELD,
        ID_CHANGE_FILL,
        ID_CHANGE_LW,
    ):

        refresh_dialog()

    elif item == 1:

        STATE["operation"] = choice_text(
            ID_OPERATION,
            OP_HIGHLIGHT
        )

        STATE["scope"] = choice_text(
            ID_SCOPE,
            SCOPE_SELECTED
        )

        STATE["field"] = choice_text(
            ID_FIELD,
            ""
        )

        try:
            STATE["shadow_color_index"] = int(
                vs.GetColorChoice(
                    DIALOG,
                    ID_SHADOW_COLOR
                )
            )

        except:
            STATE["shadow_color_index"] = (
                initial_shadow_color_index()
            )

        try:
            STATE["change_fill"] = bool(
                vs.GetBooleanItem(
                    DIALOG,
                    ID_CHANGE_FILL
                )
            )

        except:
            STATE["change_fill"] = False

        try:
            STATE["fill_color_index"] = int(
                vs.GetColorChoice(
                    DIALOG,
                    ID_FILL_COLOR
                )
            )

        except:
            STATE["fill_color_index"] = (
                initial_fill_color_index(
                    SEED[0]
                )
            )

        try:
            STATE["solid_fill"] = bool(
                vs.GetBooleanItem(
                    DIALOG,
                    ID_SOLID_FILL
                )
            )

        except:
            STATE["solid_fill"] = False

        try:
            STATE["change_lw"] = bool(
                vs.GetBooleanItem(
                    DIALOG,
                    ID_CHANGE_LW
                )
            )

        except:
            STATE["change_lw"] = False

        try:
            STATE["line_weight"] = int(
                vs.GetLineWeightChoice(
                    DIALOG,
                    ID_LINE_WEIGHT
                )
            )

        except:
            STATE["line_weight"] = (
                initial_line_weight(
                    SEED[0]
                )
            )


def build_dialog():
    global DIALOG

    DIALOG = vs.CreateLayout(
        "VWX FAILS - Lighting Device Attributes v1.5",
        False,
        "Apply",
        "Cancel"
    )

    vs.CreateStaticText(
        DIALOG,
        ID_OPERATION_LABEL,
        "Operation:",
        18
    )

    vs.CreatePullDownMenu(
        DIALOG,
        ID_OPERATION,
        38
    )

    vs.CreateStaticText(
        DIALOG,
        ID_SCOPE_LABEL,
        "Apply to:",
        18
    )

    vs.CreatePullDownMenu(
        DIALOG,
        ID_SCOPE,
        38
    )

    vs.CreateStaticText(
        DIALOG,
        ID_FIELD_LABEL,
        "Match field:",
        18
    )

    vs.CreatePullDownMenu(
        DIALOG,
        ID_FIELD,
        38
    )

    vs.CreateStaticText(
        DIALOG,
        ID_MATCH_VALUES,
        "Selected value(s):",
        58
    )

    vs.CreateStaticText(
        DIALOG,
        ID_SHADOW_HEADER,
        "DROP SHADOW",
        18
    )

    vs.CreateStaticText(
        DIALOG,
        ID_SHADOW_COLOR_LABEL,
        "Drop Shadow Color:",
        22
    )

    vs.CreateColorPopup(
        DIALOG,
        ID_SHADOW_COLOR,
        -1
    )

    vs.CreateStaticText(
        DIALOG,
        ID_LEGACY_HEADER,
        "LEGACY OBJECT ATTRIBUTES",
        28
    )

    vs.CreateCheckBox(
        DIALOG,
        ID_CHANGE_FILL,
        "Change fill color"
    )

    vs.CreateStaticText(
        DIALOG,
        ID_FILL_COLOR_LABEL,
        "Fill Color:",
        18
    )

    vs.CreateColorPopup(
        DIALOG,
        ID_FILL_COLOR,
        -1
    )

    vs.CreateCheckBox(
        DIALOG,
        ID_SOLID_FILL,
        "Force solid fill"
    )

    vs.CreateCheckBox(
        DIALOG,
        ID_CHANGE_LW,
        "Change line weight"
    )

    vs.CreateStaticText(
        DIALOG,
        ID_LINE_WEIGHT_LABEL,
        "Line Weight:",
        18
    )

    vs.CreateLineWeightPopup(
        DIALOG,
        ID_LINE_WEIGHT
    )

    vs.CreateStaticText(
        DIALOG,
        ID_NOTE,
        "",
        62
    )

    vs.SetFirstLayoutItem(
        DIALOG,
        ID_OPERATION_LABEL
    )

    vs.SetRightItem(
        DIALOG,
        ID_OPERATION_LABEL,
        ID_OPERATION,
        0,
        0
    )

    vs.SetBelowItem(
        DIALOG,
        ID_OPERATION_LABEL,
        ID_SCOPE_LABEL,
        0,
        8
    )

    vs.SetRightItem(
        DIALOG,
        ID_SCOPE_LABEL,
        ID_SCOPE,
        0,
        0
    )

    vs.SetBelowItem(
        DIALOG,
        ID_SCOPE_LABEL,
        ID_FIELD_LABEL,
        0,
        8
    )

    vs.SetRightItem(
        DIALOG,
        ID_FIELD_LABEL,
        ID_FIELD,
        0,
        0
    )

    vs.SetBelowItem(
        DIALOG,
        ID_FIELD_LABEL,
        ID_MATCH_VALUES,
        18,
        4
    )

    vs.SetBelowItem(
        DIALOG,
        ID_MATCH_VALUES,
        ID_SHADOW_HEADER,
        -18,
        14
    )

    vs.SetBelowItem(
        DIALOG,
        ID_SHADOW_HEADER,
        ID_SHADOW_COLOR_LABEL,
        0,
        6
    )

    vs.SetRightItem(
        DIALOG,
        ID_SHADOW_COLOR_LABEL,
        ID_SHADOW_COLOR,
        0,
        0
    )

    vs.SetBelowItem(
        DIALOG,
        ID_SHADOW_COLOR_LABEL,
        ID_LEGACY_HEADER,
        0,
        16
    )

    vs.SetBelowItem(
        DIALOG,
        ID_LEGACY_HEADER,
        ID_CHANGE_FILL,
        0,
        6
    )

    vs.SetBelowItem(
        DIALOG,
        ID_CHANGE_FILL,
        ID_FILL_COLOR_LABEL,
        18,
        4
    )

    vs.SetRightItem(
        DIALOG,
        ID_FILL_COLOR_LABEL,
        ID_FILL_COLOR,
        0,
        0
    )

    vs.SetBelowItem(
        DIALOG,
        ID_FILL_COLOR_LABEL,
        ID_SOLID_FILL,
        0,
        4
    )

    vs.SetBelowItem(
        DIALOG,
        ID_SOLID_FILL,
        ID_CHANGE_LW,
        -18,
        10
    )

    vs.SetBelowItem(
        DIALOG,
        ID_CHANGE_LW,
        ID_LINE_WEIGHT_LABEL,
        18,
        4
    )

    vs.SetRightItem(
        DIALOG,
        ID_LINE_WEIGHT_LABEL,
        ID_LINE_WEIGHT,
        0,
        0
    )

    vs.SetBelowItem(
        DIALOG,
        ID_LINE_WEIGHT_LABEL,
        ID_NOTE,
        -18,
        14
    )

    return DIALOG


def apply_operation(handles):
    if not handles:

        return (
            0,
            [],
            0
        )

    operation = STATE["operation"]

    problems = []
    skipped = 0
    changed = 0

    shadow_rgb = None
    fill_rgb = None

    if operation == OP_HIGHLIGHT:

        if not drop_shadows_visible():

            return (
                0,
                [
                    "Document Preferences > Display > "
                    "Drop shadows is OFF. "
                    "Turn it on to display Highlight Shadow."
                ],
                0
            )

        try:
            shadow_rgb = vs.ColorIndexToRGB(
                STATE["shadow_color_index"]
            )

        except Exception as e:

            return (
                0,
                [
                    "Could not resolve Drop Shadow Color: "
                    "{}".format(e)
                ],
                0
            )

    elif (
        operation == OP_SET
        and STATE["change_fill"]
    ):

        try:
            fill_rgb = vs.ColorIndexToRGB(
                STATE["fill_color_index"]
            )

        except Exception as e:

            return (
                0,
                [
                    "Could not resolve Fill Color: "
                    "{}".format(e)
                ],
                0
            )

    setter_offset = (
        HIGHLIGHT_OFFSET
        / SHADOW_DISTANCE_COMPENSATION
    )

    setter_blur = (
        HIGHLIGHT_BLUR
        / SHADOW_DISTANCE_COMPENSATION
    )

    began = False

    try:
        if hasattr(
            vs,
            "UndoBegin"
        ):

            vs.UndoBegin()
            began = True

        if hasattr(
            vs,
            "NameUndoEvent"
        ):

            try:
                vs.NameUndoEvent(
                    "Lighting Device Attributes"
                )
            except:
                pass

        for h in handles:

            try:
                if operation == OP_HIGHLIGHT:

                    vs.ResetObject(
                        h
                    )

                    vs.EnableDropShadow(
                        h,
                        False
                    )

                    vs.SetDropShadowByCls(
                        h,
                        False
                    )

                    vs.SetDropShadowData(
                        h,
                        HIGHLIGHT_UNITS,
                        setter_offset,
                        setter_blur,
                        HIGHLIGHT_ANGLE,
                        HIGHLIGHT_OPACITY,
                        shadow_rgb
                    )

                    vs.EnableDropShadow(
                        h,
                        True
                    )

                    try:
                        enabled = bool(
                            vs.IsDropShadowEnabled(
                                h
                            )
                        )

                    except:
                        enabled = False

                    if not enabled:

                        problems.append(
                            "Vectorworks did not report "
                            "the highlight shadow as enabled "
                            "after applying it."
                        )

                        skipped += 1
                        continue

                elif (
                    operation
                    == OP_REMOVE_HIGHLIGHT
                ):

                    vs.EnableDropShadow(
                        h,
                        False
                    )

                    try:
                        still_enabled = bool(
                            vs.IsDropShadowEnabled(
                                h
                            )
                        )

                    except:
                        still_enabled = False

                    if still_enabled:

                        problems.append(
                            "Vectorworks still reports "
                            "a shadow enabled after removal."
                        )

                        skipped += 1
                        continue

                elif operation == OP_SET:

                    if (
                        STATE["change_fill"]
                        and fill_rgb
                    ):

                        vs.SetFillFore(
                            h,
                            fill_rgb
                        )

                        vs.SetFillBack(
                            h,
                            fill_rgb
                        )

                        if STATE["solid_fill"]:

                            vs.SetFPat(
                                h,
                                1
                            )

                    if STATE["change_lw"]:

                        vs.SetLW(
                            h,
                            STATE["line_weight"]
                        )

                    vs.ResetObject(
                        h
                    )

                elif operation == OP_BY_CLASS:

                    vs.SetFillColorByClass(
                        h
                    )

                    vs.SetFPatByClass(
                        h
                    )

                    vs.SetPenColorByClass(
                        h
                    )

                    vs.SetLWByClass(
                        h
                    )

                    vs.SetLSByClass(
                        h
                    )

                    vs.ResetObject(
                        h
                    )

                changed += 1

            except Exception as e:

                problems.append(
                    "Fixture update failed: "
                    "{}".format(e)
                )

        try:
            vs.ReDrawAll()
        except:
            pass

    finally:

        if (
            began
            and hasattr(
                vs,
                "UndoEnd"
            )
        ):

            vs.UndoEnd()

    return (
        changed,
        problems,
        skipped
    )


def main():
    global SEED
    global FIELD_NAMES

    SEED = selected_lds()

    if not SEED:

        vs.AlrtDialog(
            "Lighting Device Attributes v1.5\n\n"
            "Select one or more Lighting Devices first."
        )

        return

    FIELD_NAMES = sorted(
        field_names(
            SEED[0]
        ),
        key=field_priority
    )

    if not FIELD_NAMES:

        vs.AlrtDialog(
            "Lighting Device Attributes v1.5\n\n"
            "Could not read Lighting Device fields."
        )

        return

    if vs.RunLayoutDialog(
        build_dialog(),
        dialog_handler
    ) != 1:

        return

    if (
        STATE["operation"] == OP_SET
        and not STATE["change_fill"]
        and not STATE["change_lw"]
    ):

        vs.AlrtDialog(
            "Lighting Device Attributes v1.5\n\n"
            "Neither Fill nor Line Weight is enabled.\n"
            "Nothing changed."
        )

        return

    (
        targets,
        match_description,
        errors
    ) = target_handles(
        STATE["scope"],
        STATE["field"]
    )

    if errors:

        vs.AlrtDialog(
            "Lighting Device Attributes v1.5\n\n"
            + "\n".join(
                errors
            )
        )

        return

    if not targets:

        vs.AlrtDialog(
            "Lighting Device Attributes v1.5\n\n"
            "No matching Lighting Devices were found."
        )

        return

    operation = STATE["operation"]

    if operation == OP_HIGHLIGHT:

        try:
            color_rgb = vs.ColorIndexToRGB(
                STATE["shadow_color_index"]
            )
        except:
            color_rgb = "<unavailable>"

        detail = (
            "Applies the VWX FAILS compact highlight "
            "to every target.\n"
            "Native symbol colors are left alone.\n\n"
            "Offset: {offset} in\n"
            "Blur: {blur} in\n"
            "Angle: {angle} degrees\n"
            "Opacity: {opacity}%\n"
            "Drop Shadow RGB: {rgb}"
        ).format(
            offset=HIGHLIGHT_OFFSET,
            blur=HIGHLIGHT_BLUR,
            angle=HIGHLIGHT_ANGLE,
            opacity=HIGHLIGHT_OPACITY,
            rgb=color_rgb
        )

    elif operation == OP_REMOVE_HIGHLIGHT:

        detail = (
            "Disables the native drop shadow "
            "on every target fixture."
        )

    elif operation == OP_SET:

        detail = (
            "LEGACY OBJECT-ATTRIBUTE MODE\n"
            "Change fill: {fill}\n"
            "Force solid fill: {solid}\n"
            "Change line weight: {lw}\n"
            "Fill color requires Spotlight > Modify lighting "
            "device color > Object attributes to display."
        ).format(
            fill=(
                "YES"
                if STATE["change_fill"]
                else "NO"
            ),
            solid=(
                "YES"
                if (
                    STATE["change_fill"]
                    and STATE["solid_fill"]
                )
                else "NO"
            ),
            lw=(
                "YES"
                if STATE["change_lw"]
                else "NO"
            ),
        )

    else:

        detail = (
            "Fill color, fill pattern, pen color, "
            "line weight and line style "
            "will be set By Class."
        )

    preview = (
        "Lighting Device Attributes v1.5\n\n"
        "Seed selection: {seed} Lighting Device(s)\n"
        "Operation: {operation}\n"
        "Apply to: {scope}\n"
        "Match: {match}\n"
        "Targets: {targets}\n\n"
        "{detail}\n\n"
        "Apply?"
    ).format(
        seed=len(SEED),
        operation=operation,
        scope=STATE["scope"],
        match=(
            match_description
            or "<selected only>"
        ),
        targets=len(
            targets
        ),
        detail=detail,
    )

    if not vs.YNDialog(
        preview
    ):

        return

    (
        changed,
        problems,
        skipped
    ) = apply_operation(
        targets
    )

    message = (
        "Lighting Device Attributes v1.5\n\n"
        "Operation: {}\n"
        "Updated: {} Lighting Device(s)\n"
        "Skipped: {}\n"
        "Problems: {}"
    ).format(
        operation,
        changed,
        skipped,
        len(
            problems
        )
    )

    if problems:

        message += (
            "\n\n"
            + "\n".join(
                "- " + item
                for item in problems[:10]
            )
        )

    vs.AlrtDialog(
        message
    )


main()
