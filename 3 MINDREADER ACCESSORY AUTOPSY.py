# VWX FAILS - MINDREADER ACCESSORY AUTOPSY v1.0
# vibed by Chuckles
# Date: 2026-08-18
# Version: v1.0
#
# Vectorworks Fixes, Automation, Inspection & Library Scripts
# Secondary read-only accessory anatomy diagnostic.

# MINDREADER DEEPDIVE: ACCESSORY ANATOMY v1.0
# VWX FAILS
#
# READ ONLY.
#
# Select one Spotlight Lighting Device with an accessory and run.
#
# Purpose:
#   Inspect the generated accessory instance, its parent/container,
#   transformation/orientation data, and every object inside the accessory
#   symbol definition. This is intended for Base-vs-Yoke comparisons.
#
# No records, geometry, classes, resources, or object variables are modified.

import vs

PIO_TYPE = 86
SYM_INST = 15
SYM_DEF = 16
REC_DEF = 47

LD_REC = "Lighting Device"
LIGHT_REC = "Light Info Record"
PARTS_REC = "Parts"
ENT_REC = "EntEquipUniversal"

MAX_OBJECTS = 3000
MAX_DEPTH = 10


# ---------------------------------------------------------------------------
# SAFE BASICS
# ---------------------------------------------------------------------------

def valid(h):
    if h is None:
        return False
    try:
        return h != vs.Handle()
    except:
        return True


def typ(h):
    try:
        return vs.GetTypeN(h)
    except:
        return -1


def name(h):
    try:
        v = vs.GetName(h)
        return v if v else ""
    except:
        return ""


def cls(h):
    try:
        v = vs.GetClass(h)
        return v if v else ""
    except:
        return ""


def sym_name(h):
    try:
        v = vs.GetSymName(h)
        return v if v else ""
    except:
        return ""


def parent(h):
    try:
        p = vs.GetParent(h)
        return p if valid(p) else None
    except:
        return None


def rfield(h, rec, fld):
    try:
        v = vs.GetRField(h, rec, fld)
        return "" if v is None else str(v)
    except:
        return ""


def rec_names(h):
    out = []
    try:
        n = vs.NumRecords(h)
    except:
        return out

    for i in range(1, n + 1):
        try:
            rh = vs.GetRecord(h, i)
            if valid(rh):
                rn = vs.GetName(rh)
                if rn:
                    out.append(rn)
        except:
            pass

    return out


def has_rec(h, rec):
    return rec in rec_names(h)


def parts_summary(h):
    if not has_rec(h, PARTS_REC):
        return ""

    fields = ["Base", "Yoke", "Body", "Lens", "Point", "Light Emitter"]

    return ", ".join(
        "{}={}".format(f, rfield(h, PARTS_REC, f))
        for f in fields
    )


def ident(h):
    bits = ["type {}".format(typ(h))]

    n = name(h)
    if n:
        bits.append("name={!r}".format(n))

    s = sym_name(h)
    if s:
        bits.append("symbol={!r}".format(s))

    c = cls(h)
    if c:
        bits.append("class={!r}".format(c))

    return ", ".join(bits)


def fmt_num(v):
    try:
        return "{:.9g}".format(float(v))
    except:
        return str(v)


def fmt_pt(v):
    try:
        return "(" + ", ".join(fmt_num(x) for x in v) + ")"
    except:
        return repr(v)


# ---------------------------------------------------------------------------
# GEOMETRY / TRANSFORM SNAPSHOT
# ---------------------------------------------------------------------------

def safe_call(label, fn):
    try:
        return label + ": " + fn()
    except Exception as e:
        return label + ": <unavailable: {}>".format(e)


def transform_lines(h, ind=""):
    out = []

    out.append(
        ind + safe_call(
            "GetSymLoc",
            lambda: fmt_pt(vs.GetSymLoc(h))
        )
    )

    out.append(
        ind + safe_call(
            "GetSymRot",
            lambda: fmt_num(vs.GetSymRot(h))
        )
    )

    out.append(
        ind + safe_call(
            "GetBBox",
            lambda: repr(vs.GetBBox(h))
        )
    )

    out.append(
        ind + safe_call(
            "Get3DCntr",
            lambda: repr(vs.Get3DCntr(h))
        )
    )

    out.append(
        ind + safe_call(
            "Get3DInfo",
            lambda: repr(vs.Get3DInfo(h))
        )
    )

    out.append(
        ind + safe_call(
            "Get3DOrientation",
            lambda: repr(vs.Get3DOrientation(h))
        )
    )

    out.append(
        ind + safe_call(
            "GetEntityMatrix",
            lambda: repr(vs.GetEntityMatrix(h))
        )
    )

    out.append(
        ind + safe_call(
            "IsPlanarObj",
            lambda: repr(vs.IsPlanarObj(h))
        )
    )

    out.append(
        ind + safe_call(
            "GetPlanarRef",
            lambda: repr(vs.GetPlanarRef(h))
        )
    )

    return out


# ---------------------------------------------------------------------------
# RECORD SUMMARY
# ---------------------------------------------------------------------------

def record_identity_lines(h, ind=""):
    out = []

    rn = rec_names(h)
    out.append(
        ind + "Records: " + (", ".join(rn) if rn else "(none)")
    )

    ps = parts_summary(h)
    if ps:
        out.append(ind + "Parts: " + ps)

    if has_rec(h, LIGHT_REC):
        out.append(
            ind + "Light Info.Device Type = {!r}".format(
                rfield(h, LIGHT_REC, "Device Type")
            )
        )
        out.append(
            ind + "Light Info.Model Name = {!r}".format(
                rfield(h, LIGHT_REC, "Model Name")
            )
        )

    if has_rec(h, ENT_REC):
        out.append(
            ind + "EntEquip.Device Type = {!r}".format(
                rfield(h, ENT_REC, "Device Type")
            )
        )
        out.append(
            ind + "EntEquip.Symbol Name = {!r}".format(
                rfield(h, ENT_REC, "Symbol Name")
            )
        )

    return out


# ---------------------------------------------------------------------------
# ACCESSORY DISCOVERY INSIDE LIGHTING DEVICE PIO
# ---------------------------------------------------------------------------

def pio_children(pio):
    items = []

    try:
        first = vs.FInGroup(pio)
    except:
        return items

    if not valid(first):
        return items

    def collect(h):
        if len(items) < MAX_OBJECTS:
            items.append(h)

    try:
        vs.ForEachObjectInList(collect, 0, 2, first)
    except:
        pass

    return items


def find_accessories(pio):
    candidates = []

    for h in pio_children(pio):
        if typ(h) != SYM_INST:
            continue

        if not has_rec(h, LIGHT_REC):
            continue

        device_type = rfield(
            h,
            LIGHT_REC,
            "Device Type"
        ).strip().lower()

        if device_type == "static accessory":
            candidates.append(h)

    return candidates


def resolve_symdef(sym_inst):
    s = sym_name(sym_inst)
    if not s:
        return None

    try:
        h = vs.GetObject(s)
    except:
        return None

    if valid(h) and typ(h) == SYM_DEF:
        return h

    return None


# ---------------------------------------------------------------------------
# FULL DEFINITION ANATOMY
# ---------------------------------------------------------------------------

def classify_hint(h):
    """
    A descriptive hint only. It does not alter or formally classify the object.
    """
    t = typ(h)

    planar = None
    try:
        planar = vs.IsPlanarObj(h)
    except:
        pass

    if planar is True:
        return "planar"

    if t in (1, 2, 3, 4, 5, 6, 7, 8, 10, 21):
        return "likely-2D"

    if t in (9, 24, 84, 86, 95, 96, 113):
        return "3D-or-container"

    if t == 15:
        return "nested-symbol"

    if t == 11:
        return "group"

    return "unclassified"


def first_in_container(h):
    t = typ(h)

    try:
        if t == SYM_DEF:
            return vs.FInSymDef(h)
        if t in (11, 86):
            return vs.FInGroup(h)
    except:
        return None

    return None


def walk_definition(def_h):
    lines = []
    seen_defs = set()
    count = [0]

    def walk_container(container_h, path, depth):
        if depth > MAX_DEPTH:
            lines.append(
                "  " * depth + "[max depth reached at {}]".format(path)
            )
            return

        ch = first_in_container(container_h)

        if not valid(ch):
            return

        idx = 0

        while valid(ch):
            count[0] += 1
            if count[0] > MAX_OBJECTS:
                lines.append(
                    "  " * depth + "[object safety limit reached]"
                )
                return

            idx += 1
            here = "{} / #{:03d}".format(path, idx)
            pad = "  " * depth

            lines.append(
                pad + "OBJECT " + here
            )
            lines.append(
                pad + "  " + ident(ch)
            )
            lines.append(
                pad + "  Anatomy hint: " + classify_hint(ch)
            )

            lines.extend(
                record_identity_lines(ch, pad + "  ")
            )

            lines.extend(
                transform_lines(ch, pad + "  ")
            )

            sn = sym_name(ch)
            if sn:
                lines.append(
                    pad + "  Nested symbol definition: " + sn
                )

                try:
                    nd = vs.GetObject(sn)
                except:
                    nd = None

                if valid(nd) and typ(nd) == SYM_DEF:
                    if sn not in seen_defs:
                        seen_defs.add(sn)
                        walk_container(
                            nd,
                            path + " / SYMBOL<{}>".format(sn),
                            depth + 1
                        )
                    else:
                        lines.append(
                            pad + "    [nested definition already scanned]"
                        )

            if typ(ch) in (11, 86):
                walk_container(
                    ch,
                    here + " / CONTAINER",
                    depth + 1
                )

            lines.append("")

            try:
                ch = vs.NextObj(ch)
            except:
                break

    root_name = name(def_h) or "<accessory definition>"
    seen_defs.add(root_name)

    lines.append("DEFINITION ROOT: " + root_name)
    lines.extend(record_identity_lines(def_h, "  "))
    lines.extend(transform_lines(def_h, "  "))
    lines.append("")

    walk_container(
        def_h,
        root_name,
        0
    )

    lines.append(
        "Definition objects inspected: {}".format(count[0])
    )

    return lines


# ---------------------------------------------------------------------------
# VS MODULE CAPABILITY SURFACE
# ---------------------------------------------------------------------------

def api_surface_lines():
    """
    Lists potentially relevant API function names available in this build of
    Vectorworks. This lets us discover component-specific calls exposed by
    the runtime without guessing function names.
    """
    out = []

    keys = (
        "component",
        "planar",
        "matrix",
        "orientation",
        "symbol",
        "sym",
        "2d",
        "3d",
        "objectvariable",
    )

    try:
        names = dir(vs)
    except:
        names = []

    hits = []

    for n in names:
        low = n.lower()
        if any(k in low for k in keys):
            hits.append(n)

    hits = sorted(set(hits))

    out.append(
        "Potentially relevant vs API names exposed: {}".format(len(hits))
    )

    for n in hits[:400]:
        out.append("  " + n)

    if len(hits) > 400:
        out.append(
            "  ... {} additional names omitted".format(len(hits) - 400)
        )

    return out


# ---------------------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------------------

def build_report(sel):
    out = []

    out.append("=" * 76)
    out.append("MINDREADER DEEPDIVE - ACCESSORY ANATOMY v1.0")
    out.append("=" * 76)
    out.append("READ ONLY")
    out.append("")

    out.append("SELECTED LIGHTING DEVICE")
    out.append("-" * 76)
    out.append(ident(sel))
    out.extend(record_identity_lines(sel, "  "))
    out.extend(transform_lines(sel, "  "))

    if has_rec(sel, LD_REC):
        out.append(
            "  Lighting Device.Symbol Definition = {!r}".format(
                rfield(sel, LD_REC, "Symbol Definition")
            )
        )
        out.append(
            "  Lighting Device.__AccessoriesCount = {!r}".format(
                rfield(sel, LD_REC, "__AccessoriesCount")
            )
        )

    out.append("")

    children = pio_children(sel)

    out.append("PIO GENERATED CHILD MAP")
    out.append("-" * 76)
    out.append(
        "Deep generated objects found: {}".format(len(children))
    )

    for i, h in enumerate(children, start=1):
        out.append(
            "#{:03d}: {}".format(i, ident(h))
        )

        p = parent(h)
        if valid(p):
            out.append(
                "      parent -> " + ident(p)
            )

        ps = parts_summary(h)
        if ps:
            out.append("      Parts -> " + ps)

        if has_rec(h, LIGHT_REC):
            out.append(
                "      Device Type -> {!r}".format(
                    rfield(h, LIGHT_REC, "Device Type")
                )
            )

    out.append("")

    accessories = find_accessories(sel)

    out.append("ACCESSORY DISCOVERY")
    out.append("-" * 76)
    out.append(
        "Static Accessory instances found: {}".format(len(accessories))
    )
    out.append("")

    if not accessories:
        out.append(
            "No generated Static Accessory symbol instance was found."
        )
        out.append(
            "Run this on a Lighting Device containing one inserted accessory."
        )

    for n, acc in enumerate(accessories, start=1):
        out.append("=" * 76)
        out.append(
            "ACCESSORY #{:02d}: {}".format(
                n,
                sym_name(acc) or "<unnamed>"
            )
        )
        out.append("=" * 76)

        out.append("GENERATED ACCESSORY INSTANCE")
        out.append("-" * 76)
        out.append(ident(acc))
        out.extend(record_identity_lines(acc, "  "))

        p = parent(acc)
        if valid(p):
            out.append("  Parent: " + ident(p))
        else:
            out.append("  Parent: <none>")

        out.extend(transform_lines(acc, "  "))
        out.append("")

        if valid(p):
            out.append("ACCESSORY PARENT / CONTAINER TRANSFORM")
            out.append("-" * 76)
            out.append(ident(p))
            out.extend(transform_lines(p, "  "))
            out.append("")

        def_h = resolve_symdef(acc)

        out.append("ACCESSORY SYMBOL DEFINITION ANATOMY")
        out.append("-" * 76)

        if valid(def_h):
            out.extend(walk_definition(def_h))
        else:
            out.append(
                "Accessory symbol definition could not be resolved."
            )

        out.append("")

    out.append("=" * 76)
    out.append("VECTORWORKS API SURFACE - COMPONENT / TRANSFORM CLUES")
    out.append("=" * 76)
    out.extend(api_surface_lines())

    out.append("")
    out.append("=" * 76)
    out.append("END DEEPDIVE")
    out.append("=" * 76)

    return "\n".join(out), accessories


# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------

def safe_file_piece(s):
    if not s:
        return "Accessory"

    for c in '<>:"/\\|?*':
        s = s.replace(c, "_")

    return s.strip() or "Accessory"


def save_report(text, accessory_name):
    suggested = "MINDREADER_DEEPDIVE_{}.txt".format(
        safe_file_piece(accessory_name)
    )

    try:
        fn = vs.PutFile(
            "Save MINDREADER DeepDive report:",
            suggested
        )
    except Exception as e:
        vs.AlrtDialog(
            "MINDREADER DeepDive\n\nSave dialog failed:\n{}".format(e)
        )
        return

    try:
        cancelled = vs.DidCancel()
    except:
        cancelled = not bool(fn)

    if cancelled or not fn:
        return

    try:
        vs.Close(fn)
    except:
        pass

    try:
        with open(fn, "w", encoding="utf-8") as f:
            f.write(text)

        vs.AlrtDialog(
            "MINDREADER DeepDive - Report Saved"
        )
    except Exception as e:
        vs.AlrtDialog(
            "MINDREADER DeepDive\n\nSave failed:\n{}".format(e)
        )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    sel = vs.FSActLayer()

    if not valid(sel):
        vs.AlrtDialog(
            "MINDREADER DeepDive\n\n"
            "Select one Lighting Device and run again."
        )
        return

    try:
        nxt = vs.NextSObj(sel)
    except:
        nxt = None

    if valid(nxt):
        vs.AlrtDialog(
            "MINDREADER DeepDive\n\n"
            "More than one object is selected."
        )
        return

    if typ(sel) != PIO_TYPE or not has_rec(sel, LD_REC):
        vs.AlrtDialog(
            "MINDREADER DeepDive\n\n"
            "The selected object is not a Lighting Device PIO."
        )
        return

    text, accessories = build_report(sel)

    names = [
        sym_name(h) or "<unnamed>"
        for h in accessories
    ]

    if names:
        detail = "\n".join(
            "  * " + n for n in names[:10]
        )
    else:
        detail = "  <none found>"

    msg = (
        "MINDREADER DeepDive - Accessory Anatomy\n\n"
        "Static Accessory instances found: {}\n\n"
        "{}\n\n"
        "Save full anatomy report?"
    ).format(
        len(accessories),
        detail
    )

    primary_name = names[0] if names else "Accessory"

    if vs.YNDialog(msg):
        save_report(text, primary_name)


main()
