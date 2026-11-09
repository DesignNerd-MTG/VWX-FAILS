VWX FAILS 2.0.1 VALIDATION
========================

Scope: Resource Auditor v2.7.1, MINDREADER v5.0.1, and Fixture Type to New
Layer v1.2.1. CHUCKLES NOTES v1.0.4 contains the corresponding documentation.
The remaining seven tools are unchanged.

AUTOMATED CHECKS
----------------

Run from the repository root with Python 3:

    python -m unittest discover -s tests -v

The tests use only the Python standard library. They do not import the native
Vectorworks vs module or open a drawing.

- Resource Auditor: referenced, local, locked, unknown, unsupported, and
  malformed API results; no writes to blocked resources; safety rechecks
  after confirmation; accurate summaries of skipped resources.
- Fixture Type to New Layer: successful, rejected, unverified, exceptional,
  and already-on-target moves; accurate total and per-type counts.
- MINDREADER: native Python two-point GetBBox return shape and the existing
  unavailable-result fallback.
- Release integrity: all source syntax, source/VSM filename pairing, SHA-256
  manifest, quick-reference inventory, and newline formatting.
- VSM packaging: supported container structure, source extraction, preserved
  metadata and icons, and no-op round trips. The packaging tool accepts only
  the checked export family; it is not a general VSM writer.

The changed VSMs have refreshed embedded source and adjusted container
offsets. They were not exported or loaded by a live Vectorworks application
during this patch. Automated package validation is not native acceptance.

DUPLICATE-DRAWING ACCEPTANCE CHECKLIST
-------------------------------------

Before production use, install the new VSMs using INSTALL.md and test a copy
of a representative drawing in Vectorworks 2026. Keep the original drawing
and previous plug-in versions outside the active Plug-ins folders.

1. Run each changed menu command and CHUCKLES NOTES. Confirm the patched
   version appears, and verify that only one copy of each command is active.
2. Resource Auditor: use local unlocked, local locked, and externally
   referenced resources that are missing the required record. Preview the
   audit and confirm that referenced and locked resources are counted
   separately. Only the local unlocked resource should receive the record.
   Cancel a second audit and confirm that no resources change. Compare
   Record Fields should continue to work without modifying anything.
3. Fixture Type to New Layer: move selected fixtures of two instrument types.
   Confirm their destination layers and the reported counts. Run again to
   check the already-on-target count. Test a move that Vectorworks rejects
   if a suitable non-destructive case is available; it must not be reported
   as successful. Check Undo and the broader matching-type scope.
4. MINDREADER: inspect a rectangle with known bounds and a representative
   Lighting Device. Confirm that valid bounds appear in the report instead
   of <unavailable>. Inspect an object inside a symbol definition as well.
5. CHUCKLES NOTES: confirm the updated versions and warnings, readable line
   breaks, and unchanged dialog behavior.

No live drawing, native dialog, Undo, or VSM-loading checks were performed
for this release. These remain manual acceptance items, not passed tests.
