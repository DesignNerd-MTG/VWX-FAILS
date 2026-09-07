# 99 CHUCKLES NOTES v1.0.3
# Self-contained: no network access or separate README file.

import vs


DIALOG_TITLE = "CHUCKLES NOTES - VWX FAILS QUICK REFERENCE"
TEXT_WIDTH_CHARS = 104
TEXT_HEIGHT_LINES = 36
TEXT_CONTROL_ID = 4


# ============================================================================
# BEGIN EMBEDDED ABRIDGED README
# Update this block whenever the canonical Git README changes.
# ============================================================================

NOTES_TEXT = r"""VWX FAILS — CHUCKLES NOTES
QUICK REFERENCE FOR VECTORWORKS FIXES, AUTOMATION, INSPECTION & LIBRARY SCRIPTS

Package date: 2026-09-07
vibed by Chuckles

===============================================================================
WHAT THIS IS
===============================================================================

This is the abridged, in-Vectorworks field guide for the VWX FAILS script shelf.
It covers what each tool does, how to start it, and the warnings most likely to
save your ass.

The full README in the Git repository remains the exhaustive manual:
DesignNerd-MTG/VWX-FAILS

SCRIPT ORDER

1  RESOURCE AUDITOR
2  MINDREADER
3  MINDREADER ACCESSORY AUTOPSY
4  HYPERLINK REBUILDER
5  STIRRUP HANGER INSERTION TRICK
6  FIXTURE TYPE TO NEW LAYER
7  LIGHTING DEVICE ATTRIBUTES
8  DR. DOOM
9  PICK A UNIT! ANY UNIT!
10 F.I.N.G.
99 CHUCKLES NOTES


GENERAL USE / INSTALLATION
--------------------------

These are Python scripts intended to run inside Vectorworks.

SCRIPT RESOURCE
Keep a script palette in a VWX library/template file and paste the matching
script into each script resource.

MENU COMMAND PLUG-IN
Create a menu-command plug-in in Plug-in Manager, paste the script into its
script editor, and add the command to the desired workspace.

The .py file is canonical source code. A script resource or plug-in is a
deployed copy. Updating the .py file does not automatically update a deployed
copy already inside Vectorworks.

Test any resource-changing or geometry-changing tool on a duplicate when using
it in an unfamiliar file.


===============================================================================
1 RESOURCE AUDITOR — v2.7
===============================================================================

WHAT IT DOES
Checks Vectorworks resources for attached Record Formats.

MODE A — FIND / ADD RECORDS
Finds resources that qualify by one or more existing Record Formats and checks
whether they also contain one or more required Record Formats.

Typical use:
Find Symbol Definitions containing Light Info Record but missing
EntEquipUniversal.

Basic workflow:
1. Choose FIND / ADD RECORDS.
2. Choose the resource type. Default 16 = Symbol Definition.
3. Enter qualifying Record Format name(s), separated by commas.
4. Enter required Record Format name(s).
5. If needed, choose whether qualifying records use ALL or ANY logic.
6. Review the audit.
7. Confirm before missing records are attached.
8. Review the verification result.

MODE B — COMPARE RECORD FIELDS
Lists one Record Format's fields or compares two Record Formats. This mode is
read only and is useful for diagnosing version-to-version field changes.

IMPORTANT
- It only attaches Record Formats already present in the current file.
- It does not invent Record Formats.
- It does not alter field values or symbol geometry.
- Referenced resources are skipped when they cannot be modified safely.


===============================================================================
2 MINDREADER — v5.0
===============================================================================

WHAT IT DOES
Universal read-only object inspector. Its central question is:

"What the hell does Vectorworks think this object actually is?"

It can report object type, name, class, bounds, center, parent/container chain,
symbol identity, parametric record, attached records and fields, exposed child
contents, embedded Symbol Definitions, and Lighting Device clues.

SELECTED DRAWING OBJECT
1. Select exactly one ordinary drawing object.
2. Run MINDREADER.
3. Choose SELECTED DRAWING OBJECT.
4. Review the summary and optionally save the full report.

OBJECT INSIDE A SYMBOL DEFINITION
Use this when Vectorworks will not expose a nested symbol-edit selection.
1. Run MINDREADER.
2. Choose OBJECT INSIDE A SYMBOL DEFINITION.
3. Enter the exact Symbol Definition name.
4. Optionally enter a filter such as Hyperlink, Lighting Device, or Parts.
5. Choose the listed object to inspect.
6. Review or save the report.

MINDREADER changes nothing.


===============================================================================
3 MINDREADER ACCESSORY AUTOPSY — v1.0
===============================================================================

WHAT IT DOES
Specialized read-only anatomy report for Spotlight Lighting Device accessories.

It inspects generated Static Accessory instances, parent/container
relationships, accessory symbols, transforms/orientation, Parts records,
Light Info Record, EntEquipUniversal, and exposed internal geometry.

WORKFLOW
1. Select exactly one Lighting Device containing the accessory.
2. Run MINDREADER ACCESSORY AUTOPSY.
3. Review the Static Accessory summary.
4. Optionally save the full anatomy report.

Use ordinary MINDREADER for general objects. Use AUTOPSY when the problem is
specifically accessory anatomy, Parts role, generated instances, orientation,
or Base-versus-Yoke behavior.

It changes nothing.


===============================================================================
4 HYPERLINK REBUILDER — v2.0
===============================================================================

WHAT IT DOES
Rebuilds Sheet Layer hyperlinks inside a named TOC Symbol Definition.

It can retarget existing sheet hyperlinks, duplicate a working hyperlink when
more are needed, delete excess sheet hyperlinks, preserve matching labels,
generate labels for new targets, reposition the list, preserve non-sheet
hyperlinks, and optionally reflow preserved non-sheet hyperlinks.

WORKFLOW
1. Run HYPERLINK REBUILDER.
2. Enter the exact TOC Symbol Definition name. Default: TOC BIG.
3. Choose Sheet Layers using entries such as 1,3,5-8.
4. Choose whether preserved non-sheet links should reflow.
5. Confirm X/Y spacing.
6. Review the preview.
7. Confirm before modification.

IMPORTANT
- The Symbol Definition must contain at least one working Sheet Layer
  hyperlink to use as a template.
- It edits the Symbol Definition, so every placed instance changes.
- It does not create or retarget PDF / Open Document links.
- Existing non-sheet hyperlinks are preserved.


===============================================================================
5 STIRRUP HANGER INSERTION TRICK — SHIT v1.3
===============================================================================

WHAT IT DOES
Works around the VW2026 Spotlight accessory-display conflict where:

- Parts.Yoke=True gives the desired 2D Top/Plan accessory appearance.
- Parts.Base=True gives the desired 3D hanging behavior.

Each supported physical item uses two resources:
- NORMAL accessory: clean name, Static Accessory, Parts.Yoke=True, normal 2D.
- Z-3D PROXY: name begins "Z-3D PROXY -", Static Accessory, Parts.Base=True,
  required 3D geometry.

WORKFLOW
1. Insert the NORMAL accessory.
2. If only 2D is needed, stop.
3. For 3D, select the Lighting Device(s) and run SHIT.
4. Review configured resources, selected fixture count, and warnings.
5. Continue. SHIT adds a missing matching proxy and leaves existing proxies
   alone.

CURRENT CONFIGURED PAIRS
- Telescoping Kellum 8-16 ft
- Telescoping Stirrup Hanger 2-6ft
- Telescoping Stirrup Hanger 4-8 ft
- Pantograph

Each maps to the same name prefixed with "Z-3D PROXY -".

IMPORTANT
- Selected Lighting Devices only.
- Single-cell Lighting Devices only; multi-cell fixtures are skipped.
- Every configured resource pair is validated before anything changes.
- A missing or malformed configured resource is a hard stop.
- It never intentionally adds the same proxy twice.
- It never deletes accessories or edits record values or symbol geometry.

ADDING HARDWARE
Create both required Symbol Definitions, then add one exact-name mapping to
ACCESSORY_TO_3D_PROXY in the canonical script. Resource names must match
exactly. Update the deployed script resource or plug-in afterward.


===============================================================================
6 FIXTURE TYPE TO NEW LAYER — v1.2
===============================================================================

WHAT IT DOES
Moves Lighting Devices to layers grouped by Instrument Type.

WORKFLOW
1. Select one or more Lighting Devices.
2. Run FIXTURE TYPE TO NEW LAYER.
3. Choose scope:
   - selected Lighting Devices only; or
   - selected devices as seed types, then all matching devices in the file.
4. Confirm the layer-name prefix. Default: LD - Type:
5. Review actual seed count, types, scope, and target count.
6. Confirm. The script creates or reuses one layer per Instrument Type.

IMPORTANT
- It moves Lighting Devices; it does not duplicate them.
- Existing layers with matching generated names are reused.
- Selection can span layers when Layer Options permit cross-layer editing.


===============================================================================
7 LIGHTING DEVICE ATTRIBUTES — v1.5
===============================================================================

WHAT IT DOES
Batch editor for Lighting Device highlighting and graphic attributes.

OPERATIONS
HIGHLIGHT SHADOW — default
Applies the standard VWX FAILS drop shadow while preserving symbol colors:
Offset 0.035", Blur 0.03", Angle 300 degrees, Opacity 85%, chosen shadow color.

REMOVE HIGHLIGHT SHADOW
Disables the native drop shadow on each target. This also removes any purposeful
drop shadow the device already had.

LEGACY: SET FILL / LINE WEIGHT
Changes selected object fill and/or lineweight. Displayed fill depends on
Spotlight's Modify Lighting Device Color > Object Attributes preference.

MAKE ATTRIBUTES BY CLASS
Returns fill color, fill pattern, pen color, lineweight, and line style to
By Class.

TARGET SCOPES
- Selected Lighting Devices.
- All devices matching selected Instrument Type(s).
- All devices matching selected value(s) from a chosen Lighting Device field.

IMPORTANT
- Begin with one or more selected Lighting Devices.
- Review the target count before confirming.
- Document-level Drop Shadows display must be enabled for highlights.
- Highlight Shadow does not alter records, classes, layers, Symbol Definitions,
  Spotlight color preferences, or colors inside the fixture symbol.


===============================================================================
8 DR. DOOM — v1.2
DRAWING REVIEW, DIAGNOSTICS, ORGANIZATION & OBJECT MANIPULATION
===============================================================================

WHAT IT DOES
Diagnosis-first drawing intake and cleanup inspector for the active layer or
entire drawing.

It reports object/layer/class/type counts, drawing extents, heavy lineweights,
extreme size outliers, unusually large filled objects, and spatial outliers.
Geometry heuristics are evaluated per layer.

ACTIONS
SAVE THE PROPHECY
Save Report

SELECT THE ACCUSED
Select Flagged Objects for Inspection

DEPLOY DOOMBOT
Repair / Normalize Flagged Objects

UNWORTHY
Cancel

DOOMBOT
In v1.2, DOOMBOT repairs excessive lineweight only. It can set repairable
objects By Class or apply one explicit lineweight. It previews the target count
and lineweight distribution, requires confirmation, verifies the repair, and
re-scans.

IMPORTANT
- Review flags are heuristics, not automatic guilt.
- It does not automatically delete, move, reshape, convert, purge, or reclass.
- Large fills, spatial outliers, and size outliers are reported but not repaired.
- Groups are traversed; Symbol Definitions and generated PIO internals are not
  recursively treated as ordinary drawing geometry.


===============================================================================
9 PICK A UNIT! ANY UNIT! — v1.0.2
===============================================================================

WHAT IT DOES
Fast Lighting Device selector using record parameters plus object Class and
Layer.

SELECTION MODES
- Single Parameter Selection.
- Multi-Parameter Selection with up to four criteria.
- Multi-parameter logic can MATCH ALL or MATCH ANY.

SELECTION ACTIONS
- Replace Selection.
- Add to Selection.
- Remove From Selection.

OPERATORS
Equals, Does Not Equal, Contains, Starts With, Is Blank, Is Not Blank.

FIELDS
Menus are built from Lighting Device fields present in the drawing. Common
fields are prioritized: Purpose, System, Position, Universe, Address, Channel,
Unit Number, Instrument Type, Focus, Color, Fixture Mode, Device Type, Circuit
Name/Number, and User Fields. Object Class and Layer are also available.

Existing Value menus list distinct non-blank values currently found in the
drawing.

IMPORTANT
PICK A UNIT! changes selection state only. It does not edit parameters, move
objects, change layers/classes, edit Symbol Definitions, or alter geometry.


===============================================================================
10 F.I.N.G. — v1.0
===============================================================================

WHAT IT DOES
Manual Vectorworks 2026 Update 6 inventory switcher. F.I.N.G. discovers the
inventory XML files in the Vectorworks inventory folder, shows which are
enabled, activates one chosen inventory, and disables the other discovered
inventories.

It can remember the chosen inventory in the current drawing using the
__FING_DOCUMENT_BINDING Record Format and its InventoryName field. REBIND
restores that saved choice when returning to the drawing.

WORKFLOW
1. Run F.I.N.G. after changing files and before inventory-dependent paperwork.
2. Choose the inventory that should be active.
3. Leave Remember this inventory for this file enabled when the drawing should
   retain that choice.
4. Click THIS IS MY INVENTORY.
5. Save the Vectorworks drawing if its document binding should persist.
6. When returning to the drawing, run F.I.N.G. and use REBIND to restore its
   remembered inventory.

IMPORTANT
- Inventory activation is global to Vectorworks, not isolated per open file.
- F.I.N.G. refreshes placed Summary Key objects in the drawing, including keys
  in groups and viewport annotations; Symbol Definitions are excluded.
- Before writing, it creates verified backups, checks that the inspected XML
  files have not changed, writes atomically, reads the result back, and attempts
  rollback if a batch write fails.
- It saves a last-run report in the Vectorworks user folder.
- UNASSOCIATED is deliberately disabled in v1.0 because native equipment
  source assignment has not been verified safely.
- It does not edit inventory quantities or equipment source assignments.
- Disk flags are verified, but visible Summary Key totals remain the final
  authoritative check.
- It refuses to run while the earlier live-test probe has an unfinished restore.


===============================================================================
99 CHUCKLES NOTES — v1.0.3
===============================================================================

WHAT IT DOES
Displays this abridged README inside Vectorworks in a scrollable window.

It contains no network access and requires no separate README file.

MAINTENANCE
Whenever the VWX FAILS package changes:
1. Update the full canonical README in the Git repository.
2. Update this abridged NOTES_TEXT block with the meaningful change.
3. Update versions and the package date here.
4. Update the deployed Script Resource or menu-command plug-in.

Editing text in this window does not change the script.


===============================================================================
VERSION LIST
===============================================================================

1  RESOURCE AUDITOR                         v2.7
2  MINDREADER                              v5.0
3  MINDREADER ACCESSORY AUTOPSY             v1.0
4  HYPERLINK REBUILDER                      v2.0
5  STIRRUP HANGER INSERTION TRICK           v1.3
6  FIXTURE TYPE TO NEW LAYER                v1.2
7  LIGHTING DEVICE ATTRIBUTES               v1.5
8  DR. DOOM                                 v1.2
9  PICK A UNIT! ANY UNIT!                   v1.0.2
10 F.I.N.G.                                 v1.0
99 CHUCKLES NOTES                           v1.0.3

VWX FAILS =
Vectorworks Fixes, Automation, Inspection & Library Scripts.
"""

# ============================================================================
# END EMBEDDED ABRIDGED README
# ============================================================================


def dialog_handler(item, data):
    """The dialog is informational; the CLOSE button ends it."""
    pass


def show_notes():
    dialog_id = vs.CreateLayout(DIALOG_TITLE, False, "CLOSE", "")

    if not dialog_id:
        vs.AlrtDialog("CHUCKLES NOTES could not create its dialog.")
        return

    # The Windows Vectorworks multiline control requires a CRLF pair.
    # LF alone and CR alone are both discarded, producing one giant paragraph.
    display_text = NOTES_TEXT.replace("\n", "\r\n")

    vs.CreateEditTextBox(
        dialog_id,
        TEXT_CONTROL_ID,
        display_text,
        TEXT_WIDTH_CHARS,
        TEXT_HEIGHT_LINES,
    )
    vs.SetFirstLayoutItem(dialog_id, TEXT_CONTROL_ID)
    vs.SetBelowItem(dialog_id, TEXT_CONTROL_ID, 1, 0, 0)
    vs.RunLayoutDialog(dialog_id, dialog_handler)


show_notes()
