# -*- coding: utf-8 -*-
# VWX FAILS - MINDREADER v5.0
# vibed by Chuckles
# Date: 2026-08-18
# Version: v5.0
#
# Universal read-only Vectorworks object inspector.
#
# Goal:
#   Select ONE object. MINDREADER reports what Vectorworks actually exposes.
#
# Generic inspection:
#   - object type / name / class
#   - parent chain
#   - symbol identity / definition
#   - parametric record when present
#   - every attached record, field type, and current value
#   - child/generated contents when exposed
#   - embedded symbol definitions
#
# Specialized inspection:
#   - Lighting Device / Parts / EntEquip / Light Info clues when present
#
# READ ONLY.

import vs
import os
import tempfile

REC_TYPE = 47
SYMDEF_TYPE = 16
PIO_TYPE = 86

LD_REC = "Lighting Device"
PARTS_REC = "Parts"
LIGHT_REC = "Light Info Record"
ENT_REC = "EntEquipUniversal"

MAX_OBJECTS = 5000
MAX_DEPTH = 8
MAX_PARENT_DEPTH = 12


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


def oclass(h):
    try:
        return vs.GetClass(h) or ""
    except:
        return ""


def symname(h):
    try:
        return vs.GetSymName(h) or ""
    except:
        return ""


def parent(h):
    try:
        p = vs.GetParent(h)
        return p if valid(p) else None
    except:
        return None


def clean(v):
    if v is None:
        return ""
    return str(v).replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")


def recnames(h):
    out = []
    try:
        n = vs.NumRecords(h)
    except:
        return out

    for i in range(1, n + 1):
        try:
            rh = vs.GetRecord(h, i)
            if valid(rh):
                nm = vs.GetName(rh)
                if nm and nm not in out:
                    out.append(nm)
        except:
            pass
    return out


def hasrec(h, rec):
    return rec in recnames(h)


def rfield(h, rec, fld):
    try:
        return clean(vs.GetRField(h, rec, fld))
    except:
        return ""


def recdef(rec):
    try:
        h = vs.GetObject(rec)
        if valid(h) and otype(h) == REC_TYPE:
            return h
    except:
        pass
    return None


def parametric_record(h):
    try:
        pr = vs.GetParametricRecord(h)
        return pr if valid(pr) else None
    except:
        return None


def bbox_text(h):
    try:
        x1, y1, x2, y2 = vs.GetBBox(h)
        return "({:.4f}, {:.4f}) to ({:.4f}, {:.4f})".format(
            x1, y1, x2, y2
        )
    except:
        return "<unavailable>"


def center_text(h):
    try:
        x, y = vs.HCenter(h)
        return "({:.4f}, {:.4f})".format(x, y)
    except:
        return "<unavailable>"


def ident(h):
    parts = ["type {}".format(otype(h))]

    n = oname(h)
    if n:
        parts.append("name={!r}".format(n))

    s = symname(h)
    if s:
        parts.append("symbol={!r}".format(s))

    c = oclass(h)
    if c:
        parts.append("class={!r}".format(c))

    return ", ".join(parts)


def dump_record_by_name(h, rec, ind=""):
    out = [ind + "RECORD: " + rec]
    rd = recdef(rec)

    if not valid(rd):
        out.append(ind + "  [record format unavailable]")
        return out

    try:
        count = vs.NumFields(rd)
    except:
        count = 0

    for i in range(1, count + 1):
        try:
            fn = vs.GetFldName(rd, i)
        except:
            fn = "<?>"

        try:
            ft = vs.GetFldType(rd, i)
        except:
            ft = "?"

        try:
            val = clean(vs.GetRField(h, rec, fn))
        except:
            val = "<error>"

        out.append(
            ind + "  {:03d}. {} [type {}] = {!r}".format(
                i, fn, ft, val
            )
        )

    return out


def dump_records(h, ind=""):
    out = []
    names = recnames(h)

    if not names:
        return [ind + "(no attached records)"]

    for rec in names:
        out.extend(dump_record_by_name(h, rec, ind))
        out.append("")

    return out


def dump_parametric_record(h, ind=""):
    pr = parametric_record(h)

    if not valid(pr):
        return [ind + "Parametric record: <none>"]

    try:
        rname = vs.GetName(pr) or "<unnamed>"
    except:
        rname = "<unnamed>"

    out = [
        ind + "Parametric record: " + rname
    ]

    try:
        count = vs.NumFields(pr)
    except:
        count = 0

    for i in range(1, count + 1):
        try:
            fn = vs.GetFldName(pr, i)
        except:
            fn = "<?>"

        try:
            ft = vs.GetFldType(pr, i)
        except:
            ft = "?"

        try:
            val = clean(vs.GetRField(h, rname, fn))
        except:
            val = "<error>"

        out.append(
            ind + "  {:03d}. {} [type {}] = {!r}".format(
                i, fn, ft, val
            )
        )

    return out


def parts_text(h):
    if not hasrec(h, PARTS_REC):
        return ""

    fields = [
        "Base", "Yoke", "Body",
        "Lens", "Point", "Light Emitter"
    ]

    return ", ".join(
        "{}={}".format(f, rfield(h, PARTS_REC, f))
        for f in fields
    )


def symdef(name):
    if not name:
        return None
    try:
        h = vs.GetObject(name)
        if valid(h) and otype(h) == SYMDEF_TYPE:
            return h
    except:
        pass
    return None


def parent_chain(h):
    out = []
    p = parent(h)
    depth = 0

    while valid(p) and depth < MAX_PARENT_DEPTH:
        depth += 1
        out.append(
            "  {}. {}".format(depth, ident(p))
        )
        p = parent(p)

    if not out:
        out.append("  <none>")

    if valid(p):
        out.append("  ...parent depth limit reached")

    return out


def first_child(h):
    try:
        ch = vs.FInGroup(h)
        return ch if valid(ch) else None
    except:
        return None


def scan_children(container):
    result = {
        "ok": False,
        "error": "",
        "items": [],
        "defs": {}
    }

    first = first_child(container)

    if not valid(first):
        result["error"] = "No child/generated objects exposed by FInGroup"
        return result

    result["ok"] = True
    seq = [0]

    def inspect(h):
        seq[0] += 1
        if seq[0] > MAX_OBJECTS:
            return

        ph = parent(h)
        sn = symname(h)

        item = {
            "i": seq[0],
            "h": h,
            "type": otype(h),
            "name": oname(h),
            "class": oclass(h),
            "sym": sn,
            "recs": recnames(h),
            "parts": parts_text(h),
            "ptype": otype(ph) if valid(ph) else -1,
            "pname": oname(ph) if valid(ph) else "",
            "psym": symname(ph) if valid(ph) else ""
        }

        result["items"].append(item)

        if sn:
            dh = symdef(sn)
            if valid(dh):
                result["defs"][sn] = dh

    try:
        vs.ForEachObjectInList(inspect, 0, 2, first)
    except Exception as e:
        result["error"] = "Traversal warning: {}".format(e)

    return result


def dump_definition(defh, title, visited=None, depth=0, counter=None):
    if visited is None:
        visited = set()

    if counter is None:
        counter = [0]

    pad = "  " * depth
    out = []

    if depth > MAX_DEPTH:
        return [pad + "[max definition depth reached]"]

    key = oname(defh) or title

    if key in visited:
        return [pad + "[already scanned: {}]".format(key)]

    visited.add(key)

    out.append(pad + "DEFINITION: " + title)
    out.append(pad + "Identity: " + ident(defh))

    dr = recnames(defh)
    if dr:
        out.append(
            pad + "Definition records: " + ", ".join(dr)
        )

    out.extend(dump_records(defh, pad + "  "))

    try:
        ch = vs.FInSymDef(defh)
    except:
        ch = None

    idx = 0

    while valid(ch):
        counter[0] += 1

        if counter[0] > MAX_OBJECTS:
            out.append(
                pad + "[definition scan safety limit reached]"
            )
            break

        idx += 1
        sn = symname(ch)
        rn = recnames(ch)

        out.append(
            pad + "  OBJ #{:03d}: {}".format(
                idx, ident(ch)
            )
        )

        ps = parts_text(ch)
        if ps:
            out.append(
                pad + "    PARTS: " + ps
            )

        if rn:
            out.extend(
                dump_records(ch, pad + "    ")
            )

        if sn:
            nested = symdef(sn)
            if valid(nested):
                out.extend(
                    dump_definition(
                        nested,
                        sn,
                        visited,
                        depth + 1,
                        counter
                    )
                )

        try:
            ch = vs.NextObj(ch)
        except:
            break

    return out


def lighting_device_section(h):
    out = []

    if not hasrec(h, LD_REC):
        return out

    out += [
        "=" * 72,
        "LIGHTING DEVICE CLUES",
        "=" * 72,
    ]

    acc = rfield(h, LD_REC, "__AccessoriesCount")
    primary = rfield(h, LD_REC, "Symbol Definition")

    if not primary:
        primary = rfield(h, LD_REC, "Symbol Name")

    out.append(
        "Accessories count: {!r}".format(acc)
    )
    out.append(
        "Symbol Definition: {!r}".format(
            rfield(h, LD_REC, "Symbol Definition")
        )
    )
    out.append(
        "Symbol Name: {!r}".format(
            rfield(h, LD_REC, "Symbol Name")
        )
    )

    if primary:
        dh = symdef(primary)

        if valid(dh):
            out.append("Resolved fixture resource: " + primary)

            if hasrec(dh, LIGHT_REC):
                out.append(
                    "Light Info Device Type: {!r}".format(
                        rfield(dh, LIGHT_REC, "Device Type")
                    )
                )

            if hasrec(dh, ENT_REC):
                out.append(
                    "EntEquip Device Type: {!r}".format(
                        rfield(dh, ENT_REC, "Device Type")
                    )
                )
        else:
            out.append(
                "Could not resolve fixture resource: " + primary
            )

    out.append("")
    return out


def build_report(sel):
    out = []

    out += [
        "=" * 72,
        "MINDREADER V5.0 - UNIVERSAL OBJECT INSPECTION",
        "=" * 72,
        "READ ONLY",
        "",
        "SELECTED OBJECT",
        "-" * 72,
        ident(sel),
        "Bounding box: " + bbox_text(sel),
        "Center: " + center_text(sel),
        "",
        "PARENT / CONTAINER CHAIN",
        "-" * 72,
    ]

    out.extend(parent_chain(sel))

    out += [
        "",
        "PARAMETRIC / PON DATA",
        "-" * 72,
    ]

    out.extend(dump_parametric_record(sel))

    out += [
        "",
        "ATTACHED RECORDS",
        "-" * 72,
    ]

    out.extend(dump_records(sel))

    ps = parts_text(sel)
    if ps:
        out += [
            "",
            "PARTS QUICK VIEW",
            "-" * 72,
            ps,
        ]

    selected_sym = symname(sel)
    selected_def = symdef(selected_sym) if selected_sym else None

    if valid(selected_def):
        out += [
            "",
            "=" * 72,
            "SELECTED SYMBOL DEFINITION",
            "=" * 72,
        ]
        out.extend(
            dump_definition(
                selected_def,
                selected_sym
            )
        )

    scan = scan_children(sel)

    out += [
        "",
        "=" * 72,
        "CHILD / GENERATED CONTENTS",
        "=" * 72,
    ]

    if not scan["ok"]:
        out.append(scan["error"])
    else:
        out.append(
            "Objects exposed: {}".format(
                len(scan["items"])
            )
        )

        if scan["error"]:
            out.append(scan["error"])

        out.append("")

        for it in scan["items"]:
            out.append(
                "CHILD #{:04d}".format(it["i"])
            )
            out.append(
                "  Type: {}".format(it["type"])
            )

            if it["name"]:
                out.append(
                    "  Name: " + it["name"]
                )

            if it["class"]:
                out.append(
                    "  Class: " + it["class"]
                )

            if it["sym"]:
                out.append(
                    "  Symbol: " + it["sym"]
                )

            pp = ["type {}".format(it["ptype"])]

            if it["pname"]:
                pp.append(
                    "name={!r}".format(it["pname"])
                )

            if it["psym"]:
                pp.append(
                    "symbol={!r}".format(it["psym"])
                )

            out.append(
                "  Parent: " + ", ".join(pp)
            )

            if it["recs"]:
                out.append(
                    "  Records: " + ", ".join(it["recs"])
                )
                out.extend(
                    dump_records(it["h"], "    ")
                )

            if it["parts"]:
                out.append(
                    "  PARTS: " + it["parts"]
                )

            out.append("")

    if scan["defs"]:
        out += [
            "",
            "=" * 72,
            "EMBEDDED SYMBOL DEFINITIONS",
            "=" * 72,
        ]

        for nm in sorted(scan["defs"].keys()):
            out.append("")
            out.extend(
                dump_definition(
                    scan["defs"][nm],
                    nm
                )
            )

    out += lighting_device_section(sel)

    out += [
        "=" * 72,
        "END REPORT",
        "=" * 72,
    ]

    summary = {
        "type": otype(sel),
        "name": oname(sel),
        "class": oclass(sel),
        "symbol": selected_sym,
        "parametric": "",
        "records": recnames(sel),
        "children": len(scan["items"]) if scan["ok"] else 0,
        "child_scan": scan["ok"],
        "lighting": hasrec(sel, LD_REC),
    }

    pr = parametric_record(sel)
    if valid(pr):
        summary["parametric"] = oname(pr)

    return "\n".join(out), summary


def safe_filename(summary):
    base = (
        summary["name"]
        or summary["symbol"]
        or summary["parametric"]
        or "Object_Type_{}".format(summary["type"])
    )

    for c in '<>:"/\\|?*':
        base = base.replace(c, "_")

    return "MINDREADER_V5_4_{}.txt".format(base)


def save_report(text, summary):
    suggested = safe_filename(summary)

    # Avoid PutFile entirely. In VW26, PutFile can leave the chosen
    # output file owned/open by Vectorworks, which then conflicts with
    # Python open(). Instead, ask only for a destination folder, then
    # let Python create the report file itself.
    try:
        result = vs.GetFolder(
            "Choose a folder for the MINDREADER report"
        )
    except Exception as e:
        vs.AlrtDialog(
            "MINDREADER V5.0\n\n"
            "Could not open the folder picker:\n{}".format(e)
        )
        return

    folder = ""

    try:
        if isinstance(result, tuple):
            if len(result) >= 2:
                folder = result[1]
        elif isinstance(result, str):
            folder = result
    except:
        folder = ""

    folder = str(folder or "").strip()

    if not folder:
        return

    filename = vs.StrDialog(
        "MINDREADER V5.0\n\n"
        "Report filename:",
        suggested
    )

    try:
        if vs.DidCancel():
            return
    except:
        pass

    filename = str(filename or "").strip()

    if not filename:
        return

    for c in '<>:"/\\|?*':
        filename = filename.replace(c, "_")

    if not filename.lower().endswith(".txt"):
        filename += ".txt"

    target = os.path.join(
        folder,
        filename
    )

    try:
        with open(
            target,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(text)

        vs.AlrtDialog(
            "MINDREADER V5.0 - REPORT SAVED\n\n{}".format(
                target
            )
        )
        return

    except Exception as first_error:
        try:
            fallback = os.path.join(
                tempfile.gettempdir(),
                filename
            )

            with open(
                fallback,
                "w",
                encoding="utf-8"
            ) as f:
                f.write(text)

            vs.AlrtDialog(
                "MINDREADER V5.0\n\n"
                "The chosen folder could not be written:\n"
                "{}\n\n"
                "I saved the report here instead:\n\n"
                "{}".format(
                    first_error,
                    fallback
                )
            )

        except Exception as second_error:
            vs.AlrtDialog(
                "MINDREADER V5.0\n\n"
                "Could not save the report.\n\n"
                "Chosen-folder error:\n{}\n\n"
                "Fallback error:\n{}".format(
                    first_error,
                    second_error
                )
            )



# ============================================================================
# SAFE TARGET RESOLVER
# ============================================================================
#
# The inspector itself is generic and stable. VW26's fragile part is target
# acquisition while editing inside a symbol definition.
#
# v5 deliberately avoids interactive tracking callbacks and avoids scanning
# every symbol definition for stale selection flags.
#
# For nested symbol contents, browse ONE explicitly named symbol definition
# and choose an object by number.

MAX_BROWSER_OBJECTS = 250
MAX_BROWSER_DEPTH = 6


def pon_name(h):
    pr = parametric_record(h)
    if valid(pr):
        return oname(pr)
    return ""


def hyperlink_hint(h):
    p = pon_name(h)

    if p not in ("Hyperlink CW", "Hyperlink"):
        return ""

    label = ""
    target = ""
    function = ""

    for rec in recnames(h):
        if rec in ("Hyperlink CW", "Hyperlink"):
            label = (
                rfield(h, rec, "EditableLabel")
                or rfield(h, rec, "Description")
                or rfield(h, rec, "Label")
            )
            target = (
                rfield(h, rec, "target")
                or rfield(h, rec, "SheetLayer")
                or rfield(h, rec, "Url")
            )
            function = (
                rfield(h, rec, "function")
                or rfield(h, rec, "EditableFunction")
            )
            break

    bits = []

    if function:
        bits.append(function)

    if label:
        bits.append("label={!r}".format(label))

    if target:
        bits.append("target={!r}".format(target))

    return "; ".join(bits)


def browser_descriptor(h, path_text):
    bits = [
        path_text,
        "type {}".format(otype(h))
    ]

    p = pon_name(h)

    if p:
        bits.append("PIO={!r}".format(p))

    s = symname(h)

    if s:
        bits.append("symbol={!r}".format(s))

    n = oname(h)

    if n:
        bits.append("name={!r}".format(n))

    c = oclass(h)

    if c and c != "None":
        bits.append("class={!r}".format(c))

    recs = recnames(h)

    if recs:
        bits.append(
            "records=" + ",".join(recs)
        )

    hh = hyperlink_hint(h)

    if hh:
        bits.append(hh)

    return " | ".join(bits)


def collect_symbol_contents(defh):
    items = []
    seen_count = [0]

    def walk(first, prefix, depth):
        if depth > MAX_BROWSER_DEPTH:
            return

        h = first
        idx = 0

        while valid(h):
            idx += 1
            seen_count[0] += 1

            if seen_count[0] > MAX_BROWSER_OBJECTS:
                return

            path_text = "{}{}".format(
                prefix,
                idx
            )

            items.append(
                {
                    "h": h,
                    "path": path_text,
                    "desc": browser_descriptor(
                        h,
                        path_text
                    )
                }
            )

            try:
                child = vs.FInGroup(h)
            except:
                child = None

            if valid(child):
                walk(
                    child,
                    path_text + ".",
                    depth + 1
                )

            try:
                h = vs.NextObj(h)
            except:
                break

    try:
        first = vs.FInSymDef(defh)
    except:
        first = None

    if valid(first):
        walk(
            first,
            "",
            0
        )

    return items


def filter_browser_items(items, text):
    text = str(text or "").strip().lower()

    if not text:
        return items

    return [
        item
        for item in items
        if text in item["desc"].lower()
    ]


def browser_list_text(items, symbol_name, filter_text):
    lines = [
        "MINDREADER V5.0 - SYMBOL CONTENTS",
        "",
        "Symbol Definition: {}".format(
            symbol_name
        )
    ]

    if filter_text:
        lines.append(
            "Filter: {!r}".format(
                filter_text
            )
        )

    lines += [
        "",
        "Objects found: {}".format(
            len(items)
        ),
        ""
    ]

    for i, item in enumerate(items, 1):
        lines.append(
            "{}. {}".format(
                i,
                item["desc"]
            )
        )

    return "\n".join(lines)


def pick_object_from_symbol_definition():
    symbol_name = vs.StrDialog(
        "MINDREADER V5.0\n\n"
        "Type the exact Symbol Definition name to inspect.\n\n"
        "Example:\n"
        "TOC BIG",
        ""
    )

    try:
        if vs.DidCancel():
            return None, "Cancelled.", ""
    except:
        pass

    symbol_name = str(
        symbol_name or ""
    ).strip()

    if not symbol_name:
        return None, "No Symbol Definition name entered.", ""

    defh = symdef(
        symbol_name
    )

    if not valid(defh):
        return (
            None,
            "Symbol Definition not found:\n{}".format(
                symbol_name
            ),
            ""
        )

    all_items = collect_symbol_contents(
        defh
    )

    if not all_items:
        return (
            None,
            "No inspectable objects were found inside:\n{}".format(
                symbol_name
            ),
            ""
        )

    filter_text = vs.StrDialog(
        "MINDREADER V5.0\n\n"
        "Optional filter.\n\n"
        "Examples:\n"
        "Hyperlink\n"
        "Lighting Device\n"
        "Parts\n"
        "Labels- Tags\n\n"
        "Leave blank to show everything.",
        ""
    )

    try:
        if vs.DidCancel():
            return None, "Cancelled.", ""
    except:
        pass

    filter_text = str(
        filter_text or ""
    ).strip()

    items = filter_browser_items(
        all_items,
        filter_text
    )

    if not items:
        vs.AlrtDialog(
            "MINDREADER V5.0\n\n"
            "Nothing inside {} matched:\n\n"
            "{}".format(
                symbol_name,
                filter_text
            )
        )
        return None, "Nothing matched the filter.", ""

    preview = items[:60]

    vs.AlrtDialog(
        browser_list_text(
            preview,
            symbol_name,
            filter_text
        ) +
        (
            "\n\nShowing first 60 matches. Refine the filter if needed."
            if len(items) > 60
            else ""
        )
    )

    choice = vs.StrDialog(
        "MINDREADER V5.0\n\n"
        "Enter the number of the object to inspect:",
        "1"
    )

    try:
        if vs.DidCancel():
            return None, "Cancelled.", ""
    except:
        pass

    try:
        n = int(
            str(choice).strip()
        )
    except:
        return None, "Object number must be an integer.", ""

    if n < 1 or n > len(preview):
        return (
            None,
            "Object number must be between 1 and {}.".format(
                len(preview)
            ),
            ""
        )

    picked = preview[n - 1]

    return (
        picked["h"],
        "",
        "symbol browser: {} / {}".format(
            symbol_name,
            picked["path"]
        )
    )


def selected_object():
    # Safe ordinary drawing-object selection.
    # Nested symbol-edit selections use Symbol Definition Browser mode.

    try:
        h = vs.FSActLayer()
    except:
        h = None

    if valid(h):
        try:
            nxt = vs.NextSObj(h)
        except:
            nxt = None

        if valid(nxt):
            return (
                None,
                "More than one object is selected on the active layer.",
                ""
            )

        return (
            h,
            "",
            "selected drawing object"
        )

    found = []

    try:
        vs.ForEachObject(
            lambda obj: found.append(obj),
            "(SEL=TRUE)"
        )
    except:
        pass

    if len(found) == 1:
        return (
            found[0],
            "",
            "criteria fallback"
        )

    if len(found) > 1:
        return (
            None,
            "More than one drawing object is selected.",
            ""
        )

    return (
        None,
        "No ordinary drawing object is selected.",
        ""
    )


def main():
    browse_symbol = vs.YNDialog(
        "MINDREADER V5.0\n\n"
        "What do you want to inspect?\n\n"
        "YES = OBJECT INSIDE A SYMBOL DEFINITION\n"
        "Use this for things such as a Hyperlink inside your TOC symbol.\n\n"
        "NO = SELECTED DRAWING OBJECT\n"
        "Use this for ordinary objects on a design/sheet layer."
    )

    if browse_symbol:
        sel, error, selection_source = (
            pick_object_from_symbol_definition()
        )
    else:
        sel, error, selection_source = (
            selected_object()
        )

    if not valid(sel):
        if error and error != "Cancelled.":
            vs.AlrtDialog(
                "MINDREADER V5.0\n\n" + error
            )
        return

    text, summary = build_report(
        sel
    )

    record_text = (
        ", ".join(
            summary["records"]
        )
        if summary["records"]
        else "<none>"
    )

    msg = (
        "MINDREADER V5.0 - UNIVERSAL INSPECTOR\n\n"
        "Target source: {selection_source}\n"
        "Object type: {type}\n"
        "Name: {name}\n"
        "Symbol: {symbol}\n"
        "Parametric/PON: {parametric}\n"
        "Attached records: {records}\n"
        "Child/generated objects: {children}\n"
        "Lighting Device: {lighting}\n\n"
        "Save full report?"
    ).format(
        selection_source=selection_source or "unknown",
        type=summary["type"],
        name=summary["name"] or "<none>",
        symbol=summary["symbol"] or "<none>",
        parametric=summary["parametric"] or "<none>",
        records=record_text,
        children=summary["children"],
        lighting=(
            "YES"
            if summary["lighting"]
            else "NO"
        ),
    )

    if vs.YNDialog(
        msg
    ):
        save_report(
            text,
            summary
        )


main()
