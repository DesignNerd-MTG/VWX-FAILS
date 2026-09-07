# VWX FAILS - STIRRUP HANGER INSERTION TRICK v1.3
# vibed by Chuckles
# Date: 2026-08-18
# Version: v1.3
#
# Stirrup Hanger Insertion Trick
# Hanging Hardware 3D Companion Pairer
#
# Workaround for Vectorworks 2026 Spotlight Base accessory Top/Plan behavior.
#
# HUMAN WORKFLOW
# --------------
# 1. Insert the normal, cleanly named 2D-only Yoke accessory.
# 2. If 2D is all you need, stop there.
# 3. If you need correct 3D hanging geometry, select the Lighting Device(s).
# 4. Run SHIT.
# 5. SHIT adds the matching Z-3D PROXY Base accessory if it is missing.
#
# The normal accessory handles drafting.
# The Z-3D PROXY handles correct 3D hanging behavior.
#
# v1.3 is designed for MULTIPLE accessory / 3D-companion pairs.
#
# SAFETY
# ------
# - Selected Lighting Devices only.
# - Single-cell Lighting Devices only in this version.
# - Never adds a 3D companion twice.
# - Never deletes an accessory.
# - Never edits resource geometry or record values.
# - Validates every configured pair before touching a fixture.

import vs


# ============================================================================
# USER CONFIGURATION - ADD NEW HARDWARE HERE
# ============================================================================
#
# Each line is:
#
#     "NORMAL 2D ACCESSORY": "Z-3D PROXY BASE ACCESSORY",
#
# Use the EXACT Vectorworks resource names.
#
# Normal accessory requirements:
#   - Static Accessory
#   - Parts.Yoke=True
#   - 2D geometry used for normal Top/Plan drafting
#
# 3D companion requirements:
#   - Static Accessory
#   - Parts.Base=True
#   - 3D geometry used for correct hanging behavior
#
# IMPORTANT:
# Do not activate a line until BOTH symbol resources exist in the current file.
# SHIT deliberately fails preflight on missing or misspelled resources.

ACCESSORY_TO_3D_PROXY = {
    "Telescoping Kellum 8-16 ft":
        "Z-3D PROXY - Telescoping Kellum 8-16 ft",

    "Telescoping Stirrup Hanger 2-6ft":
        "Z-3D PROXY - Telescoping Stirrup Hanger 2-6ft",

    "Telescoping Stirrup Hanger 4-8 ft":
        "Z-3D PROXY - Telescoping Stirrup Hanger 4-8 ft",

    "Pantograph":
        "Z-3D PROXY - Pantograph",
}


# ============================================================================
# CONSTANTS
# ============================================================================

LIGHTING_DEVICE_RECORD = "Lighting Device"
LIGHT_INFO_RECORD = "Light Info Record"
PARTS_RECORD = "Parts"

PIO_TYPE = 86
SYMBOL_INSTANCE_TYPE = 15
SYMBOL_DEFINITION_TYPE = 16

MAX_GENERATED_OBJECTS = 2500


# ============================================================================
# BASIC HELPERS
# ============================================================================

def valid(h):
    if h is None:
        return False

    try:
        return h != vs.Handle()
    except:
        return True


def obj_type(h):
    try:
        return vs.GetTypeN(h)
    except:
        return -1


def get_sym_name(h):
    try:
        value = vs.GetSymName(h)
        return value if value else ""
    except:
        return ""


def get_rfield(h, record, field):
    try:
        value = vs.GetRField(
            h,
            record,
            field
        )

        return "" if value is None else str(value)

    except:
        return ""


def record_names(h):
    names = []

    try:
        count = vs.NumRecords(h)
    except:
        return names

    for i in range(1, count + 1):
        try:
            rh = vs.GetRecord(h, i)

            if valid(rh):
                rn = vs.GetName(rh)

                if rn:
                    names.append(rn)

        except:
            pass

    return names


def has_record(h, record_name):
    return record_name in record_names(h)


def record_true(value):
    return str(value).strip().lower() in (
        "true",
        "yes",
        "1",
        "t",
        "y",
    )


# ============================================================================
# RESOURCE PREFLIGHT
# ============================================================================

def symbol_definition(symbol_name):
    try:
        h = vs.GetObject(symbol_name)
    except:
        return None

    if (
        valid(h)
        and obj_type(h) == SYMBOL_DEFINITION_TYPE
    ):
        return h

    return None


def device_type(h):
    return get_rfield(
        h,
        LIGHT_INFO_RECORD,
        "Device Type"
    ).strip()


def part_true(h, field):
    return record_true(
        get_rfield(
            h,
            PARTS_RECORD,
            field
        )
    )


def validate_configuration():
    errors = []
    resources = {}

    if not ACCESSORY_TO_3D_PROXY:
        errors.append(
            "ACCESSORY_TO_3D_PROXY contains no configured hardware pairs."
        )
        return resources, errors

    for accessory_name, proxy3d_name in ACCESSORY_TO_3D_PROXY.items():
        if not accessory_name.strip():
            errors.append(
                "A normal accessory name is blank."
            )
            continue

        if not proxy3d_name.strip():
            errors.append(
                "{}: 3D proxy symbol name is blank.".format(
                    accessory_name
                )
            )
            continue

        accessory_h = symbol_definition(
            accessory_name
        )

        proxy3d_h = symbol_definition(
            proxy3d_name
        )

        if not valid(accessory_h):
            errors.append(
                "Normal 2D accessory not found: {}".format(
                    accessory_name
                )
            )
            continue

        if not valid(proxy3d_h):
            errors.append(
                "3D Base proxy not found: {}".format(
                    proxy3d_name
                )
            )
            continue

        if device_type(accessory_h).lower() != "static accessory":
            errors.append(
                "Normal 2D accessory is not Static Accessory: {}".format(
                    accessory_name
                )
            )

        if device_type(proxy3d_h).lower() != "static accessory":
            errors.append(
                "3D proxy is not Static Accessory: {}".format(
                    proxy3d_name
                )
            )

        if not part_true(
            accessory_h,
            "Yoke"
        ):
            errors.append(
                "Normal 2D accessory is not Parts.Yoke=True: {}".format(
                    accessory_name
                )
            )

        if not part_true(
            proxy3d_h,
            "Base"
        ):
            errors.append(
                "3D proxy is not Parts.Base=True: {}".format(
                    proxy3d_name
                )
            )

        resources[accessory_name] = {
            "accessory_h": accessory_h,
            "proxy3d_h": proxy3d_h,
            "proxy3d_name": proxy3d_name,
        }

    return resources, errors


# ============================================================================
# SELECTED LIGHTING DEVICES
# ============================================================================

def selected_objects():
    out = []

    try:
        h = vs.FSActLayer()
    except:
        h = None

    while valid(h):
        out.append(h)

        try:
            h = vs.NextSObj(h)
        except:
            break

    return out


def is_lighting_device(h):
    return (
        valid(h)
        and obj_type(h) == PIO_TYPE
        and has_record(
            h,
            LIGHTING_DEVICE_RECORD
        )
    )


# ============================================================================
# GENERATED ACCESSORY DISCOVERY
# ============================================================================

def generated_objects(pio):
    out = []

    try:
        first = vs.FInGroup(pio)
    except:
        return out

    if not valid(first):
        return out

    def collect(h):
        if len(out) < MAX_GENERATED_OBJECTS:
            out.append(h)

    try:
        vs.ForEachObjectInList(
            collect,
            0,
            2,
            first
        )
    except:
        pass

    return out


def attached_static_accessories(pio):
    names = []

    for h in generated_objects(pio):
        if obj_type(h) != SYMBOL_INSTANCE_TYPE:
            continue

        if not has_record(
            h,
            LIGHT_INFO_RECORD
        ):
            continue

        dt = get_rfield(
            h,
            LIGHT_INFO_RECORD,
            "Device Type"
        ).strip().lower()

        if dt != "static accessory":
            continue

        sn = get_sym_name(h)

        if sn:
            names.append(sn)

    return names


# ============================================================================
# LDEVICE API
# ============================================================================

def cell_count(h):
    try:
        return int(
            vs.LDevice_GetCellCount(h)
        )
    except:
        return -1


def add_accessory(
    fixture_h,
    proxy3d_symbol_h
):
    try:
        index = vs.LDevice_AddAccessory(
            fixture_h,
            0,
            proxy3d_symbol_h
        )

        return True, index, ""

    except Exception as e:
        return False, None, str(e)


def reset_device(h):
    try:
        vs.LDevice_Reset(h)
        return True, ""
    except Exception as e:
        return False, str(e)


# ============================================================================
# PROCESS ONE FIXTURE
# ============================================================================

def process_fixture(
    fixture_h,
    pair_resources
):
    count = cell_count(fixture_h)

    if count < 0:
        return (
            "failure",
            "Could not read cell count."
        )

    if count != 1:
        return (
            "multicell",
            "Cell count = {}.".format(count)
        )

    before = set(
        attached_static_accessories(
            fixture_h
        )
    )

    configured_accessories = [
        accessory_name
        for accessory_name in ACCESSORY_TO_3D_PROXY
        if accessory_name in before
    ]

    if not configured_accessories:
        return (
            "no_accessory",
            "No configured 2D accessory attached."
        )

    added = []
    already = []
    failures = []

    for accessory_name in configured_accessories:
        proxy3d_name = ACCESSORY_TO_3D_PROXY[
            accessory_name
        ]

        if proxy3d_name in before:
            already.append(proxy3d_name)
            continue

        proxy3d_h = pair_resources[
            accessory_name
        ]["proxy3d_h"]

        ok, index, error = add_accessory(
            fixture_h,
            proxy3d_h
        )

        if not ok:
            failures.append(
                "{}: AddAccessory error: {}".format(
                    proxy3d_name,
                    error
                )
            )
            continue

        reset_ok, reset_error = reset_device(
            fixture_h
        )

        if not reset_ok:
            failures.append(
                "{}: added index {}, reset failed: {}".format(
                    proxy3d_name,
                    index,
                    reset_error
                )
            )
            continue

        after = set(
            attached_static_accessories(
                fixture_h
            )
        )

        if proxy3d_name in after:
            added.append(
                "{} [index {}]".format(
                    proxy3d_name,
                    index
                )
            )
            before.add(proxy3d_name)
        else:
            failures.append(
                "{}: API returned index {}, but verification "
                "did not find the accessory.".format(
                    proxy3d_name,
                    index
                )
            )

    if failures:
        text = "\n".join(failures)

        if added:
            text += (
                "\nAdded: " +
                ", ".join(added)
            )

        if already:
            text += (
                "\nAlready present: " +
                ", ".join(already)
            )

        return "failure", text

    if added:
        return (
            "added",
            "Added: {}".format(
                ", ".join(added)
            )
        )

    if already:
        return (
            "already",
            "3D companion already present: {}".format(
                ", ".join(already)
            )
        )

    return (
        "failure",
        "No 3D companion action completed."
    )


# ============================================================================
# STARTUP / WARNING SUMMARY
# ============================================================================

def configured_accessory_lines():
    names = list(
        ACCESSORY_TO_3D_PROXY.keys()
    )

    if not names:
        return [
            "(none configured)"
        ]

    return [
        "- {}".format(name)
        for name in names
    ]


def selection_warning_lines(fixtures):
    warnings = []

    multicell = 0

    for h in fixtures:
        count = cell_count(h)

        if count != 1:
            multicell += 1

    if multicell:
        warnings.append(
            "{} selected Lighting Device(s) are multi-cell or "
            "could not report a single cell; they will be skipped.".format(
                multicell
            )
        )

    return warnings


def startup_message(
    fixtures,
    config_errors
):
    lines = [
        "VWX FAILS - SHIT v1.3",
        "",
        "STIRRUP HANGER INSERTION TRICK",
        "",
        "CONFIGURED ACCESSORIES",
    ]

    lines.extend(
        configured_accessory_lines()
    )

    lines.extend([
        "",
        "Selected Lighting Devices: {}".format(
            len(fixtures)
        ),
    ])

    warnings = []

    if config_errors:
        warnings.extend(
            config_errors
        )

    if not fixtures:
        warnings.append(
            "No Lighting Devices are selected."
        )
    else:
        warnings.extend(
            selection_warning_lines(
                fixtures
            )
        )

    if warnings:
        lines.extend([
            "",
            "WARNING",
        ])

        lines.extend(
            "- {}".format(w)
            for w in warnings
        )

    return "\n".join(lines), warnings


# ============================================================================
# MAIN
# ============================================================================

def main():
    pair_resources, errors = validate_configuration()

    selected = selected_objects()

    fixtures = [
        h
        for h in selected
        if is_lighting_device(h)
    ]

    summary, warnings = startup_message(
        fixtures,
        errors
    )

    if errors:
        vs.AlrtDialog(
            summary +
            "\n\nCONFIGURATION / RESOURCE PREFLIGHT FAILED."
            "\nNothing was changed."
        )
        return

    if not fixtures:
        vs.AlrtDialog(
            summary +
            "\n\nSelect one or more Lighting Devices and run SHIT again."
        )
        return

    if not vs.YNDialog(
        summary +
        "\n\nContinue?"
    ):
        return

    counts = {
        "added": 0,
        "already": 0,
        "no_accessory": 0,
        "multicell": 0,
        "failure": 0,
    }

    details = []

    for number, fixture_h in enumerate(
        fixtures,
        start=1
    ):
        status, detail = process_fixture(
            fixture_h,
            pair_resources
        )

        counts[status] += 1

        if status in (
            "failure",
            "multicell",
        ):
            details.append(
                "Fixture #{:03d}: {}".format(
                    number,
                    detail
                )
            )

    message = (
        "VWX FAILS - SHIT v1.3\n\n"
        "Selected Lighting Devices: {total}\n\n"
        "3D companion added: {added}\n"
        "3D companion already present: {already}\n"
        "No configured 2D accessory found: {no_accessory}\n"
        "Skipped multi-cell: {multicell}\n"
        "Failures: {failure}"
    ).format(
        total=len(fixtures),
        added=counts["added"],
        already=counts["already"],
        no_accessory=counts["no_accessory"],
        multicell=counts["multicell"],
        failure=counts["failure"],
    )

    if details:
        message += (
            "\n\nDETAILS\n" +
            "\n".join(
                details[:12]
            )
        )

        if len(details) > 12:
            message += (
                "\n...and {} more.".format(
                    len(details) - 12
                )
            )

    vs.AlrtDialog(message)


main()
