VWX FAILS
VECTORWORKS FIXES, AUTOMATION, INSPECTION & LIBRARY SCRIPTS

Package date: 2026-09-07
vibed by Chuckles

========================================================================
WHAT THIS IS
========================================================================

VWX FAILS is a small collection of Vectorworks / Spotlight utilities built
to solve recurring workflow problems, inspect Vectorworks internals, repair
resource metadata, and automate repetitive drawing operations.

The ten scripts are numbered to match the working script palette / plug-in
order:

1 RESOURCE AUDITOR
2 MINDREADER
3 MINDREADER ACCESSORY AUTOPSY
4 HYPERLINK REBUILDER
5 STIRRUP HANGER INSERTION TRICK
6 FIXTURE TYPE TO NEW LAYER
7 LIGHTING DEVICE ATTRIBUTES
8 DR. DOOM
9 PICK A UNIT! ANY UNIT!
10 F.I.N.G.


GENERAL USE / INSTALLATION
--------------------------

These files contain Python code intended to run inside Vectorworks.

They can be maintained in two useful ways:

1. SCRIPT RESOURCE
   Keep a script palette in a VWX library/template file and paste the matching
   script into each resource.

2. MENU COMMAND PLUG-IN
   Create a menu-command plug-in in Plug-in Manager and paste the script into
   its script editor. Add the commands to the desired Vectorworks workspace.

The scripts themselves are the source-of-truth code. A plug-in is simply a
deployed copy of that code.

Always test resource-changing tools on a duplicate file when using them on a
new library or unfamiliar drawing.


========================================================================
1 RESOURCE AUDITOR
Version: v2.7
========================================================================

PURPOSE
-------

Resource Auditor checks Vectorworks resources for attached Record Formats.

It was originally developed to identify lighting-symbol resources that had
Light Info Record but were missing EntEquipUniversal, but the current version
is generic and can work with other resource types and Record Formats.

It has TWO modes:

A. FIND / ADD RECORDS
B. COMPARE RECORD FIELDS


A. FIND / ADD RECORDS
---------------------

Use this when a group of resources should contain a particular Record Format
and some resources may be missing it.

Typical example:

    Check Symbol Definitions that already contain:
        Light Info Record

    Make sure they also contain:
        EntEquipUniversal

WORKFLOW:

1. Run RESOURCE AUDITOR.
2. At the first question choose:
       NO = FIND / ADD RECORDS
3. The script first displays the Record Formats available in the current file.
4. Enter the Vectorworks resource type number to inspect.
       Default: 16 = Symbol Definition
       The prompt now includes a cheat sheet of common resource type numbers
       (symbols, worksheets, materials, records, hatches, textures, line types,
       styles, fills, and related definitions).
5. Enter the Record Format(s) a resource must already contain in order to
   qualify for inspection.
       Multiple names can be separated with commas.
       Leave blank to inspect every resource of that type.
6. Enter the Record Format(s) that qualifying resources must also contain.
7. If multiple qualifying records were entered, choose whether a resource must
   contain ALL or ANY of them.
8. Review the audit summary.
9. If records are missing, the script asks before adding them.
10. The script verifies the repair afterward.

IMPORTANT:

- It only attaches Record Formats that ALREADY EXIST in the current file.
- It will not invent or construct a missing Record Format.
- It does not alter record field values.
- It does not alter symbol geometry.
- Referenced resources are skipped when they cannot safely be modified.


B. COMPARE RECORD FIELDS
------------------------

Use this to inspect the fields inside one Record Format or compare two Record
Formats.

Useful for diagnosing record changes between Vectorworks versions.

WORKFLOW:

1. Run RESOURCE AUDITOR.
2. Choose:
       YES = COMPARE RECORD FIELDS
3. Enter the exact Record Format name to inspect.
4. Enter a second Record Format to compare against.
       OR leave the comparison name blank to simply list the first record's
       fields.
5. Review the report.

This mode is READ ONLY.


========================================================================
2 MINDREADER
Version: v5.0
========================================================================

PURPOSE
-------

MINDREADER is the universal Vectorworks object inspector.

Its basic question is:

    "What the hell does Vectorworks think this object actually is?"

It can report:

- Vectorworks object type
- object name and class
- bounding box and center
- parent/container chain
- symbol identity and Symbol Definition
- parametric/PON record
- every attached record
- every record field, field type, and current value
- child/generated contents exposed by Vectorworks
- embedded Symbol Definitions
- Lighting Device / Parts / Light Info / EntEquip clues when applicable

MINDREADER is READ ONLY.


TWO TARGET MODES
----------------

Vectorworks does not reliably expose nested symbol-edit selections through the
normal layer-selection API, so MINDREADER intentionally has two target modes.

A. SELECTED DRAWING OBJECT
B. OBJECT INSIDE A SYMBOL DEFINITION


A. SELECTED DRAWING OBJECT
--------------------------

Use for ordinary objects on a Design Layer or Sheet Layer.

1. Select ONE object.
2. Run MINDREADER.
3. At the first dialog choose:
       NO = SELECTED DRAWING OBJECT
4. Review the short summary.
5. Choose whether to save the full report.

The report is saved as a text file.


B. OBJECT INSIDE A SYMBOL DEFINITION
------------------------------------

Use when the object you want to inspect lives inside a Symbol Definition and
Vectorworks' normal selected-object functions cannot see it correctly.

Example:
A Hyperlink object inside the TOC BIG symbol.

1. Run MINDREADER.
2. Choose:
       YES = OBJECT INSIDE A SYMBOL DEFINITION
3. Enter the exact Symbol Definition name.
4. Optionally enter a filter such as:
       Hyperlink
       Lighting Device
       Parts
       Labels- Tags
5. MINDREADER lists matching objects inside that definition.
6. Enter the number of the object to inspect.
7. Review/save the full report.

This symbol-browser approach is intentionally explicit and avoids unsafe or
unreliable interactive-selection tricks.


========================================================================
3 MINDREADER ACCESSORY AUTOPSY
Version: v1.0
========================================================================

PURPOSE
-------

Accessory Autopsy is a specialized, deeper MINDREADER diagnostic for Spotlight
Lighting Device accessories.

It was created while diagnosing the Vectorworks 2026 Base-vs-Yoke accessory
behavior that led to SHIT.

It inspects:

- generated Static Accessory instances
- parent/container relationships
- accessory symbol identity
- transformations/orientation data
- accessory Symbol Definitions
- Parts records
- Light Info Record
- EntEquipUniversal
- internal accessory geometry exposed by Vectorworks

It is READ ONLY.


WHEN TO USE IT
--------------

Use ordinary MINDREADER first for general object questions.

Use ACCESSORY AUTOPSY when the specific question is about an accessory's
internal anatomy, Parts role, generated instance, orientation, or Base/Yoke
behavior.


WORKFLOW
--------

1. Select exactly ONE Lighting Device containing the accessory you want to
   investigate.
2. Run MINDREADER ACCESSORY AUTOPSY.
3. The summary lists Static Accessory instances found.
4. Choose whether to save the full anatomy report.

It changes nothing in the drawing.


========================================================================
4 HYPERLINK REBUILDER
Version: v2.0
========================================================================

PURPOSE
-------

Hyperlink Rebuilder rebuilds Sheet Layer hyperlinks inside a named TOC Symbol
Definition.

It was created for a Table-of-Contents symbol containing Hyperlink CW objects.

It DOES NOT depend on selecting individual hyperlinks inside symbol-edit mode.


WHAT IT CHANGES
---------------

It manages hyperlinks whose function is:

    Activate Sheet Layer

It can:

- retarget existing Sheet Layer hyperlinks
- duplicate a working Sheet Layer hyperlink when more links are needed
- delete excess Sheet Layer hyperlinks when fewer links are needed
- preserve existing labels when an existing target still matches
- generate labels for new sheet targets from the Sheet Layer name
- reposition the rebuilt list using a configurable X/Y spacing
- preserve non-sheet hyperlinks such as existing PDF/web links
- optionally reflow preserved non-sheet hyperlinks after the Sheet Layer list


IMPORTANT LIMITATION
--------------------

This version DOES NOT create or retarget new PDF / Open Document links.

Existing non-sheet hyperlinks are preserved.

A future PDF-link builder should only be added after the exact VW26 fields of
a known-good Open Document hyperlink have been inspected.


REQUIREMENTS
------------

The target Symbol Definition must already contain at least ONE working
Sheet Layer Hyperlink. That existing hyperlink is used as the visual/template
object for any new links the script needs to create.


WORKFLOW
--------

1. Run HYPERLINK REBUILDER.
2. Enter the exact TOC Symbol Definition name.
       Default: TOC BIG
3. The script finds hyperlinks directly inside that Symbol Definition.
4. Choose the Sheet Layers to include by number.

   Examples:
       1,3,5
       1-8
       1,3,5-8

5. If non-sheet hyperlinks exist, choose whether:
       YES = reflow them immediately after the sheet links
       NO  = leave them exactly where they currently are
6. Review/change horizontal and vertical spacing.
7. Review the complete preview.
8. Confirm before the resource is modified.

IMPORTANT:

This edits the SYMBOL DEFINITION, not merely one placed symbol instance.
Every instance of that symbol therefore reflects the rebuilt hyperlinks.

For a newly developed TOC symbol, test on a duplicate before committing.


========================================================================
5 STIRRUP HANGER INSERTION TRICK
Version: v1.3
SHIT
========================================================================

PURPOSE
-------

SHIT is a workaround for a Vectorworks 2026 Spotlight accessory-display bug.

The specific problem discovered during testing:

- A Static Accessory using Parts.Base=True gives correct 3D hanging behavior,
  but its normal 2D Top/Plan representation is suppressed.
- A Static Accessory using Parts.Yoke=True displays correctly in Top/Plan,
  but does not provide the desired 3D hanging behavior for this hardware.

SHIT solves this by splitting ONE piece of physical hanging hardware into TWO
Vectorworks accessory resources:

1. NORMAL ACCESSORY
   - clean human-facing name
   - Static Accessory
   - Parts.Yoke=True
   - contains the normal 2D drafting representation
   - this is the accessory the user inserts normally

2. Z-3D PROXY ACCESSORY
   - name begins with:
         Z-3D PROXY -
   - Static Accessory
   - Parts.Base=True
   - contains the 3D geometry needed for the correct hanging behavior
   - SHIT adds this companion automatically when needed


NORMAL HUMAN WORKFLOW
---------------------

1. Insert the NORMAL accessory on the Lighting Device.
2. If the drawing only needs 2D:
       STOP.
   Nothing else is necessary.
3. If correct 3D hanging geometry is needed:
       select the Lighting Device(s)
       run SHIT
4. SHIT first displays:
       - every currently configured normal accessory
       - the number of selected Lighting Devices
       - warnings for known unsupported / unsafe states
5. Review the opening summary and choose whether to continue.
6. SHIT looks for configured normal accessories already attached to each
   selected Lighting Device.
7. If it finds a configured normal accessory and the matching Z-3D PROXY is
   missing, SHIT adds the proxy.
8. If the proxy is already attached, SHIT leaves it alone.

The normal accessory handles 2D drafting.
The Z-3D PROXY handles the 3D hanging behavior.


V1.3 STARTUP WARNINGS
---------------------

SHIT v1.3 exposes the important Vectorworks landmines before it changes
anything.

On launch it lists the configured accessory names so the user does not need to
open the code merely to remember what SHIT currently supports.

It also reports warning conditions that are already known to matter:

- configured normal accessory resource missing
- configured Z-3D PROXY resource missing
- normal resource is not Static Accessory
- proxy resource is not Static Accessory
- normal resource is not Parts.Yoke=True
- proxy resource is not Parts.Base=True
- no Lighting Devices selected
- selected Lighting Devices that are multi-cell or fail the single-cell check

Configuration/resource failures are HARD STOPS: nothing is changed.

Multi-cell selected fixtures are warnings only. They remain selected, but SHIT
skips them during processing because v1.3 is still single-cell only.

When configuration is healthy, the opening screen remains intentionally simple:
configured accessories, selected Lighting Device count, any applicable warning,
and Continue?


CURRENT CONFIGURED PAIRS
------------------------

The current script contains:

    "Telescoping Kellum 8-16 ft"
        -> "Z-3D PROXY - Telescoping Kellum 8-16 ft"

    "Telescoping Stirrup Hanger 2-6ft"
        -> "Z-3D PROXY - Telescoping Stirrup Hanger 2-6ft"

    "Telescoping Stirrup Hanger 4-8 ft"
        -> "Z-3D PROXY - Telescoping Stirrup Hanger 4-8 ft"

    "Pantograph"
        -> "Z-3D PROXY - Pantograph"


SAFETY / LIMITATIONS
--------------------

- Selected Lighting Devices only.
- Current version supports SINGLE-CELL Lighting Devices only.
- It never intentionally adds the same 3D companion twice.
- It never deletes accessories.
- It never edits accessory symbol geometry.
- It never edits record values.
- It validates every configured resource pair before modifying a fixture.
- If ANY configured resource is missing or malformed, preflight fails and
  nothing is changed.


ADDING A NEW HARDWARE TYPE
--------------------------

THIS REQUIRES TWO RESOURCE SYMBOLS AND ONE CODE ENTRY.


STEP 1 - BUILD / PREPARE THE NORMAL ACCESSORY

Create or prepare the accessory that users will actually see and insert.

Requirements:

- exact desired human-facing resource name
- Light Info Record:
      Device Type = Static Accessory
- Parts record:
      Yoke = True
- use the geometry needed for the normal Top/Plan representation
- this is the CLEAN name; it should NOT be named Z-3D PROXY


STEP 2 - BUILD / PREPARE THE 3D COMPANION

Create a second accessory resource.

Recommended naming convention:

    Z-3D PROXY - <NORMAL ACCESSORY NAME>

Requirements:

- Light Info Record:
      Device Type = Static Accessory
- Parts record:
      Base = True
- contains the 3D geometry required for correct hanging behavior
- should not be used as the normal manually inserted accessory


STEP 3 - ADD THE PAIR TO THE SCRIPT

Open:

    5 STIRRUP HANGER INSERTION TRICK.py

Near the beginning of the script find:

    ACCESSORY_TO_3D_PROXY = {

Inside that dictionary add ONE mapping:

    "NORMAL ACCESSORY EXACT RESOURCE NAME":
        "Z-3D PROXY - EXACT RESOURCE NAME",

For example, if adding a new hardware resource called:

    Motorized Stirrup Hanger

and its companion is:

    Z-3D PROXY - Motorized Stirrup Hanger

the dictionary would contain:

    ACCESSORY_TO_3D_PROXY = {
        "Telescoping Kellum 8-16 ft":
            "Z-3D PROXY - Telescoping Kellum 8-16 ft",

        "Telescoping Stirrup Hanger 2-6ft":
            "Z-3D PROXY - Telescoping Stirrup Hanger 2-6ft",

        "Telescoping Stirrup Hanger 4-8 ft":
            "Z-3D PROXY - Telescoping Stirrup Hanger 4-8 ft",

        "Pantograph":
            "Z-3D PROXY - Pantograph",

        "Motorized Stirrup Hanger":
            "Z-3D PROXY - Motorized Stirrup Hanger",
    }


STEP 4 - NAMES MUST MATCH EXACTLY

The strings in ACCESSORY_TO_3D_PROXY are Vectorworks RESOURCE NAMES.

They are not descriptions.

They are not Instrument Type values.

They must exactly match the Symbol Definition names in the current VWX file,
including spaces, hyphens, and capitalization.


STEP 5 - BOTH RESOURCES MUST EXIST

Do not add the code mapping before both Symbol Definitions exist in the file.

When SHIT runs, its preflight checks:

NORMAL accessory:
- resource exists
- Device Type is Static Accessory
- Parts.Yoke=True

3D companion:
- resource exists
- Device Type is Static Accessory
- Parts.Base=True

If a configured pair fails validation, SHIT reports the failure and changes
nothing.


STEP 6 - TEST THE NEW PAIR

Recommended test:

1. Duplicate a test file.
2. Attach only the NORMAL accessory to one single-cell Lighting Device.
3. Verify the 2D Top/Plan appearance.
4. Select the Lighting Device.
5. Run SHIT.
6. Confirm the report says the 3D companion was added.
7. Verify:
       - 2D still uses the normal accessory appearance
       - 3D now uses the desired hanging behavior
8. Run SHIT a second time.
9. Confirm it reports the companion is already present rather than adding a
   duplicate.


IMPORTANT SOURCE-OF-TRUTH NOTE
------------------------------

If the script is also installed as a Plug-in Manager command, changing only
the .py file in a library does NOT automatically change the code already
embedded in an installed plug-in.

After adding a new ACCESSORY_TO_3D_PROXY pair, update whichever deployed copy
is actually being run.

Recommended practice:

- canonical code lives in the VWX FAILS script library
- plug-in versions are deployed copies
- after editing the canonical script, paste/update that same code in the
  installed menu-command plug-in


========================================================================
6 FIXTURE TYPE TO NEW LAYER
Version: v1.2
========================================================================

PURPOSE
-------

Moves Lighting Devices to layers grouped by Instrument Type.

It is useful when a drawing needs separate Lighting Device layers for each
fixture type.


WORKFLOW
--------

1. Select one or more Lighting Devices.
2. Run FIXTURE TYPE TO NEW LAYER.
3. Choose scope:

       YES = move ONLY the currently selected Lighting Devices

       NO  = use the selected Lighting Devices as seed Instrument Types,
             then find ALL Lighting Devices in the file with those same types

   V1.2 walks Vectorworks' selected-object chain separately on every layer.
   This supports fixtures selected on non-active layers when Layer Options
   permit cross-layer editing, while still avoiding the stale global SEL=TRUE
   behavior that caused false seed fixtures.

4. Enter/confirm the desired layer-name prefix.
       Default:
           LD - Type:
5. Review the confirmation dialog. It shows the actual seed count, seed
   Instrument Type(s), scope, and target fixture count before anything moves.
6. The script creates or reuses one layer per Instrument Type.
7. Matching Lighting Devices are moved to those layers.
8. A summary reports the layers used and fixture count per type.


EXAMPLE
-------

Selected seed fixtures:

    ETC Source 4 LED Series 3
    ARRI SkyPanel S60-C

With the default prefix the script can create/reuse:

    LD - Type: ETC Source 4 LED Series 3
    LD - Type: ARRI SkyPanel S60-C


IMPORTANT
---------

This tool MOVES Lighting Device objects between layers.

It does not duplicate them.

Existing layers with matching generated names are reused.


========================================================================
7 LIGHTING DEVICE ATTRIBUTES
Version: v1.5
========================================================================

PURPOSE
-------

Batch editor for Lighting Device highlighting and graphic attributes.

The default workflow is a non-destructive visual highlight that preserves the
fixture symbol's own colors. This matters when symbol color already carries
useful information such as bi-color vs full-color, RGB vs RGBA, or other
fixture distinctions.


OPERATIONS
----------

A. HIGHLIGHT SHADOW (PRESERVES SYMBOL COLORS)

This is the DEFAULT operation.

It applies a compact native Vectorworks drop shadow to every target Lighting
Device while leaving the actual Lighting Device symbol geometry unchanged.

The VWX FAILS highlight recipe is fixed for consistency on dense plots:

    Offset:   0.035"
    Blur:     0.03"
    Angle:    300 degrees
    Opacity:  85%
    Color:    chosen with Drop Shadow Color

Every target receives the SAME normalized highlight recipe. Existing object
shadow settings are ignored so old or inconsistent drop-shadow data cannot
change the result from fixture to fixture.

The script uses a confirmed Vectorworks Python distance compensation of 25.4
for the shadow Offset and Blur setter so the values displayed in Vectorworks
land at the intended 0.035" / 0.03".

This operation does NOT require:

    Spotlight Preferences
    > Modify lighting device color
    > Object attributes

For the shadow to be visible, Vectorworks' document-level Drop shadows display
preference must be enabled. If it is off, the script stops and tells the user
instead of silently changing a document preference.


B. REMOVE HIGHLIGHT SHADOW

Disables the native drop shadow on every target Lighting Device.

NOTE:
If a Lighting Device was already using a purposeful drop shadow before this
workflow, Remove Highlight Shadow will disable that shadow too. Lighting
Devices normally do not use purposeful drop shadows, but be aware of it.


C. LEGACY: SET FILL / LINE WEIGHT

The original object-attribute workflow remains available when intentionally
wanted.

Legacy controls are separate from the Drop Shadow controls:

- Change fill color
- Fill Color
- Force solid fill
- Change line weight
- Line Weight

For fill color to display on Lighting Device geometry, Spotlight must use:

    Spotlight Preferences
    > Lighting Devices
    > Classes and Color
    > Modify lighting device color
    > Object attributes

That is a global Spotlight display behavior and can override intentional color
inside Lighting Device symbols. For that reason this mode is labeled LEGACY
and is not the default workflow.


D. MAKE ATTRIBUTES BY CLASS

Returns these Lighting Device object attributes to By Class control:

- fill color
- fill pattern
- pen color
- line weight
- line style


REQUIRED SEED SELECTION
-----------------------

Begin by selecting one or more Lighting Devices.

Selection works across drawing layers, including fixtures selected on a
non-active layer when Layer Options permit cross-layer editing.

The selected Lighting Devices are either:

- the actual target objects
OR
- seed objects whose Instrument Type or chosen field value determines the
  larger target set.


APPLY-TO SCOPES
---------------

1. SELECTED LIGHTING DEVICES

Only the currently selected Lighting Devices are changed.


2. ALL MATCHING INSTRUMENT TYPE(S)

The selected Lighting Devices are seed objects.

Example:

Select one SkyPanel S60-C and one ETC Source 4.

The script derives those selected Instrument Type values and applies the chosen
operation to every Lighting Device matching either type.


3. ALL MATCHING SELECTED FIELD VALUE(S)

Choose any available Lighting Device record field.

The selected fixture(s) provide the value(s) to match.

Example:

    Selected fixture:
        Purpose = HB

    Apply to:
        All matching selected field value(s)

    Match field:
        Purpose

Result:

Every Lighting Device whose Purpose is HB becomes a target.

The Match Field control is disabled unless this scope is selected.

When field matching is active, the dialog also displays:

    Selected value(s): HB

so the user can see exactly which selected value(s) will be used before
applying the operation.

If multiple selected seed fixtures contain different non-blank values in the
chosen field, all of those values are used as matches.

Blank seed values are ignored.


DROP SHADOW COLOR
-----------------

Highlight Shadow has its own dedicated Drop Shadow Color picker.

This is separate from the Legacy Fill Color control.

The default highlight color is magenta, but any Vectorworks document color can
be selected.


CONFIRMATION
------------

Before applying changes, the tool displays:

- number of selected seed fixtures
- chosen operation
- chosen scope
- match criteria
- total target count
- what the chosen operation will do
- the compact highlight recipe when Highlight Shadow is selected

Always review the TARGET COUNT before confirming, especially when matching by
a generic field such as Purpose, Position, System, or a User Field.


WHAT IT DOES NOT CHANGE
-----------------------

Highlight Shadow does not alter:

- Lighting Device record values
- fixture classes
- fixture layers
- Symbol Definitions
- Spotlight's Modify lighting device color preference
- the native colors inside the Lighting Device symbol

The Legacy operation changes only the Lighting Device object's graphic
attributes; it does not change record values, layers, classes, or Symbol
Definitions.



========================================================================
8 DR. DOOM
Version: v1.2
Drawing Review, Diagnostics, Organization & Object Manipulation
========================================================================

PURPOSE
-------

DR. DOOM is a diagnosis-first drawing intake / cleanup inspector.

It can scan either the ACTIVE LAYER or the ENTIRE DRAWING and reports object,
layer, class, and type counts; drawing extents; unusually heavy lineweights;
extreme size outliers; unusually large filled objects; and spatial outliers.

Geometry heuristics are evaluated per layer so unrelated scales and coordinate
systems do not contaminate one another.

REVIEW HEURISTICS
-----------------

Heavy lineweight:
    >= 100 mils

Size outlier:
    >= 100x median object size on its layer
    Simple Line objects are excluded.

Large filled object:
    >= 5% of its layer's bounding-box area

Spatial outlier:
    >= 60% of its layer diagonal
    AND >= 100x layer median object size from the layer median center

These are review heuristics, not automatic guilt.

ACTIONS
-------

SAVE THE PROPHECY
    Save Report

SELECT THE ACCUSED
    Select Flagged Objects for Inspection

DEPLOY DOOMBOT
    Repair / Normalize Flagged Objects

UNWORTHY
    Cancel

DOOMBOT
-------

In v1.2, DOOMBOT repairs EXCESSIVE LINEWEIGHT only.

It can normalize repairable objects either:

    BY CLASS
        Set each object's lineweight to By Class.

    SET EXPLICIT WEIGHT
        Apply one chosen lineweight in mils.

Before changing anything, DOOMBOT previews the repairable object count, current
lineweight distribution, and target behavior, then requires explicit
confirmation.

Afterward it verifies every attempted repair and reports attempted, verified,
failed, and still-heavy objects. DR. DOOM then re-scans the selected scope.

SAFETY / LIMITATIONS
--------------------

DR. DOOM does not automatically delete, move, reshape, convert, purge, or
reclass objects.

Large filled objects, spatial outliers, and extreme-size findings are surfaced
for inspection but are not automatically repaired.

Groups are traversed. Symbol Definitions and generated PIO internals are not
recursively treated as ordinary drawing geometry.


========================================================================
9 PICK A UNIT! ANY UNIT!
Version: v1.0.2
Lighting Device Selector
========================================================================

PURPOSE
-------

PICK A UNIT! ANY UNIT! is a fast Lighting Device selector using Lighting
Device parameters plus object Class and Layer.

SELECTION MODES
---------------

SINGLE PARAMETER SELECTION
    Uses Parameter 1 only.

MULTI-PARAMETER SELECTION
    Uses up to four criteria.

Multi-Parameter logic can be:

    MATCH ALL PARAMETERS
    MATCH ANY PARAMETER

SELECTION ACTIONS
-----------------

REPLACE SELECTION
ADD TO SELECTION
REMOVE FROM SELECTION

MATCH OPERATORS
---------------

Equals
Does Not Equal
Contains
Starts With
Is Blank
Is Not Blank

FIELDS / PARAMETERS
-------------------

The field menus are built from Lighting Device parameters in the current
drawing. Frequently useful fields are prioritized, including Purpose, System,
Position, Universe, DMX Address / Address, Channel, Unit Number, Instrument
Type / Inst Type / Fixture Type, Focus / Focus Point, Color, Fixture Mode,
Device Type, Circuit Name, and Circuit Number.

User Fields remain available.

Two object-level choices are also included:

    Class (Object)
    Layer (Object)

EXISTING VALUES
---------------

For each selected parameter the tool reads distinct non-blank values currently
present on Lighting Devices in the drawing.

The Existing Value menu can populate the Value field instead of requiring
manual typing.

V1.0.2 FIX
----------

v1.0.2 corrected the Vectorworks pull-down selection getter by using
GetSelectedChoiceInfo for the currently selected item.

This restored correct field selection, Existing Value population, and field
validation.

The Field and Existing Value controls use standard Vectorworks pull-down menus
because CreatePullDownSearch did not reliably populate in the tested
Vectorworks 2026 environment.

WHAT IT CHANGES
---------------

PICK A UNIT! changes selection state only.

It does not move Lighting Devices, edit parameters, change layers or classes,
edit Symbol Definitions, or alter geometry.



========================================================================
10 F.I.N.G.
Version: v1.0
File Inventory Normalization Governor
========================================================================

PURPOSE
-------

F.I.N.G. is a manual Vectorworks inventory switcher for Vectorworks 2026
Update 6.

It was created to solve the problem of a drawing's Equipment Summary Keys
using the wrong Inventory when multiple custom inventory XML files are present.

The tested mechanism is Vectorworks' inventory XML Use flag:

    <IsUsedThisInventory>
        <Use>True</Use>
    </IsUsedThisInventory>

F.I.N.G. makes one chosen inventory active and sets the other discovered
inventory XML files inactive.

This is a MANUAL inventory switch.

It does not monitor document changes automatically.

Run F.I.N.G. after changing files and before issuing inventory-dependent
paperwork.


WHAT IT DOES
------------

F.I.N.G.:

- discovers inventory XML files in the Vectorworks inventory folder
- reads each inventory's current Use flag
- shows the currently enabled inventory file(s)
- lets the user choose the inventory that should be active
- sets the chosen inventory to Use=True
- sets the other discovered inventories to Use=False
- can remember the chosen inventory inside the current Vectorworks document
- can REBIND a drawing to its previously remembered inventory
- resets Summary Key objects throughout the drawing after switching inventory
- redraws the document
- verifies the inventory XML flags on disk after the change
- saves a last-run report in the Vectorworks user folder


DOCUMENT BINDING
----------------

When:

    Remember this inventory for this file

is enabled, F.I.N.G. stores the chosen inventory identity in a document Record
Format named:

    __FING_DOCUMENT_BINDING

using the field:

    InventoryName

This allows a drawing to remember which inventory it expects.

The REBIND action restores that saved document binding regardless of the
current picker selection, then refreshes the file's Summary Keys.

Save the Vectorworks drawing after setting its binding if you want the binding
to persist with the file.


USER INTERFACE
--------------

The main confirmation button is:

    THIS IS MY INVENTORY

Additional action:

    REBIND
        Restore the inventory remembered by this drawing and update its
        Summary Keys.

The interface also contains:

    UNASSOCIATED

but that action is DISABLED in v1.0.

Native equipment source-assignment selection has not been verified strongly
enough to expose that operation.


SUMMARY KEY REFRESH
-------------------

After inventory activation, F.I.N.G. searches the drawing for Summary Key
parametric objects and requests a reset for each one.

The search includes objects inside drawing groups and viewport annotations.

Symbol Definitions are excluded so F.I.N.G. does not modify resource
definitions merely to refresh placed drawing objects.

F.I.N.G. reports how many Summary Keys were requested for refresh and any API
reset errors.


BACKUPS / WRITE SAFETY
----------------------

Before changing an inventory XML file, F.I.N.G. creates verified backups under:

    Vectorworks user folder
    / _FING
    / backups
    / <timestamp>

A manifest records each changed inventory and its before/after Use state.

Inventory-file writes are atomic.

Before the first write, F.I.N.G. verifies that every file still matches the
version it inspected.

It checks again immediately before each write.

After writing, it reads the changed files back and verifies the exact bytes.

If a batch write fails, F.I.N.G. attempts to restore already-written files to
their original contents.

If a file was concurrently changed by something else, F.I.N.G. does not
blindly overwrite that concurrent edit.


LIMITATIONS / IMPORTANT BEHAVIOR
--------------------------------

Inventory activation is GLOBAL to the Vectorworks inventory XML files.

It is not isolated per open document.

Therefore:

- run F.I.N.G. after switching between drawings that expect different
  inventories
- save a drawing after setting its document binding
- use REBIND when returning to a drawing whose remembered inventory should be
  restored

F.I.N.G. verifies the inventory flags written to disk.

Its report deliberately does NOT claim that Vectorworks' native in-memory
inventory state or visible Equipment Summary Key totals have been independently
verified by an API.

The final visual result should still be treated as the authoritative check.


UNFINISHED PROBE SAFETY CHECK
-----------------------------

F.I.N.G. refuses to run if the earlier live-test probe still has an unfinished
restore recorded at:

    Vectorworks user folder
    / _FING_PROBE
    / 06_pending_restore.json

Restore that probe state first before using F.I.N.G.


WHAT IT DOES NOT DO
-------------------

F.I.N.G. does not:

- automatically detect document switching
- automatically monitor which drawing is frontmost
- edit inventory quantities
- edit equipment source assignments
- expose the UNASSOCIATED workflow in v1.0
- modify Symbol Definitions while refreshing Summary Keys

========================================================================
========================================================================
VERSION / AUTHORSHIP
========================================================================

1 RESOURCE AUDITOR
Version: v2.7

2 MINDREADER
Version: v5.0

3 MINDREADER ACCESSORY AUTOPSY
Version: v1.0

4 HYPERLINK REBUILDER
Version: v2.0

5 STIRRUP HANGER INSERTION TRICK
Version: v1.3

6 FIXTURE TYPE TO NEW LAYER
Version: v1.2

7 LIGHTING DEVICE ATTRIBUTES
Version: v1.5

8 DR. DOOM
Version: v1.2

9 PICK A UNIT! ANY UNIT!
Version: v1.0.2

10 F.I.N.G.
Version: v1.0

Package date: 2026-09-07
vibed by Chuckles

VWX FAILS =
Vectorworks Fixes, Automation, Inspection & Library Scripts.
