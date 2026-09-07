VWX FAILS
INSTALLATION AND DEPLOYMENT

Package date: 2026-09-07

========================================================================
WHICH FILES SHOULD I USE?
========================================================================

Most users should install the ready-made VSM files from:

    plug-ins/

The editable Python source lives in:

    src/

The Python files are the canonical source. Each VSM is a deployed copy of the
matching source prepared as a Vectorworks menu command.


========================================================================
INSTALL THE VSM PLUG-INS
========================================================================

1. Close Vectorworks.
2. Copy the desired .vsm files from plug-ins/ into the Plug-ins folder inside
   the Vectorworks user folder or the applicable Vectorworks workgroup folder.
3. Reopen Vectorworks.
4. Open the Workspace Editor.
5. Add the VWX FAILS commands to the desired menu in the active workspace.
6. Save the workspace and test the commands in a duplicate drawing.

If an older copy of a command is already installed, replace that deployed VSM
with the newer matching file. Keep only one active copy of each command across
the user and workgroup Plug-ins folders to avoid duplicate commands.


========================================================================
USE THE PYTHON SOURCE AS SCRIPT RESOURCES
========================================================================

1. Open or create a Vectorworks script palette.
2. Create one Python Script Resource for each desired tool.
3. Open the matching file from src/ and paste its complete contents into the
   script editor.
4. Keep the numbered shelf order shown in README.md.
5. Test resource-changing tools on a duplicate file first.

Updating a file in src/ does not automatically update an existing Script
Resource or installed VSM. Update whichever deployed copy Vectorworks is
actually running.


========================================================================
SOURCE / VSM RELEASE RULE
========================================================================

Every published shelf tool should have one pair:

    src/<number and descriptive name>.py
    plug-ins/<same number and descriptive name>.vsm

When a tool changes:

1. Update and test the canonical Python source.
2. Update 99 CHUCKLES NOTES in the same release when the tool inventory,
   version, workflow, warnings, or limitations changed.
3. Rebuild the VSM from that final source.
4. Verify the source and VSM versions.
5. Update README.md, INSTALL.md when needed, and PACKAGE_MANIFEST.txt.
6. Publish the source and VSM together.


========================================================================
NEXT VSM REBUILD: DISPLAY-NAME STANDARD
========================================================================

The current VSM files in this release are preserved exactly as exported.

When each plug-in is next rebuilt, use these descriptive Vectorworks command
names so the acronyms remain recognizable without hiding what the tools do:

1  RESOURCE AUDITOR
2  MINDREADER
3  MINDREADER ACCESSORY AUTOPSY
4  HYPERLINK REBUILDER
5  S.H.I.T. — STIRRUP HANGER INSERTION TRICK
6  FIXTURE TYPE TO NEW LAYER
7  LIGHTING DEVICE ATTRIBUTES
8  DR. DOOM — DRAWING REVIEW, DIAGNOSTICS, ORGANIZATION & OBJECT MANIPULATION
9  PICK A UNIT! ANY UNIT!
10 F.I.N.G. — FILE INVENTORY NORMALIZATION GOVERNOR
99 CHUCKLES NOTES

Keep the shelf number first and keep CHUCKLES NOTES last.
