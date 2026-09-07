# VWX FAILS - RESOURCE AUDITOR v2.7
# vibed by Chuckles
# Date: 2026-08-19
# Version: v2.7
#
# Vectorworks Fixes, Automation, Inspection & Library Scripts
# Text-entry version with an on-screen list of available Record Formats.
# Adding records uses existing formats only; record comparison is read-only.

import vs

RECORD_FORMAT_TYPE = 47
REFERENCED_RESOURCE_SELECTOR = 700
DEFAULT_RESOURCE_TYPE = 16
DEFAULT_LOOK_FOR = "Light Info Record"
DEFAULT_REQUIRE_ADD = "EntEquipUniversal"
DEFAULT_COMPARE = "Light Info Record"
MAX_PREVIEW_NAMES = 18


COMMON_RESOURCE_TYPES = (
    (16, "Symbol Definition"),
    (18, "Worksheet"),
    (19, "Material Definition"),
    (47, "Record Format"),
    (66, "Hatch Definition"),
    (92, "Symbol Folder"),
    (93, "Texture"),
    (96, "Line Type Definition"),
    (102, "Roof Style Definition"),
    (107, "Slab Style Definition"),
    (108, "Tile Fill Definition"),
    (109, "Text Style Definition"),
    (115, "Renderworks Background"),
    (119, "Image Fill Definition"),
    (120, "Gradient Fill Definition"),
    (127, "Wall Style Definition"),
)


def common_resource_type_text():
    return "\n".join(
        "{} = {}".format(number, label)
        for number, label in COMMON_RESOURCE_TYPES
    )


def valid(h):
    if h is None:
        return False
    try:
        return h != vs.Handle()
    except:
        return True


def split_names(text):
    if text is None:
        return []
    out = []
    for piece in str(text).replace(";", ",").split(","):
        name = piece.strip()
        if name and name not in out:
            out.append(name)
    return out


def record_format_handle(name):
    try:
        h = vs.GetObject(name)
    except:
        return None
    if not valid(h):
        return None
    try:
        return h if vs.GetTypeN(h) == RECORD_FORMAT_TYPE else None
    except:
        return None


def available_record_formats():
    names = []
    try:
        list_id, count = vs.BuildResourceList(RECORD_FORMAT_TYPE, 0, "")
    except:
        return names

    for i in range(1, count + 1):
        name = ""
        try:
            name = vs.GetNameFromResourceList(list_id, i)
        except:
            try:
                h = vs.GetResourceFromList(list_id, i)
                if valid(h):
                    name = vs.GetName(h)
            except:
                pass

        if name and name not in names:
            names.append(name)

    return sorted(names, key=lambda s: s.lower())


def record_list_text():
    names = available_record_formats()

    if not names:
        return "No Record Formats were found in this file."

    return "Record Formats currently in this file:\n\n" + "\n".join(
        "- " + name for name in names
    )


def show_available_records():
    vs.AlrtDialog(
        "VWX FAILS - Resource Auditor\n\n" +
        record_list_text()
    )


def attached_record_names(h):
    names = []
    try:
        count = vs.NumRecords(h)
    except:
        return names

    for i in range(1, count + 1):
        try:
            rh = vs.GetRecord(h, i)
            if valid(rh):
                name = vs.GetName(rh)
                if name:
                    names.append(name)
        except:
            pass

    return names


def has_record(h, name):
    return name in attached_record_names(h)


def is_referenced(h):
    try:
        return bool(
            vs.GetObjectVariableBoolean(
                h,
                REFERENCED_RESOURCE_SELECTOR
            )
        )
    except:
        return False


def resources_of_type(resource_type):
    handles = []
    try:
        list_id, count = vs.BuildResourceList(resource_type, 0, "")
    except:
        return handles

    for i in range(1, count + 1):
        try:
            h = vs.GetResourceFromList(list_id, i)
            if valid(h):
                handles.append(h)
        except:
            pass

    return handles


def inspect_record(name):
    result = {
        "name": name,
        "exists": False,
        "fields": [],
        "field_map": {},
    }

    h = record_format_handle(name)
    if not valid(h):
        return result

    result["exists"] = True

    try:
        count = vs.NumFields(h)
    except:
        count = 0

    for i in range(1, count + 1):
        try:
            field_name = vs.GetFldName(h, i)
            field_type = vs.GetFldType(h, i)
        except:
            continue

        field = {
            "index": i,
            "name": field_name,
            "type": field_type,
        }

        result["fields"].append(field)
        result["field_map"][field_name] = field

    return result


def record_fields_text(record):
    if not record["exists"]:
        return "{} was not found.".format(record["name"])

    lines = [
        record["name"],
        "Fields: {}".format(len(record["fields"])),
        "",
    ]

    for field in record["fields"]:
        lines.append(
            "{:02d}  {}  [type {}]".format(
                field["index"],
                field["name"],
                field["type"]
            )
        )

    return "\n".join(lines)


def compare_records(checked, against):
    matching = []
    missing = []
    only_checked = []
    type_diff = []

    checked_map = checked["field_map"]
    against_map = against["field_map"]

    for name, other_field in against_map.items():
        if name not in checked_map:
            missing.append(other_field)
            continue

        checked_field = checked_map[name]

        if checked_field["type"] == other_field["type"]:
            matching.append(name)
        else:
            type_diff.append(
                (
                    checked_field,
                    other_field
                )
            )

    for name, checked_field in checked_map.items():
        if name not in against_map:
            only_checked.append(checked_field)

    lines = [
        "RECORD YOU CHECKED",
        "  {}  ({} fields)".format(
            checked["name"],
            len(checked["fields"])
        ),
        "",
        "COMPARED AGAINST",
        "  {}  ({} fields)".format(
            against["name"],
            len(against["fields"])
        ),
        "",
        "SUMMARY",
        "  Same fields: {}".format(len(matching)),
        "  Missing from checked record: {}".format(len(missing)),
        "  Only in checked record: {}".format(len(only_checked)),
        "  Same name, different type: {}".format(len(type_diff)),
    ]

    if missing:
        lines += ["", "MISSING FROM THE RECORD YOU CHECKED"]
        for field in missing:
            lines.append(
                "  + {}  [type {}]".format(
                    field["name"],
                    field["type"]
                )
            )

    if only_checked:
        lines += ["", "ONLY IN THE RECORD YOU CHECKED"]
        for field in only_checked:
            lines.append(
                "  - {}  [type {}]".format(
                    field["name"],
                    field["type"]
                )
            )

    if type_diff:
        lines += ["", "SAME FIELD NAME, DIFFERENT FIELD TYPE"]
        for checked_field, other_field in type_diff:
            lines.append(
                "  ! {}  checked={}  compared={}".format(
                    checked_field["name"],
                    checked_field["type"],
                    other_field["type"]
                )
            )

    if not missing and not only_checked and not type_diff:
        lines += [
            "",
            "These records have the same field names and field types."
        ]

    return "\n".join(lines)


def run_compare_records():
    show_available_records()

    checked_name = vs.StrDialog(
        "COMPARE RECORD FIELDS\n\n"
        "Type the exact name of the record you want to check:",
        DEFAULT_COMPARE
    )

    try:
        if vs.DidCancel():
            return
    except:
        pass

    checked_name = str(checked_name).strip()
    if not checked_name:
        return

    checked = inspect_record(checked_name)
    if not checked["exists"]:
        vs.AlrtDialog(
            "Resource Auditor\n\n"
            "I could not find this record:\n\n"
            "{}".format(checked_name)
        )
        return

    compare_name = vs.StrDialog(
        "COMPARE RECORD FIELDS\n\n"
        "Type the record to compare against.\n\n"
        "Leave this blank to just show the fields in:\n"
        "{}".format(checked_name),
        ""
    )

    try:
        if vs.DidCancel():
            return
    except:
        pass

    compare_name = str(compare_name).strip()

    if not compare_name:
        vs.AlrtDialog(
            "VWX FAILS - Resource Auditor\n\n"
            "RECORD FIELDS\n\n" +
            record_fields_text(checked) +
            "\n\nREAD ONLY"
        )
        return

    compared = inspect_record(compare_name)
    if not compared["exists"]:
        vs.AlrtDialog(
            "Resource Auditor\n\n"
            "I could not find the comparison record:\n\n"
            "{}".format(compare_name)
        )
        return

    vs.AlrtDialog(
        "VWX FAILS - Resource Auditor\n\n"
        "RECORD COMPARISON\n\n" +
        compare_records(
            checked,
            compared
        ) +
        "\n\nREAD ONLY - no record fields were changed."
    )


def qualifies(h, look_for, match_mode):
    if not look_for:
        return True

    attached = set(
        attached_record_names(h)
    )

    if match_mode == "ANY":
        return any(
            name in attached
            for name in look_for
        )

    return all(
        name in attached
        for name in look_for
    )


def audit_resources(
    resource_type,
    look_for,
    match_mode,
    must_have
):
    result = {
        "scanned": 0,
        "qualifying": [],
        "good": [],
        "missing": [],
        "referenced_missing": [],
    }

    resources = resources_of_type(
        resource_type
    )
    result["scanned"] = len(resources)

    for h in resources:
        if not qualifies(
            h,
            look_for,
            match_mode
        ):
            continue

        try:
            name = vs.GetName(h)
        except:
            name = ""

        result["qualifying"].append(
            (h, name)
        )

        attached = set(
            attached_record_names(h)
        )

        missing = [
            record_name
            for record_name in must_have
            if record_name not in attached
        ]

        if not missing:
            result["good"].append(
                (h, name)
            )
            continue

        item = (
            h,
            name,
            missing
        )

        if is_referenced(h):
            result["referenced_missing"].append(
                item
            )
        else:
            result["missing"].append(
                item
            )

    return result


def preview_missing(items):
    lines = []

    for item in items[:MAX_PREVIEW_NAMES]:
        lines.append(
            "- {}".format(
                item[1] or "<unnamed>"
            )
        )

    if len(items) > MAX_PREVIEW_NAMES:
        lines.append(
            "...and {} more".format(
                len(items) - MAX_PREVIEW_NAMES
            )
        )

    return "\n".join(lines)


def run_find_add():
    show_available_records()

    resource_text = vs.StrDialog(
        "FIND / ADD RECORDS\n\n"
        "What kind of resource should I check?\n\n"
        "COMMON RESOURCE TYPE NUMBERS\n"
        + common_resource_type_text()
        + "\n\nEnter the Vectorworks resource type number:",
        str(DEFAULT_RESOURCE_TYPE)
    )

    try:
        if vs.DidCancel():
            return
    except:
        pass

    try:
        resource_type = int(
            str(resource_text).strip()
        )
    except:
        vs.AlrtDialog(
            "Resource Auditor\n\n"
            "That resource type needs to be a number."
        )
        return

    look_text = vs.StrDialog(
        "FIND / ADD RECORDS\n\n"
        "Only check resources that already have:\n\n"
        "Type one or more exact record names.\n"
        "Separate multiple names with commas.\n"
        "Leave blank to check every resource of this type.",
        DEFAULT_LOOK_FOR
    )

    try:
        if vs.DidCancel():
            return
    except:
        pass

    look_for = split_names(
        look_text
    )

    must_text = vs.StrDialog(
        "FIND / ADD RECORDS\n\n"
        "Make sure those resources also have:\n\n"
        "Type one or more exact record names.\n"
        "Separate multiple names with commas.",
        DEFAULT_REQUIRE_ADD
    )

    try:
        if vs.DidCancel():
            return
    except:
        pass

    must_have = split_names(
        must_text
    )

    if not must_have:
        vs.AlrtDialog(
            "Resource Auditor\n\n"
            "Type at least one record to check for."
        )
        return

    missing_formats = [
        name
        for name in must_have
        if not valid(record_format_handle(name))
    ]

    if missing_formats:
        vs.AlrtDialog(
            "VWX FAILS - Resource Auditor\n\n"
            "I cannot find these record formats in this file:\n\n" +
            "\n".join(
                "- " + name
                for name in missing_formats
            ) +
            "\n\n"
            "The Auditor will not invent a record format.\n"
            "Import or create the real record format first.\n\n"
            "No resources were changed."
        )
        return

    match_mode = "ALL"

    if len(look_for) > 1:
        all_required = vs.YNDialog(
            "FIND / ADD RECORDS\n\n"
            "You asked me to look for more than one record:\n\n"
            "{}\n\n"
            "Should a resource need ALL of them before I check it?\n\n"
            "YES = ALL\n"
            "NO = ANY".format(
                "\n".join(
                    "- " + name
                    for name in look_for
                )
            )
        )

        match_mode = (
            "ALL"
            if all_required
            else "ANY"
        )

    result = audit_resources(
        resource_type,
        look_for,
        match_mode,
        must_have
    )

    look_summary = (
        ", ".join(look_for)
        if look_for
        else "<every resource of this type>"
    )

    summary = (
        "WHAT I CHECKED\n"
        "------------------------------\n"
        "Resource type: {resource_type}\n"
        "Only checked resources with: {look_for}\n"
        "Multiple-record rule: {match_mode}\n"
        "Made sure they also have: {must_have}\n\n"
        "Scanned: {scanned}\n"
        "Matched: {matched}\n"
        "Already good: {good}\n"
        "Need the record added: {missing}\n"
        "Referenced resources skipped: {referenced}"
    ).format(
        resource_type=resource_type,
        look_for=look_summary,
        match_mode=match_mode,
        must_have=", ".join(must_have),
        scanned=result["scanned"],
        matched=len(result["qualifying"]),
        good=len(result["good"]),
        missing=len(result["missing"]),
        referenced=len(result["referenced_missing"]),
    )

    if result["missing"]:
        summary += (
            "\n\nNEED THE RECORD ADDED\n" +
            preview_missing(
                result["missing"]
            )
        )

    if not result["missing"]:
        vs.AlrtDialog(
            "VWX FAILS - Resource Auditor\n\n" +
            summary +
            "\n\nEverything you asked me to check is already good.\n"
            "No changes were made."
        )
        return

    do_add = vs.YNDialog(
        "VWX FAILS - Resource Auditor\n\n" +
        summary +
        "\n\nAdd the missing record(s) now?\n\n"
        "No field values or geometry will be changed."
    )

    if not do_add:
        vs.AlrtDialog(
            "Resource Auditor\n\n"
            "Audit complete.\n"
            "No changes were made."
        )
        return

    attempted = 0
    added = 0
    failed = []

    for h, resource_name, missing in result["missing"]:
        for record_name in missing:
            attempted += 1

            try:
                vs.SetRecord(
                    h,
                    record_name
                )
            except Exception as e:
                failed.append(
                    (
                        resource_name,
                        record_name,
                        str(e)
                    )
                )
                continue

            if has_record(
                h,
                record_name
            ):
                added += 1
            else:
                failed.append(
                    (
                        resource_name,
                        record_name,
                        "Could not verify after adding."
                    )
                )

    verify = audit_resources(
        resource_type,
        look_for,
        match_mode,
        must_have
    )

    message = (
        "VWX FAILS - Resource Auditor\n\n"
        "DONE\n\n"
        "Records I tried to add: {attempted}\n"
        "Successfully added: {added}\n"
        "Could not add: {failed}\n"
        "Still missing after double-checking: {still_missing}"
    ).format(
        attempted=attempted,
        added=added,
        failed=len(failed),
        still_missing=len(verify["missing"])
    )

    if failed:
        message += "\n\nCOULD NOT ADD\n"
        for resource_name, record_name, reason in failed[:MAX_PREVIEW_NAMES]:
            message += (
                "\n- {} / {} / {}".format(
                    resource_name or "<unnamed>",
                    record_name,
                    reason
                )
            )

    if not failed and not verify["missing"]:
        message += (
            "\n\nEverything you asked me to check is now good."
        )

    vs.AlrtDialog(
        message
    )


def main():
    compare_mode = vs.YNDialog(
        "VWX FAILS - Resource Auditor v2.7\n\n"
        "What do you want to do?\n\n"
        "YES = COMPARE RECORD FIELDS\n"
        "See what fields a record contains, or compare two records.\n\n"
        "NO = FIND / ADD RECORDS\n"
        "Find matching resources and add a record they are missing."
    )

    if compare_mode:
        run_compare_records()
    else:
        run_find_add()


main()
