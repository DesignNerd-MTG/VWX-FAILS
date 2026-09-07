# VWX FAILS - DR. DOOM v1.1.1
# Drawing Review, Diagnostics, Organization & Object Manipulation
import vs
import math
from collections import Counter
VERSION = "1.2"
TITLE = "VWX FAILS - DR. DOOM v{}".format(VERSION)
GROUP_TYPE = 11
TYPE_NAMES = {
 2: "Line",
 3: "Rectangle",
 4: "Oval",
 5: "Polygon",
 6: "Arc / Circle",
 8: "Freehand",
 9: "3D Locus",
 10: "Text",
 11: "Group",
 12: "Quarter Arc",
 13: "Rounded Rectangle",
 14: "Image",
 15: "Symbol Instance",
 16: "Symbol Definition",
 17: "2D Locus",
 18: "Worksheet",
 21: "Polyline",
 22: "Image",
 24: "Extrude",
 25: "3D Polygon",
 31: "Layer",
 40: "Mesh",
 86: "Parametric Object",
}
HEAVY_LINEWEIGHT_MILS = 100
SIZE_OUTLIER_RATIO = 100.0
LARGE_FILLED_AREA_FRACTION = 0.05
DISTANT_DRAWING_DIAGONAL_FRACTION = 0.60
DISTANT_MEDIAN_SIZE_RATIO = 100.0
MAX_OBJECTS = 250000
MAX_GROUP_DEPTH = 32
MAX_FLAGGED_REPORT_ITEMS = 500
MAX_PREVIEW_ITEMS = 10
def valid(h):
 if h is None:
  return False
 try:
  return h != vs.Handle()
 except Exception:
  return True
def obj_type(h):
 try:
  return int(vs.GetTypeN(h))
 except Exception:
  return -1
def type_name(type_num):
 return TYPE_NAMES.get(type_num, "Type {}".format(type_num))
def obj_name(h):
 try:
  return vs.GetName(h) or ""
 except Exception:
  return ""
def obj_class(h):
 try:
  return vs.GetClass(h) or "<no class>"
 except Exception:
  return "<class unavailable>"
def layer_name(layer_h):
 try:
  name = vs.GetName(layer_h)
  if name:
   return name
 except Exception:
  pass
 try:
  name = vs.GetLName(layer_h)
  if name:
   return name
 except Exception:
  pass
 return "<unnamed layer>"
def bbox(h):
 try:
  raw = vs.GetBBox(h)
  if not raw or len(raw) != 2:
   return None
  p1, p2 = raw
  if len(p1) != 2 or len(p2) != 2:
   return None
  x1, y1 = p1
  x2, y2 = p2
  left = min(float(x1), float(x2))
  right = max(float(x1), float(x2))
  bottom = min(float(y1), float(y2))
  top = max(float(y1), float(y2))
  return (left, bottom, right, top)
 except Exception:
  return None
def lineweight(h):
 try:
  return int(vs.GetLW(h))
 except Exception:
  return None
def fill_pattern(h):
 try:
  return int(vs.GetFPat(h))
 except Exception:
  return None
def median(values):
 vals = sorted(values)
 n = len(vals)
 if not n:
  return 0.0
 mid = n // 2
 if n % 2:
  return float(vals[mid])
 return (float(vals[mid - 1]) + float(vals[mid])) / 2.0
def fmt_num(value):
 try:
  a = abs(float(value))
  if a >= 1000000:
   return "{:.3e}".format(value)
  if a >= 1000:
   return "{:,.2f}".format(value)
  if a >= 1:
   return "{:.3f}".format(value)
  return "{:.6f}".format(value)
 except Exception:
  return str(value)
def choose_scope():
 prompt = (
  "DR. DOOM v{}\n".format(VERSION)
  + "Drawing Review, Diagnostics, Organization & Object Manipulation\n\n"
  + "DOOM CHOOSES HIS DOMAIN\n\n"
  + "1 = ACTIVE LAYER\n"
  "    Fast intake check for the layer you are working on.\n\n"
  "2 = ENTIRE DRAWING\n"
  "    Scan every layer in the file.\n\n"
  "Enter 1 or 2."
 )
 try:
  value = vs.StrDialog(prompt, "1")
 except Exception as e:
  vs.AlrtDialog(TITLE + "\n\nCould not open scope dialog:\n{}".format(e))
  return None
 try:
  if vs.DidCancel():
   return None
 except Exception:
  pass
 value = str(value).strip()
 if value == "1":
  return "ACTIVE_LAYER"
 if value == "2":
  return "ENTIRE_DRAWING"
 vs.AlrtDialog(
  TITLE + "\n\n"
  "DOOM REQUIRES PRECISION.\n\n"
  "Enter exactly 1 or 2. No changes were made."
 )
 return None
def scope_layers(scope):
 if scope == "ACTIVE_LAYER":
  try:
   h = vs.ActLayer()
  except Exception:
   h = None
  return [h] if valid(h) else []
 layers = []
 try:
  h = vs.FLayer()
 except Exception:
  h = None
 while valid(h):
  layers.append(h)
  try:
   h = vs.NextLayer(h)
  except Exception:
   break
 return layers
def make_item(h, layer_nm, depth, root_h):
 bb = bbox(h)
 item = {
  "h": h,
  "select_h": root_h if valid(root_h) else h,
  "type": obj_type(h),
  "name": obj_name(h),
  "class": obj_class(h),
  "layer": layer_nm,
  "depth": depth,
  "bbox": bb,
  "lineweight": lineweight(h),
  "fill": fill_pattern(h),
  "flags": [],
  "severity": "INFO",
 }
 if bb is not None:
  left, bottom, right, top = bb
  width = max(0.0, right - left)
  height = max(0.0, top - bottom)
  item["width"] = width
  item["height"] = height
  item["size"] = max(width, height)
  item["area"] = width * height
  item["cx"] = (left + right) / 2.0
  item["cy"] = (bottom + top) / 2.0
 else:
  item.update({
   "width": 0.0,
   "height": 0.0,
   "size": 0.0,
   "area": 0.0,
   "cx": None,
   "cy": None,
  })
 return item
def scan_group_children(group_h, layer_nm, depth, root_h, items, state):
 if depth > MAX_GROUP_DEPTH:
  state["depth_limit_hits"] += 1
  return
 try:
  child = vs.FInGroup(group_h)
 except Exception:
  child = None
 while valid(child):
  if state["object_count"] >= MAX_OBJECTS:
   state["object_limit_hit"] = True
   return
  walk_object(child, layer_nm, depth, root_h, items, state)
  try:
   child = vs.NextObj(child)
  except Exception:
   break
def walk_object(h, layer_nm, depth, root_h, items, state):
 if not valid(h):
  return
 if state["object_count"] >= MAX_OBJECTS:
  state["object_limit_hit"] = True
  return
 state["object_count"] += 1
 if not valid(root_h):
  root_h = h
 item = make_item(h, layer_nm, depth, root_h)
 items.append(item)
 if item["type"] == GROUP_TYPE:
  scan_group_children(
   h,
   layer_nm,
   depth + 1,
   root_h,
   items,
   state,
  )
def scan_layer(layer_h, items, state):
 lname = layer_name(layer_h)
 try:
  h = vs.FInLayer(layer_h)
 except Exception:
  h = None
 top_count = 0
 while valid(h):
  if state["object_count"] >= MAX_OBJECTS:
   state["object_limit_hit"] = True
   break
  top_count += 1
  walk_object(h, lname, 0, h, items, state)
  try:
   h = vs.NextObj(h)
  except Exception:
   break
 state["layer_top_counts"][lname] = top_count
def scan(scope):
 layers = scope_layers(scope)
 result = {
  "scope": scope,
  "layers": layers,
  "items": [],
  "object_count": 0,
  "object_limit_hit": False,
  "depth_limit_hits": 0,
  "layer_top_counts": {},
 }
 for layer_h in layers:
  scan_layer(layer_h, result["items"], result)
  if result["object_limit_hit"]:
   break
 return result
def add_flag(item, code, label, severity):
 item["flags"].append((code, label, severity))
 rank = {"INFO": 0, "SUSPICIOUS": 1, "DOOM": 2}
 if rank.get(severity, 0) > rank.get(item["severity"], 0):
  item["severity"] = severity
def geometry_stats(items):
 boxed = [i for i in items if i["bbox"] is not None]
 stats = {
  "bbox": None,
  "width": 0.0,
  "height": 0.0,
  "diag": 0.0,
  "area": 0.0,
  "median_size": 0.0,
  "median_cx": 0.0,
  "median_cy": 0.0,
 }
 if not boxed:
  return stats
 left = min(i["bbox"][0] for i in boxed)
 bottom = min(i["bbox"][1] for i in boxed)
 right = max(i["bbox"][2] for i in boxed)
 top = max(i["bbox"][3] for i in boxed)
 stats["bbox"] = (left, bottom, right, top)
 stats["width"] = max(0.0, right - left)
 stats["height"] = max(0.0, top - bottom)
 stats["diag"] = math.hypot(stats["width"], stats["height"])
 stats["area"] = stats["width"] * stats["height"]
 sizes = [i["size"] for i in boxed if i["size"] > 0]
 centers_x = [i["cx"] for i in boxed if i["cx"] is not None]
 centers_y = [i["cy"] for i in boxed if i["cy"] is not None]
 stats["median_size"] = median(sizes)
 stats["median_cx"] = median(centers_x)
 stats["median_cy"] = median(centers_y)
 return stats
def analyze(scan_result):
 items = scan_result["items"]
 analysis = {
  "overall_bbox": None,
  "drawing_width": 0.0,
  "drawing_height": 0.0,
  "drawing_diag": 0.0,
  "median_size": 0.0,
  "class_counts": Counter(),
  "type_counts": Counter(),
  "layer_counts": Counter(),
  "layer_stats": {},
  "flag_counts": Counter(),
  "severity_counts": Counter(),
  "flagged": [],
  "selection_handles": [],
 }
 by_layer = {}
 for item in items:
  analysis["class_counts"][item["class"]] += 1
  analysis["type_counts"][item["type"]] += 1
  analysis["layer_counts"][item["layer"]] += 1
  by_layer.setdefault(item["layer"], []).append(item)
 combined = geometry_stats(items)
 analysis["overall_bbox"] = combined["bbox"]
 analysis["drawing_width"] = combined["width"]
 analysis["drawing_height"] = combined["height"]
 analysis["drawing_diag"] = combined["diag"]
 analysis["median_size"] = combined["median_size"]
 for lname, layer_items in by_layer.items():
  analysis["layer_stats"][lname] = geometry_stats(layer_items)
 for item in items:
  if item["type"] == GROUP_TYPE:
   continue
  stats = analysis["layer_stats"].get(item["layer"], {})
  layer_area = stats.get("area", 0.0)
  layer_diag = stats.get("diag", 0.0)
  layer_median_size = stats.get("median_size", 0.0)
  lw = item["lineweight"]
  if lw is not None and lw >= HEAVY_LINEWEIGHT_MILS:
   add_flag(
    item,
    "HEAVY_LINEWEIGHT",
    "Lineweight {} mils".format(lw),
    "DOOM",
   )
  size_outlier = (
   layer_median_size > 0
   and item["type"] != 2
   and item["size"] >= layer_median_size * SIZE_OUTLIER_RATIO
  )
  if size_outlier:
   add_flag(
    item, "SIZE_OUTLIER",
    "Object size is {:.1f}x layer median".format(item["size"] / layer_median_size),
    "SUSPICIOUS",
   )
  fill = item["fill"]
  large_filled = (
   fill is not None and fill != 0 and layer_area > 0
   and item["area"] >= layer_area * LARGE_FILLED_AREA_FRACTION
  )
  if large_filled:
   add_flag(
    item, "LARGE_FILLED_OBJECT",
    "Filled bbox is {:.1%} of layer bbox area".format(item["area"] / layer_area),
    "DOOM" if size_outlier else "SUSPICIOUS",
   )
  if (
   item["cx"] is not None
   and layer_diag > 0
   and layer_median_size > 0
  ):
   dist = math.hypot(
    item["cx"] - stats.get("median_cx", 0.0),
    item["cy"] - stats.get("median_cy", 0.0),
   )
   if (
    dist >= layer_diag * DISTANT_DRAWING_DIAGONAL_FRACTION
    and dist >= layer_median_size * DISTANT_MEDIAN_SIZE_RATIO
   ):
    add_flag(
     item,
     "SPATIAL_OUTLIER",
     "Far from main cluster on its layer",
     "DOOM",
    )
  if item["flags"]:
   analysis["flagged"].append(item)
   analysis["severity_counts"][item["severity"]] += 1
   for code, _label, _severity in item["flags"]:
    analysis["flag_counts"][code] += 1
 seen = set()
 for item in analysis["flagged"]:
  h = item["select_h"]
  try:
   key = int(h)
  except Exception:
   key = str(h)
  if key not in seen and valid(h):
   seen.add(key)
   analysis["selection_handles"].append(h)
 return analysis
def scope_text(scope):
 if scope == "ACTIVE_LAYER":
  return "Active layer"
 return "Entire drawing"
def bbox_text(bb):
 if bb is None:
  return "<unavailable>"
 l, b, r, t = bb
 return "({}, {}) to ({}, {})".format(
  fmt_num(l), fmt_num(b), fmt_num(r), fmt_num(t)
 )
def object_label(item):
 bits = [type_name(item["type"])]
 if item["name"]:
  bits.append("name={!r}".format(item["name"]))
 bits.append("class={!r}".format(item["class"]))
 bits.append("layer={!r}".format(item["layer"]))
 if item["depth"]:
  bits.append("group depth={}".format(item["depth"]))
 return ", ".join(bits)
def top_counter_lines(counter, limit=20, formatter=None):
 lines = []
 for key, count in counter.most_common(limit):
  label = formatter(key) if formatter else str(key)
  lines.append("  {:>7}  {}".format(count, label))
 extra = len(counter) - min(len(counter), limit)
 if extra > 0:
  lines.append("  ... {} more".format(extra))
 return lines
def build_report(scan_result, analysis):
 out = []
 out.extend([
  "=" * 78,
  "DR. DOOM v{} - DRAWING REVIEW, DIAGNOSTICS, ORGANIZATION & OBJECT MANIPULATION".format(VERSION),
  "=" * 78,
    "",
  "V1.2 SAFETY CONTRACT",
  "- Diagnosis first; repairs require explicit confirmation.",
  "",
  "SCAN SUMMARY",
  "-" * 78,
  "Scope: {}".format(scope_text(scan_result["scope"])),
  "Layers scanned: {}".format(len(scan_result["layers"])),
  "Objects scanned: {}".format(len(scan_result["items"])),
  "Classes used by scanned objects: {}".format(len(analysis["class_counts"])),
  "Object types found: {}".format(len(analysis["type_counts"])),
  "Flagged objects: {}".format(len(analysis["flagged"])),
  "  DOOM DEMANDS ATTENTION: {}".format(analysis["severity_counts"].get("DOOM", 0)),
  "  Suspicious: {}".format(analysis["severity_counts"].get("SUSPICIOUS", 0)),
  "",
  "Overall bbox: {}".format(bbox_text(analysis["overall_bbox"])),
  "Drawing width: {} document units".format(fmt_num(analysis["drawing_width"])),
  "Drawing height: {} document units".format(fmt_num(analysis["drawing_height"])),
  "Combined median non-zero object size: {} document units".format(fmt_num(analysis["median_size"])),
  "",
 ])
 if scan_result["object_limit_hit"]:
  out.append("WARNING: Object safety limit was reached. Scan is incomplete.")
  out.append("")
 if scan_result["depth_limit_hits"]:
  out.append(
   "WARNING: Group depth limit was reached {} time(s).".format(
    scan_result["depth_limit_hits"]
   )
  )
  out.append("")
 out.extend([
  "DETECTION THRESHOLDS",
  "-" * 78,
  "Heavy lineweight: >= {} mils".format(HEAVY_LINEWEIGHT_MILS),
  "Size outlier: >= {:.0f}x median object size ON ITS LAYER (simple Lines excluded)".format(SIZE_OUTLIER_RATIO),
  "Large filled object: >= {:.1%} of ITS LAYER bbox area".format(LARGE_FILLED_AREA_FRACTION),
  "Spatial outlier: >= {:.0%} of ITS LAYER diagonal AND >= {:.0f}x layer median object size from layer median center".format(
   DISTANT_DRAWING_DIAGONAL_FRACTION,
   DISTANT_MEDIAN_SIZE_RATIO,
  ),
  "",
  "These are review heuristics, not automatic guilt. Doom still expects judgment.",
  "",
  "FLAG COUNTS",
  "-" * 78,
 ])
 if analysis["flag_counts"]:
  for code, count in analysis["flag_counts"].most_common():
   out.append("  {:>7}  {}".format(count, code))
 else:
  out.append("  None. The drawing has escaped Doom's immediate suspicion.")
 out.extend(["", "OBJECT TYPES", "-" * 78])
 out.extend(
  top_counter_lines(
   analysis["type_counts"],
   limit=30,
   formatter=lambda n: "{} ({})".format(type_name(n), n),
  )
 )
 out.extend(["", "LAYERS", "-" * 78])
 out.extend(top_counter_lines(analysis["layer_counts"], limit=50))
 out.extend(["", "CLASSES", "-" * 78])
 out.extend(top_counter_lines(analysis["class_counts"], limit=75))
 out.extend(["", "FLAGGED OBJECTS", "-" * 78])
 if not analysis["flagged"]:
  out.append("None.")
 else:
  ranked = sorted(
   analysis["flagged"],
   key=lambda i: (0 if i["severity"] == "DOOM" else 1, i["layer"], i["class"]),
  )
  for idx, item in enumerate(ranked[:MAX_FLAGGED_REPORT_ITEMS], start=1):
   out.append("#{:04d} [{}] {}".format(idx, item["severity"], object_label(item)))
   out.append("       BBox: {}".format(bbox_text(item["bbox"])))
   out.append("       Size: {} x {}".format(fmt_num(item["width"]), fmt_num(item["height"])))
   if item["lineweight"] is not None:
    out.append("       Lineweight: {} mils".format(item["lineweight"]))
   if item["fill"] is not None:
    out.append("       Fill pattern index: {}".format(item["fill"]))
   for code, label, severity in item["flags"]:
    out.append("       - [{}] {}: {}".format(severity, code, label))
   out.append("")
  hidden = len(ranked) - MAX_FLAGGED_REPORT_ITEMS
  if hidden > 0:
   out.append("... {} additional flagged objects omitted by report safety limit.".format(hidden))
 out.extend([
  "",
  "NOTES",
  "-" * 78,
  "- A class listed here is merely used by scanned drawing objects. V1.2 does not claim a class is empty or safe to delete.",
  "- Groups are traversed, but symbol definitions and generated PIO internals are not. This avoids double-counting resource internals as drawing geometry.",
  "- Large filled objects can be completely legitimate. They are surfaced because imported CAD frequently converts wide polylines or hatches into surprising filled geometry.",
  "- Spatial outliers are based on each layer's median object center, not the Vectorworks internal origin alone.",
  "- Geometry heuristics are evaluated per layer so sheet/design layer scales and unrelated coordinate systems do not contaminate each other.",
  "",
  "END REPORT",
  "=" * 78,
 ])
 return "\n".join(out)
def compact_summary(scan_result, analysis):
 lines = [
  "DOOM HAS REVIEWED THE REALM.",
  "",
  "Scope: {}".format(scope_text(scan_result["scope"])),
  "Objects scanned: {}".format(len(scan_result["items"])),
  "Layers scanned: {}".format(len(scan_result["layers"])),
  "Classes encountered: {}".format(len(analysis["class_counts"])),
  "",
  "Flagged objects: {}".format(len(analysis["flagged"])),
  "DOOM DEMANDS ATTENTION: {}".format(analysis["severity_counts"].get("DOOM", 0)),
  "Suspicious: {}".format(analysis["severity_counts"].get("SUSPICIOUS", 0)),
 ]
 if analysis["flag_counts"]:
  lines.append("")
  lines.append("Most common offenses:")
  for code, count in analysis["flag_counts"].most_common(4):
   lines.append("  {} x {}".format(count, code))
 else:
  lines.extend(["", "No immediate geometric offenses were detected."])
 if analysis["flagged"]:
  lines.append("")
  lines.append("Preview:")
  for item in analysis["flagged"][:MAX_PREVIEW_ITEMS]:
   labels = ", ".join(flag[0] for flag in item["flags"])
   lines.append("  - {} / {} / {}".format(item["layer"], item["class"], labels))
  extra = len(analysis["flagged"]) - MAX_PREVIEW_ITEMS
  if extra > 0:
   lines.append("  - ...and {} more".format(extra))
 return "\n".join(lines)
def save_report(report_text, scope):
 suggested = "DR_DOOM_v{}_{}.txt".format(
  VERSION.replace(".", "_"),
  "ACTIVE_LAYER" if scope == "ACTIVE_LAYER" else "ENTIRE_DRAWING",
 )
 try:
  file_name = vs.PutFile("Save Dr. Doom forensic report:", suggested)
 except Exception as e:
  vs.AlrtDialog(TITLE + "\n\nSave dialog failed:\n{}".format(e))
  return False, ""
 try:
  cancelled = vs.DidCancel()
 except Exception:
  cancelled = not bool(file_name)
 if cancelled or not file_name:
  return False, ""
 try:
  vs.Close(file_name)
 except Exception:
  pass
 try:
  with open(file_name, "w", encoding="utf-8") as f:
   f.write(report_text)
  return True, file_name
 except Exception as e:
  vs.AlrtDialog(TITLE + "\n\nReport save failed:\n{}".format(e))
  return False, ""
def select_flagged(handles):
 try:
  vs.DSelectAll()
 except Exception:
  pass
 selected = 0
 failed = 0
 for h in handles:
  if not valid(h):
   failed += 1
   continue
  try:
   vs.SetSelect(h)
   selected += 1
  except Exception:
   failed += 1
 return selected, failed
def action_menu(summary, has_flags):
 # Custom result dialog keeps the joke AND the definition in each button.
 # IDs 1/2 are Vectorworks' default/cancel buttons.
 ID_ACRONYM = 4
 ID_SUMMARY = 5
 ID_SELECT = 10
 ID_DOOMBOT = 11
 state = {"action": "CANCEL"}
 try:
  dialog = vs.CreateLayout(
   "DR. DOOM v{}".format(VERSION),
   False,
   "SAVE THE PROPHECY - Save Report",
   "UNWORTHY - Cancel",
  )
  vs.CreateCenteredStaticText(
   dialog, ID_ACRONYM,
   "Drawing Review, Diagnostics, Organization & Object Manipulation", 78
  )
  vs.CreateStaticText(dialog, ID_SUMMARY, summary, 78)
  vs.CreatePushButton(
   dialog, ID_SELECT,
   "SELECT THE ACCUSED - Select Flagged Objects for Inspection"
  )
  vs.CreatePushButton(
   dialog, ID_DOOMBOT,
   "DEPLOY DOOMBOT - Repair / Normalize Flagged Objects"
  )
  vs.SetFirstLayoutItem(dialog, ID_ACRONYM)
  vs.SetBelowItem(dialog, ID_ACRONYM, ID_SUMMARY, 0, 8)
  vs.SetBelowItem(dialog, ID_SUMMARY, ID_SELECT, 0, 10)
  vs.SetBelowItem(dialog, ID_SELECT, ID_DOOMBOT, 0, 4)
  def handler(item, data):
   if item == 12255:
    try:
     vs.SetStaticTextStyle(dialog, ID_ACRONYM, 1)
     vs.EnableItem(dialog, ID_SELECT, bool(has_flags))
     vs.EnableItem(dialog, ID_DOOMBOT, bool(has_flags))
    except Exception:
     pass
   elif item == ID_SELECT and has_flags:
    state["action"] = "SELECT"
    return 1
   elif item == ID_DOOMBOT and has_flags:
    state["action"] = "DOOMBOT"
    return 1
   elif item == 1:
    state["action"] = "SAVE"
   elif item == 2:
    state["action"] = "CANCEL"
   return item
  result = vs.RunLayoutDialog(dialog, handler)
  if result == 2:
   return "CANCEL"
  return state["action"]
 except Exception as e:
  vs.AlrtDialog(
   TITLE + "\n\nAction menu failed:\n{}\n\nNo changes were made.".format(e)
  )
  return "CANCEL"
def repairable_lineweight_items(analysis):
 repairable = []
 for item in analysis["flagged"]:
  for code, _label, _severity in item["flags"]:
   if code == "HEAVY_LINEWEIGHT":
    repairable.append(item)
    break
 return repairable
def doombot_choose_mode(repairable):
 question = (
  "DOOMBOT REPAIR PROTOCOL\n\n"
  "{} excessive-lineweight object(s) are repairable.\n\n"
  "Choose a normalization method.".format(len(repairable))
 )
 advice = (
  "BY CLASS - Use each object's class lineweight.\n"
  "SET EXPLICIT WEIGHT - Apply one chosen lineweight in mils.\n"
  "UNWORTHY - Cancel without changes."
 )
 try:
  result = vs.AlertQuestion(
   question,
   advice,
   1,
   "BY CLASS",
   "UNWORTHY",
   "SET EXPLICIT WEIGHT",
   "",
  )
 except Exception as e:
  vs.AlrtDialog(TITLE + "\n\nDOOMBOT mode dialog failed:\n{}".format(e))
  return None
 if result == 1:
  return {"mode": "BY_CLASS", "target": None}
 if result == 2:
  try:
   value = vs.StrDialog(
    "DOOMBOT EXPLICIT LINEWEIGHT\n\n"
    "Enter target lineweight in mils (1-255).",
    "10",
   )
  except Exception as e:
   vs.AlrtDialog(TITLE + "\n\nLineweight dialog failed:\n{}".format(e))
   return None
  try:
   if vs.DidCancel():
    return None
  except Exception:
   pass
  try:
   target = int(str(value).strip())
  except Exception:
   target = 0
  if target < 1 or target > 255:
   vs.AlrtDialog(
    TITLE + "\n\n"
    "DOOM REQUIRES A VALID LINEWEIGHT.\n\n"
    "Enter an integer from 1 through 255 mils. No changes were made."
   )
   return None
  return {"mode": "EXPLICIT", "target": target}
 return None
def lineweight_distribution(items):
 counts = Counter()
 for item in items:
  lw = item.get("lineweight")
  if lw is not None:
   counts[int(lw)] += 1
 return counts
def doombot_preview(repairable, plan):
 dist = lineweight_distribution(repairable)
 before = ", ".join(
  "{} x {} mil".format(count, lw)
  for lw, count in sorted(dist.items(), key=lambda kv: (-kv[1], kv[0]))[:6]
 ) or "<unavailable>"
 if plan["mode"] == "BY_CLASS":
  target_text = "Each object's class lineweight"
 else:
  target_text = "{} mils".format(plan["target"])
 question = (
  "DOOMBOT IS ARMED.\n\n"
  "Repairable objects: {}\n"
  "Current lineweights: {}\n"
  "Target: {}\n\n"
  "Apply these repairs?".format(len(repairable), before, target_text)
 )
 advice = (
  "Changes lineweight attributes only.\n"
  "It does not delete, move, reshape, convert, purge, or reclass objects.\n"
  "Every attempted repair is verified afterward."
 )
 try:
  result = vs.AlertQuestion(
   question,
   advice,
   1,
   "DOOM SUFFERS NO FOOLS",
   "UNWORTHY",
   "",
   "",
  )
 except Exception as e:
  vs.AlrtDialog(TITLE + "\n\nDOOMBOT confirmation failed:\n{}".format(e))
  return False
 return result == 1
def deploy_doombot(analysis):
 repairable = repairable_lineweight_items(analysis)
 if not repairable:
  vs.AlrtDialog(
   TITLE + "\n\n"
   "DOOMBOT FINDS NO REPAIRABLE OFFENSES.\n\n"
   "Doombot repairs excessive lineweights only."
  )
  return None
 plan = doombot_choose_mode(repairable)
 if plan is None:
  return None
 if not doombot_preview(repairable, plan):
  return None
 try:
  vs.NameUndoEvent("DR. DOOM - DEPLOY DOOMBOT")
 except Exception:
  pass
 attempted = 0
 verified = 0
 failed = 0
 still_heavy = 0
 for item in repairable:
  h = item["h"]
  if not valid(h):
   failed += 1
   continue
  attempted += 1
  try:
   if plan["mode"] == "BY_CLASS":
    vs.SetLWByClass(h)
   else:
    vs.SetLW(h, int(plan["target"]))
  except Exception:
   failed += 1
   continue
  try:
   actual = int(vs.GetLW(h))
  except Exception:
   actual = None
  try:
   if plan["mode"] == "BY_CLASS":
    applied_ok = bool(vs.IsLWByClass(h))
   else:
    applied_ok = (actual == int(plan["target"]))
  except Exception:
   applied_ok = False
  if applied_ok:
   verified += 1
  else:
   failed += 1
  if actual is not None and actual >= HEAVY_LINEWEIGHT_MILS:
   still_heavy += 1
 try:
  vs.ReDrawAll()
 except Exception:
  try:
   vs.Redraw()
  except Exception:
   pass
 lines = [
  "DOOMBOT REPORTS.",
  "",
  "Repairs attempted: {}".format(attempted),
  "Repairs verified: {}".format(verified),
  "Verification failures: {}".format(failed),
  "Still at or above Doom threshold: {}".format(still_heavy),
 ]
 if plan["mode"] == "BY_CLASS" and still_heavy:
  lines.extend([
   "",
   "Some class lineweights are themselves still heavy.",
   "Doom changed those objects to By Class as ordered; the class attributes may require review.",
  ])
 elif failed == 0 and still_heavy == 0:
  lines.extend([
   "",
   "DOOMBOT HAS COMPLETED ITS TASK.",
   "No repaired object remains condemned for excessive lineweight.",
  ])
 vs.AlrtDialog(TITLE + "\n\n" + "\n".join(lines))
 return {
  "attempted": attempted,
  "verified": verified,
  "failed": failed,
  "still_heavy": still_heavy,
  "mode": plan["mode"],
  "target": plan["target"],
 }
def main():
 scope = choose_scope()
 if scope is None:
  return
 scan_result = scan(scope)
 if not scan_result["layers"]:
  vs.AlrtDialog(
   TITLE + "\n\n"
   "Doom found no layers to scan. No changes were made."
  )
  return
 analysis = analyze(scan_result)
 report_text = build_report(scan_result, analysis)
 summary = compact_summary(scan_result, analysis)
 while True:
  action = action_menu(summary, bool(analysis["flagged"]))
  if action == "CANCEL":
   return
  if action == "SAVE":
   saved, saved_path = save_report(report_text, scope)
   if saved:
    vs.AlrtDialog(
     TITLE + "\n\n"
     "THE PROPHECY HAS BEEN PRESERVED.\n\n{}".format(saved_path)
    )
   else:
    vs.AlrtDialog(
     TITLE + "\n\n"
     "The report was not saved. No drawing changes were made."
    )
   continue
  if action == "SELECT":
   selected, select_failed = select_flagged(analysis["selection_handles"])
   lines = [
    "THE ACCUSED HAVE BEEN MARKED.",
    "",
    "Review objects selected: {}".format(selected),
   ]
   if select_failed:
    lines.append("Selection failures: {}".format(select_failed))
   vs.AlrtDialog(TITLE + "\n\n" + "\n".join(lines))
   return
  if action == "DOOMBOT":
   result = deploy_doombot(analysis)
   if result is None:
    continue
   scan_result = scan(scope)
   analysis = analyze(scan_result)
   report_text = build_report(scan_result, analysis)
   summary = compact_summary(scan_result, analysis)
   vs.AlrtDialog(
    TITLE + "\n\n"
    "DR. DOOM HAS RE-INSPECTED THE REALM.\n\n"
    "Flagged objects now: {}\n"
    "DOOM DEMANDS ATTENTION: {}\n"
    "Suspicious: {}".format(
     len(analysis["flagged"]),
     analysis["severity_counts"].get("DOOM", 0),
     analysis["severity_counts"].get("SUSPICIOUS", 0),
    )
   )
   continue
try:
 main()
except Exception as e:
 try:
  vs.AlrtDialog(
   "VWX FAILS - DR. DOOM v{}\n\n"
   "DOOM HAS ENCOUNTERED AN UNWORTHY EXCEPTION.\n\n{}".format(VERSION, e)
  )
 except Exception:
  pass
