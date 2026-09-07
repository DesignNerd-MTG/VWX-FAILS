# -*- coding: utf-8 -*-
# VWX FAILS - HYPERLINK REBUILDER v2.0
# vibed by Chuckles
# Date: 2026-08-18
# Version: v2.0
#
#
# Rebuilds Sheet Layer hyperlinks inside a named TOC symbol definition.
# Preserves existing non-sheet hyperlinks (PDFs, webpages, etc.).
#
# VW26 evidence-based Hyperlink CW fields used for Sheet Layer links:
#   function
#   target
#   EditableLabel
#   EditableFunction
#   SheetLayer
#
# SAFE BOUNDARY
# - Works directly on ONE explicitly named Symbol Definition.
# - Does not depend on nested selection/edit-context state.
# - Only retargets hyperlinks whose function is "Activate Sheet Layer".
# - Existing non-sheet hyperlinks are never deleted or retargeted.
# - Existing non-sheet hyperlinks can optionally be reflowed after sheets.
# - Uses an existing Sheet Layer hyperlink as the visual/style template.
# - Audits and asks before changing anything.
#
# Future:
# Once a known-good VW26 "Open Document" PDF hyperlink has been inspected,
# file-link creation can be added without guessing.

import vs


DEFAULT_TOC_SYMBOL = "TOC BIG"

HYPERLINK_PONS = (
    "Hyperlink CW",
    "Hyperlink",
)

SHEET_FUNCTION = "Activate Sheet Layer"

MAX_PREVIEW = 20


def valid(h):
    if h is None:
        return False

    try:
        return h != vs.Handle()
    except:
        return True


def otype(h):
    try:
        return vs.GetTypeN(h)
    except:
        return -1


def oname(h):
    try:
        return vs.GetName(h) or ""
    except:
        return ""


def parametric_record(h):
    try:
        pr = vs.GetParametricRecord(h)

        if valid(pr):
            return pr
    except:
        pass

    return None


def pon_name(h):
    pr = parametric_record(h)

    if valid(pr):
        return oname(pr)

    return ""


def is_hyperlink(h):
    if otype(h) != 86:
        return False

    return pon_name(h) in HYPERLINK_PONS


def hyperlink_record_name(h):
    p = pon_name(h)

    if p in HYPERLINK_PONS:
        return p

    return ""


def get_field(h, field):
    rec = hyperlink_record_name(h)

    if not rec:
        return ""

    try:
        return vs.GetRField(
            h,
            rec,
            field
        ) or ""
    except:
        return ""


def set_field(h, field, value):
    rec = hyperlink_record_name(h)

    if not rec:
        return False

    try:
        vs.SetRField(
            h,
            rec,
            field,
            str(value)
        )
        return True
    except:
        return False


def hyperlink_function(h):
    return get_field(
        h,
        "function"
    )


def hyperlink_target(h):
    return (
        get_field(h, "target")
        or get_field(h, "SheetLayer")
        or get_field(h, "Url")
        or get_field(h, "DocumentName")
    )


def hyperlink_label(h):
    return get_field(
        h,
        "EditableLabel"
    )


def is_sheet_hyperlink(h):
    return (
        is_hyperlink(h)
        and hyperlink_function(h) == SHEET_FUNCTION
    )


def get_xy(h):
    try:
        return vs.HCenter(h)
    except:
        return (0.0, 0.0)


def move_center_to(h, x, y):
    cx, cy = get_xy(h)

    try:
        vs.HMove(
            h,
            x - cx,
            y - cy
        )
    except:
        pass


def duplicate_object(h):
    try:
        parent = vs.GetParent(h)
    except:
        parent = None

    try:
        dup = vs.CreateDuplicateObject(
            h,
            parent
        )
    except:
        dup = None

    if valid(dup):
        try:
            vs.ResetObject(dup)
        except:
            pass

    return dup


def delete_object(h):
    try:
        vs.DelObject(h)
        return True
    except:
        return False


def symbol_definition(name):
    try:
        h = vs.GetObject(name)
    except:
        return None

    if not valid(h):
        return None

    if otype(h) != 16:
        return None

    return h


def direct_hyperlinks_in_definition(defh):
    out = []

    try:
        h = vs.FInSymDef(defh)
    except:
        h = None

    while valid(h):
        if is_hyperlink(h):
            out.append(h)

        try:
            h = vs.NextObj(h)
        except:
            break

    return out


def sort_top_to_bottom(handles):
    return sorted(
        handles,
        key=lambda h: (
            -get_xy(h)[1],
            get_xy(h)[0]
        )
    )


def list_sheet_layers():
    out = []

    try:
        lyr = vs.FLayer()
    except:
        lyr = None

    while valid(lyr):
        try:
            layer_type = vs.GetObjectVariableInt(
                lyr,
                154
            )
        except:
            layer_type = -1

        if layer_type == 2:
            try:
                name = vs.GetLName(lyr)
            except:
                name = ""

            if name:
                out.append(name)

        try:
            lyr = vs.NextLayer(lyr)
        except:
            break

    return sorted(
        out,
        key=lambda s: s.lower()
    )


def parse_index_ranges(text, maxn):
    text = str(
        text or ""
    ).strip()

    if not text:
        return []

    found = set()

    for token in text.replace(
        " ",
        ""
    ).split(","):

        if not token:
            continue

        if "-" in token:
            a, b = token.split(
                "-",
                1
            )

            try:
                a = int(a)
                b = int(b)
            except:
                continue

            if a > b:
                a, b = b, a

            for n in range(
                a,
                b + 1
            ):
                if 1 <= n <= maxn:
                    found.add(n - 1)

        else:
            try:
                n = int(token)
            except:
                continue

            if 1 <= n <= maxn:
                found.add(n - 1)

    return sorted(found)


def choose_sheet_layers():
    sheets = list_sheet_layers()

    if not sheets:
        vs.AlrtDialog(
            "Hyperlink Rebuilder\n\n"
            "No Sheet Layers were found."
        )
        return None

    lines = [
        "HYPERLINK REBUILDER\n",
        "Choose Sheet Layers by number.",
        "Example: 1,3,5-8\n",
    ]

    for i, name in enumerate(
        sheets,
        1
    ):
        lines.append(
            "{}. {}".format(
                i,
                name
            )
        )

    choice = vs.StrDialog(
        "\n".join(lines),
        ""
    )

    try:
        if vs.DidCancel():
            return None
    except:
        pass

    indexes = parse_index_ranges(
        choice,
        len(sheets)
    )

    return [
        sheets[i]
        for i in indexes
    ]


def default_label_for_sheet(layer_name):
    # Vectorworks sheet layer names commonly look like:
    #   1 [PLOT OVERVIEW]
    # Turn that into:
    #   1 PLOT OVERVIEW
    #
    # Existing labels are preserved whenever an existing target still exists,
    # so custom labels such as "0 TABLE OF CONTENTS" survive automatically.

    text = str(
        layer_name or ""
    ).strip()

    text = text.replace(
        "[",
        ""
    ).replace(
        "]",
        ""
    )

    while "  " in text:
        text = text.replace(
            "  ",
            " "
        )

    return text.upper()


def existing_label_map(sheet_links):
    out = {}

    for h in sheet_links:
        target = hyperlink_target(h)
        label = hyperlink_label(h)

        if target and label:
            out[target] = label

    return out


def retarget_sheet_link(
    h,
    layer_name,
    label
):
    # These are the actual VW26 Hyperlink CW fields observed in the user's
    # working TOC hyperlinks.

    ok = True

    ok = (
        set_field(
            h,
            "function",
            SHEET_FUNCTION
        )
        and ok
    )

    ok = (
        set_field(
            h,
            "target",
            layer_name
        )
        and ok
    )

    ok = (
        set_field(
            h,
            "EditableFunction",
            SHEET_FUNCTION
        )
        and ok
    )

    ok = (
        set_field(
            h,
            "SheetLayer",
            layer_name
        )
        and ok
    )

    if label is not None:
        ok = (
            set_field(
                h,
                "EditableLabel",
                label
            )
            and ok
        )

    # The working links showed EditableTarget blank for Sheet Layer links.
    set_field(
        h,
        "EditableTarget",
        ""
    )

    try:
        vs.ResetObject(h)
    except:
        pass

    return ok


def infer_step(sheet_links, all_links):
    source = (
        sheet_links
        if len(sheet_links) >= 2
        else all_links
    )

    ordered = sort_top_to_bottom(
        source
    )

    if len(ordered) >= 2:
        x1, y1 = get_xy(
            ordered[0]
        )
        x2, y2 = get_xy(
            ordered[1]
        )

        return (
            x2 - x1,
            y2 - y1
        )

    # Safe fallback if only one hyperlink exists.
    return (
        0.0,
        -0.25
    )


def ask_step(default_step):
    dx, dy = default_step

    dx_text = vs.StrDialog(
        "HYPERLINK REBUILDER\n\n"
        "Horizontal spacing between links:",
        "{:.4f}".format(dx)
    )

    try:
        if vs.DidCancel():
            return None
    except:
        pass

    dy_text = vs.StrDialog(
        "HYPERLINK REBUILDER\n\n"
        "Vertical spacing between links.\n"
        "Negative = down:",
        "{:.4f}".format(dy)
    )

    try:
        if vs.DidCancel():
            return None
    except:
        pass

    try:
        return (
            float(dx_text),
            float(dy_text)
        )
    except:
        return default_step


def other_links_summary(links):
    lines = []

    for h in links[:MAX_PREVIEW]:
        lines.append(
            "- {} | {} | {}".format(
                hyperlink_function(h)
                or "<unknown function>",
                hyperlink_label(h)
                or "<no label>",
                hyperlink_target(h)
                or "<no target>"
            )
        )

    if len(links) > MAX_PREVIEW:
        lines.append(
            "...and {} more".format(
                len(links)
                - MAX_PREVIEW
            )
        )

    return "\n".join(lines)


def chosen_sheets_summary(sheets):
    return "\n".join(
        "- " + name
        for name in sheets
    )


def main():
    symbol_name = vs.StrDialog(
        "VWX FAILS - Hyperlink Rebuilder v2.0\n\n"
        "TOC Symbol Definition to rebuild:",
        DEFAULT_TOC_SYMBOL
    )

    try:
        if vs.DidCancel():
            return
    except:
        pass

    symbol_name = str(
        symbol_name or ""
    ).strip()

    if not symbol_name:
        return

    defh = symbol_definition(
        symbol_name
    )

    if not valid(defh):
        vs.AlrtDialog(
            "Hyperlink Rebuilder\n\n"
            "I could not find a Symbol Definition named:\n\n"
            "{}".format(
                symbol_name
            )
        )
        return

    all_links = direct_hyperlinks_in_definition(
        defh
    )

    if not all_links:
        vs.AlrtDialog(
            "Hyperlink Rebuilder\n\n"
            "No Hyperlink CW / Hyperlink objects were found "
            "directly inside:\n\n"
            "{}".format(
                symbol_name
            )
        )
        return

    sheet_links = [
        h
        for h in all_links
        if is_sheet_hyperlink(h)
    ]

    other_links = [
        h
        for h in all_links
        if not is_sheet_hyperlink(h)
    ]

    if not sheet_links:
        vs.AlrtDialog(
            "Hyperlink Rebuilder\n\n"
            "I found {} hyperlink(s), but none are existing "
            "'Activate Sheet Layer' links.\n\n"
            "This version needs one working Sheet Layer hyperlink "
            "to use as its visual/template object.".format(
                len(all_links)
            )
        )
        return

    chosen_sheets = choose_sheet_layers()

    if chosen_sheets is None:
        return

    if not chosen_sheets:
        vs.AlrtDialog(
            "Hyperlink Rebuilder\n\n"
            "No Sheet Layers were selected.\n"
            "Nothing changed."
        )
        return

    reflow_other = False

    if other_links:
        reflow_other = vs.YNDialog(
            "HYPERLINK REBUILDER\n\n"
            "I found {} non-sheet hyperlink(s).\n\n"
            "{}\n\n"
            "These will NOT be retargeted or deleted.\n\n"
            "Place them immediately after the rebuilt Sheet Layer links?\n\n"
            "YES = reflow them after the sheets\n"
            "NO = leave them exactly where they are".format(
                len(other_links),
                other_links_summary(
                    other_links
                )
            )
        )

    default_step = infer_step(
        sheet_links,
        all_links
    )

    step = ask_step(
        default_step
    )

    if step is None:
        return

    sheet_links_sorted = sort_top_to_bottom(
        sheet_links
    )

    template = sheet_links_sorted[0]
    start_xy = get_xy(
        template
    )

    old_labels = existing_label_map(
        sheet_links
    )

    preview = (
        "VWX FAILS - HYPERLINK REBUILDER v2.0\n\n"
        "Symbol: {symbol}\n"
        "Existing Sheet Layer links: {sheet_count}\n"
        "Existing non-sheet links preserved: {other_count}\n"
        "New Sheet Layer links: {new_count}\n"
        "Spacing: dx={dx:.4f}, dy={dy:.4f}\n\n"
        "SHEETS TO BUILD\n"
        "{sheets}\n\n"
        "Existing labels are preserved when the target still matches.\n"
        "New targets get a label based on the Sheet Layer name.\n\n"
        "Proceed?"
    ).format(
        symbol=symbol_name,
        sheet_count=len(sheet_links),
        other_count=len(other_links),
        new_count=len(chosen_sheets),
        dx=step[0],
        dy=step[1],
        sheets=chosen_sheets_summary(
            chosen_sheets
        )
    )

    if not vs.YNDialog(
        preview
    ):
        return

    began = False
    created = 0
    deleted = 0
    updated = 0
    failed = []

    try:
        if hasattr(vs, "UndoBegin"):
            vs.UndoBegin()
            began = True

        working = list(
            sheet_links_sorted
        )

        # Add sheet hyperlinks as needed by duplicating the proven sheet link.
        while len(working) < len(chosen_sheets):
            dup = duplicate_object(
                template
            )

            if not valid(dup):
                failed.append(
                    "Could not duplicate the Sheet Layer hyperlink template."
                )
                break

            working.append(
                dup
            )
            created += 1

        # Remove excess SHEET hyperlinks only.
        # Non-sheet / PDF links are deliberately untouched.
        if len(working) > len(chosen_sheets):
            extras = working[
                len(chosen_sheets):
            ]

            for h in extras:
                if delete_object(h):
                    deleted += 1

            working = working[
                :len(chosen_sheets)
            ]

        if len(working) != len(chosen_sheets):
            failed.append(
                "Could not make the Sheet Layer hyperlink count match."
            )
        else:
            dx, dy = step
            x0, y0 = start_xy

            for i, (
                h,
                layer_name
            ) in enumerate(
                zip(
                    working,
                    chosen_sheets
                )
            ):
                label = old_labels.get(
                    layer_name,
                    default_label_for_sheet(
                        layer_name
                    )
                )

                if retarget_sheet_link(
                    h,
                    layer_name,
                    label
                ):
                    updated += 1
                else:
                    failed.append(
                        "Could not fully retarget: {}".format(
                            layer_name
                        )
                    )

                move_center_to(
                    h,
                    x0 + i * dx,
                    y0 + i * dy
                )

            # Reflow preserved PDF/web/other links only if requested.
            if (
                reflow_other
                and other_links
            ):
                ordered_other = sort_top_to_bottom(
                    other_links
                )

                offset = len(
                    chosen_sheets
                )

                for j, h in enumerate(
                    ordered_other
                ):
                    move_center_to(
                        h,
                        x0 + (
                            offset + j
                        ) * dx,
                        y0 + (
                            offset + j
                        ) * dy
                    )

        try:
            vs.ReDrawAll()
        except:
            pass

    finally:
        if (
            began
            and hasattr(vs, "UndoEnd")
        ):
            vs.UndoEnd()

    message = (
        "VWX FAILS - Hyperlink Rebuilder v2.0\n\n"
        "DONE\n\n"
        "Sheet links updated: {updated}\n"
        "Sheet links created: {created}\n"
        "Excess sheet links deleted: {deleted}\n"
        "Non-sheet links preserved: {other}\n"
        "Problems: {problems}"
    ).format(
        updated=updated,
        created=created,
        deleted=deleted,
        other=len(other_links),
        problems=len(failed)
    )

    if failed:
        message += (
            "\n\nPROBLEMS\n" +
            "\n".join(
                "- " + item
                for item in failed[:MAX_PREVIEW]
            )
        )

    if other_links:
        message += (
            "\n\nPDF/web/other hyperlinks were not retargeted."
        )

    vs.AlrtDialog(
        message
    )


main()
