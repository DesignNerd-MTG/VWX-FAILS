# -*- coding: utf-8 -*-
# VWX FAILS - FIXTURE TYPE TO NEW LAYER v1.2
# vibed by Chuckles
# Date: 2026-08-19
# Version: v1.2
#
# Menu Command: Fixture Type to New Layer  (VW26-safe)
import vs

LD_PIO = "Lighting Device"
LD_REC = "Lighting Device"
TYPE_CANDIDATES = ["Instrument Type", "Inst Type", "Fixture Type", "Type", "Device Type"]

def is_ld(h):
    try: return vs.GetTypeN(h)==86 and vs.GetName(vs.GetParametricRecord(h))==LD_PIO
    except: return False

def existing_field_names(h):
    pr = vs.GetParametricRecord(h)
    if not pr: return []
    return [vs.GetFldName(pr,i) for i in range(1, vs.NumFields(pr)+1)]

def first_existing_field(h, candidates):
    ex = set(existing_field_names(h))
    for c in candidates:
        if c in ex: return c
    return None

def get_type(h):
    fld = first_existing_field(h, TYPE_CANDIDATES)
    if not fld: return ""
    v = vs.GetRField(h, LD_REC, fld)
    return ("" if v is None else str(v)).strip()

def sanitize(name):
    s = " ".join((name or "").split())
    for ch in '\\/:*?"<>|': s = s.replace(ch, "-")
    return (s.strip() or "Untitled")[:255]

def ensure_layer(name):
    h = vs.GetObject(name)
    if h and vs.GetTypeN(h)==31: return h
    vs.Layer(name); return vs.ActLayer()

def seed_selected_lds():
    # Walk the selected-object chain on EACH layer.
    # FSActLayer only sees the active layer; users can select fixtures on
    # other layers when Layer Options allow Show/Snap/Modify Others.
    items=[]
    seen=set()

    try:
        layer = vs.FLayer()
    except:
        layer = None

    while layer:
        try:
            h = vs.FSObject(layer)
        except:
            h = None

        while h:
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
    # Top-level objects only, across all drawing layers.
    items=[]
    def f(h):
        if is_ld(h): items.append(h)
        return False
    try:
        vs.ForEachObjectInLayer(f, 0, 0, 1)
    except:
        pass
    return items

def group_by_type(handles):
    groups={}
    for h in handles:
        raw=get_type(h); key=raw.lower()
        if not key: continue
        groups.setdefault(key, {'raw':raw,'items':[]})['items'].append(h)
    return groups

def main():
    # scope
    only_selected = vs.YNDialog("Move ONLY currently selected LDs?\n\nYes = selection only\nNo  = ALL that match selected Instrument Type(s)")
    # prefix
    prefix_default = "LD - Type: "
    p = vs.StrDialog("Layer name prefix", prefix_default)
    if p is None: return
    prefix = p.strip() or prefix_default

    seed = seed_selected_lds()
    if not seed:
        vs.AlrtDialog("Select one or more Lighting Devices first."); return

    g_seed = group_by_type(seed)
    if not g_seed:
        vs.AlrtDialog("No Instrument Type / Inst Type / Fixture Type found on the selected LD(s).\n\nFields on first selection:\n- " + "\n- ".join(existing_field_names(seed[0])))
        return

    if only_selected:
        g_move = g_seed
    else:
        wanted = set(g_seed.keys())
        matches = [h for h in all_lds() if get_type(h).lower() in wanted]
        g_move = group_by_type(matches)

    total = sum(len(x['items']) for x in g_move.values())
    if total==0:
        vs.AlrtDialog("Nothing to move."); return

    seed_types = [
        info['raw']
        for _,info in sorted(
            g_seed.items(),
            key=lambda kv: kv[1]['raw'].lower()
        )
    ]
    scope_text = (
        "Selected Lighting Devices only"
        if only_selected
        else "ALL Lighting Devices matching selected Instrument Type(s)"
    )
    preview = (
        "FIXTURE TYPE TO NEW LAYER v1.2\n\n"
        "Seed selection: {} Lighting Device(s)\n"
        "Seed Instrument Type(s):\n- {}\n\n"
        "Scope: {}\n"
        "Targets: {} Lighting Device(s)\n\n"
        "Continue?"
    ).format(
        len(seed),
        "\n- ".join(seed_types),
        scope_text,
        total
    )
    if not vs.YNDialog(preview):
        return

    # per-type layers (create/reuse)
    key2layer={}
    for k,info in g_move.items():
        lname = sanitize(prefix + info['raw'])
        key2layer[k] = ensure_layer(lname)

    began=False; moved=0
    try:
        if hasattr(vs,"UndoBegin"): vs.UndoBegin(); began=True
        for k,info in g_move.items():
            lyr = key2layer[k]
            for h in info['items']:
                vs.SetParent(h, lyr); moved += 1
        vs.ReDrawAll()
    finally:
        if began and hasattr(vs,"UndoEnd"): vs.UndoEnd()

    lines = ["Moved {} Lighting Devices.".format(moved), "", "Grouped by: Instrument Type", "Layers created/used:"]
    for k,info in sorted(g_move.items(), key=lambda kv: kv[1]['raw'].lower()):
        lines.append("• {} → {} ({})".format(info['raw'], vs.GetLName(key2layer[k]), len(info['items'])))
    vs.AlrtDialog("\n".join(lines))

if __name__=="__main__":
    main()
