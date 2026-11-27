"""Validate schema, referential integrity, non-duplication, and scenario coverage
for data/travel-ops/ and data/travel-behavior/ using pure Python stdlib.

Run:
    python data/validate_travel_data.py
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPS_DIR = ROOT / "data" / "travel-ops"
BEH_DIR = ROOT / "data" / "travel-behavior"

EXPECTED_OPS_FILES = [
    "README.md",
    "poi_master.csv",
    "opening_hours.csv",
    "zone_travel_matrix.csv",
    "live_disruptions.csv",
    "schedule_warnings.csv",
    "edit_history.csv",
]

EXPECTED_BEH_FILES = [
    "README.md",
    "column_dictionary.csv",
    "event_types.csv",
    "travelers.csv",
    "trips.csv",
    "chat.csv",
    "recommendations.csv",
    "events.csv",
    "disruption_events.csv",
    "completed_itineraries.csv",
]

DAYS = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
SCENARIO_GROUPS = {
    "multi_stop_scheduling",
    "dynamic_rescheduling",
    "context_aware_qa",
    "edge_adversarial",
}
TEST_TYPES = {"thuong", "kho", "tu_choi"}


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = []
        for idx, row in enumerate(reader, 2):
            if None in row:
                raise ValueError(f"{path.name} line {idx}: extra columns {row[None]}")
            if all(not str(v or "").strip() for v in row.values()):
                raise ValueError(f"{path.name} line {idx}: blank row")
            rows.append(row)
    return fields, rows


def main() -> int:
    errors: list[str] = []

    def err(msg: str):
        errors.append(msg)

    # 1. File existence
    for fn in EXPECTED_OPS_FILES:
        if not (OPS_DIR / fn).exists():
            err(f"Missing file in travel-ops/: {fn}")
    for fn in EXPECTED_BEH_FILES:
        if not (BEH_DIR / fn).exists():
            err(f"Missing file in travel-behavior/: {fn}")
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1

    # 2. Load travel-ops
    poi_fields, poi_rows = read_csv(OPS_DIR / "poi_master.csv")
    oh_fields, oh_rows = read_csv(OPS_DIR / "opening_hours.csv")
    mat_fields, mat_rows = read_csv(OPS_DIR / "zone_travel_matrix.csv")
    dis_fields, dis_rows = read_csv(OPS_DIR / "live_disruptions.csv")
    warn_fields, warn_rows = read_csv(OPS_DIR / "schedule_warnings.csv")
    edit_fields, edit_rows = read_csv(OPS_DIR / "edit_history.csv")

    # Primary key uniqueness in travel-ops
    poi_ids = [r["poi_id"] for r in poi_rows]
    if len(poi_ids) != len(set(poi_ids)):
        err("Duplicate poi_id in poi_master.csv")
    poi_map = {r["poi_id"]: r for r in poi_rows}

    # opening_hours completeness: 7 days per POI, unique (poi_id, day_of_week)
    oh_pairs = [(r["poi_id"], r["day_of_week"]) for r in oh_rows]
    if len(oh_pairs) != len(set(oh_pairs)):
        err("Duplicate (poi_id, day_of_week) in opening_hours.csv")
    for pid in poi_map:
        days_for_poi = {r["day_of_week"] for r in oh_rows if r["poi_id"] == pid}
        if days_for_poi != DAYS:
            err(f"opening_hours.csv missing days for {pid}: {DAYS - days_for_poi}")
    for r in oh_rows:
        if r["poi_id"] not in poi_map:
            err(f"opening_hours.csv unknown poi_id: {r['poi_id']}")
        if r["is_open"] not in ("True", "False"):
            err(f"opening_hours.csv invalid is_open for {r['poi_id']} {r['day_of_week']}")

    # zone_travel_matrix completeness: every (city, z1, z2) pair covered
    city_zones: dict[str, set[str]] = {}
    for r in poi_rows:
        city_zones.setdefault(r["city"], set()).add(r["zone"])
    mat_keys = [(r["city"], r["from_zone"], r["to_zone"]) for r in mat_rows]
    if len(mat_keys) != len(set(mat_keys)):
        err("Duplicate (city, from_zone, to_zone) in zone_travel_matrix.csv")
    mat_set = set(mat_keys)
    for city, zones in city_zones.items():
        for z1 in zones:
            for z2 in zones:
                if (city, z1, z2) not in mat_set:
                    err(f"zone_travel_matrix.csv missing pair {(city, z1, z2)}")

    # live_disruptions & schedule_warnings checks
    dis_ids = [r["disruption_id"] for r in dis_rows]
    if len(dis_ids) != len(set(dis_ids)):
        err("Duplicate disruption_id in live_disruptions.csv")
    for r in dis_rows:
        if r["poi_id"] and r["poi_id"] not in poi_map:
            err(f"live_disruptions.csv unknown poi_id {r['poi_id']}")
    warn_ids = [r["warning_id"] for r in warn_rows]
    if len(warn_ids) != len(set(warn_ids)):
        err("Duplicate warning_id in schedule_warnings.csv")
    for r in warn_rows:
        if r["poi_id"] not in poi_map:
            err(f"schedule_warnings.csv unknown poi_id {r['poi_id']}")

    # 3. Load travel-behavior
    beh_tables = {}
    for fn in EXPECTED_BEH_FILES:
        if fn.endswith(".csv"):
            beh_tables[fn] = read_csv(BEH_DIR / fn)

    _, cd_rows = beh_tables["column_dictionary.csv"]
    _, et_rows = beh_tables["event_types.csv"]
    _, trav_rows = beh_tables["travelers.csv"]
    _, trip_rows = beh_tables["trips.csv"]
    _, chat_rows = beh_tables["chat.csv"]
    _, rec_rows = beh_tables["recommendations.csv"]
    _, ev_rows = beh_tables["events.csv"]
    _, dev_rows = beh_tables["disruption_events.csv"]
    _, comp_rows = beh_tables["completed_itineraries.csv"]

    # Check column_dictionary matches actual headers of every data CSV in travel-behavior
    cd_cols_by_file: dict[str, set[str]] = {}
    for r in cd_rows:
        cd_cols_by_file.setdefault(r["file"], set()).add(r["cot"])
    for fn, (fields, _) in beh_tables.items():
        if fn in ("column_dictionary.csv", "event_types.csv"):
            continue
        actual_set = set(fields)
        dict_set = cd_cols_by_file.get(fn, set())
        if actual_set != dict_set:
            err(f"column_dictionary mismatch for {fn}: missing_in_dict={actual_set - dict_set}, extra_in_dict={dict_set - actual_set}")

    # Primary keys & uniqueness in travel-behavior
    trav_ids = [r["khach"] for r in trav_rows]
    if len(trav_ids) != len(set(trav_ids)):
        err("Duplicate khach in travelers.csv")
    trav_set = set(trav_ids)

    trip_ids = [r["trip_id"] for r in trip_rows]
    if len(trip_ids) != len(set(trip_ids)):
        err("Duplicate trip_id in trips.csv")
    trip_map = {r["trip_id"]: r for r in trip_rows}

    chat_ids = [r["id"] for r in chat_rows]
    if len(chat_ids) != len(set(chat_ids)):
        err("Duplicate id in chat.csv")
    chat_map = {r["id"]: r for r in chat_rows}

    user_msgs = [r["user_message"].strip() for r in chat_rows]
    if len(user_msgs) != len(set(user_msgs)):
        err("Duplicate user_message in chat.csv")

    rec_ids = [r["id"] for r in rec_rows]
    if len(rec_ids) != len(set(rec_ids)):
        err("Duplicate id in recommendations.csv")
    rec_refs = [r["ref"] for r in rec_rows]
    if len(rec_refs) != len(set(rec_refs)) or set(rec_refs) != set(chat_ids):
        err("recommendations.csv.ref must have 1-to-1 correspondence with chat.csv.id")

    # Foreign key checks
    for r in trip_rows:
        if r["khach"] not in trav_set:
            err(f"trips.csv unknown khach {r['khach']}")

    for r in chat_rows:
        if r["khach"] not in trav_set:
            err(f"chat.csv {r['id']} unknown khach {r['khach']}")
        if r["trip_id"] not in trip_map:
            err(f"chat.csv {r['id']} unknown trip_id {r['trip_id']}")
        if r["scenario_group"] not in SCENARIO_GROUPS:
            err(f"chat.csv {r['id']} invalid scenario_group {r['scenario_group']}")
        if r["test_type"] not in TEST_TYPES:
            err(f"chat.csv {r['id']} invalid test_type {r['test_type']}")
        if r["current_poi_id"] and r["current_poi_id"] not in poi_map:
            err(f"chat.csv {r['id']} unknown current_poi_id {r['current_poi_id']}")
        for col in ("expected_poi_ids", "forbidden_poi_ids"):
            for pid in [x for x in r[col].split("|") if x]:
                if pid not in poi_map:
                    err(f"chat.csv {r['id']} unknown {col} item {pid}")
        # Ensure expected and forbidden do not overlap
        exp_set = {x for x in r["expected_poi_ids"].split("|") if x}
        forb_set = {x for x in r["forbidden_poi_ids"].split("|") if x}
        if exp_set & forb_set:
            err(f"chat.csv {r['id']} overlap between expected and forbidden POIs: {exp_set & forb_set}")
        # Ensure all referenced POIs belong to the trip's city
        trip_city = trip_map[r["trip_id"]]["city"]
        for pid in exp_set | forb_set | ({r["current_poi_id"]} if r["current_poi_id"] else set()):
            if poi_map[pid]["city"] != trip_city:
                err(f"chat.csv {r['id']} POI {pid} city={poi_map[pid]['city']} != trip city={trip_city}")
        # Check lengths match
        if int(r["do_dai_cau_hoi"]) != len(r["user_message"]):
            err(f"chat.csv {r['id']} do_dai_cau_hoi mismatch")

    for r in rec_rows:
        if r["khach"] not in trav_set or r["trip_id"] not in trip_map:
            err(f"recommendations.csv {r['id']} invalid FK")
        for pid in [x for x in r["proposed_poi_ids"].split("|") if x]:
            if pid not in poi_map:
                err(f"recommendations.csv {r['id']} unknown proposed_poi_id {pid}")
        for rcol in ("rubric_chinh_xac_gio", "rubric_thuan_duong", "rubric_khong_ao_giac"):
            if r[rcol] not in ("0", "1", "2"):
                err(f"recommendations.csv {r['id']} invalid {rcol}={r[rcol]}")

    # Events & event_types consistency
    actual_ev_counts = Counter()
    for idx, r in enumerate(ev_rows, 2):
        if r["khach"] not in trav_set or r["trip_id"] not in trip_map:
            err(f"events.csv line {idx} invalid FK")
        if r["poi_id"] and r["poi_id"] not in poi_map:
            err(f"events.csv line {idx} unknown poi_id {r['poi_id']}")
        if r["ref_id"] and r["ref_id"] not in chat_map:
            err(f"events.csv line {idx} unknown ref_id {r['ref_id']}")
        try:
            obj = json.loads(r["data"])
            if not isinstance(obj, dict):
                err(f"events.csv line {idx} data is not JSON object")
        except json.JSONDecodeError as ex:
            err(f"events.csv line {idx} invalid JSON: {ex}")
        actual_ev_counts[r["type"]] += 1

    dis_id_set = set(dis_ids)
    for idx, r in enumerate(dev_rows, 2):
        if r["trip_id"] not in trip_map or r["poi_id"] not in poi_map:
            err(f"disruption_events.csv line {idx} invalid FK")
        if r["ref_id"] not in dis_id_set and r["ref_id"] not in chat_map:
            err(f"disruption_events.csv line {idx} unknown ref_id {r['ref_id']}")
        try:
            obj = json.loads(r["data"])
            if not isinstance(obj, dict):
                err(f"disruption_events.csv line {idx} data is not JSON object")
        except json.JSONDecodeError as ex:
            err(f"disruption_events.csv line {idx} invalid JSON: {ex}")
        actual_ev_counts[r["type"]] += 1

    et_map = {r["type"]: int(r["so_dong_trong_ban_nay"]) for r in et_rows}
    if set(et_map.keys()) != set(actual_ev_counts.keys()):
        err(f"event_types.csv types mismatch: dict={set(et_map.keys())}, actual={set(actual_ev_counts.keys())}")
    for t, cnt in actual_ev_counts.items():
        if et_map.get(t) != cnt:
            err(f"event_types.csv count mismatch for {t}: recorded={et_map.get(t)}, actual={cnt}")

    for idx, r in enumerate(comp_rows, 2):
        if r["khach"] not in trav_set or r["trip_id"] not in trip_map or r["poi_id"] not in poi_map:
            err(f"completed_itineraries.csv line {idx} invalid FK")

    # 4. Scenario coverage & domain consistency checks
    sg_counts = Counter(r["scenario_group"] for r in chat_rows)
    tt_counts = Counter(r["test_type"] for r in chat_rows)
    city_counts = Counter(trip_map[r["trip_id"]]["city"] for r in chat_rows)
    for sg in SCENARIO_GROUPS:
        if sg_counts[sg] < 10:
            err(f"Insufficient coverage for {sg}: {sg_counts[sg]}")

    # Check every POI in poi_master has non-empty verified_source
    for r in poi_rows:
        if not r["verified_source"].strip() or not r["address"].strip():
            err(f"poi_master.csv {r['poi_id']} missing address or verified_source")

    if errors:
        print(f"VALIDATION FAILED with {len(errors)} error(s):")
        for e in errors:
            print("  -", e)
        return 1

    print("VALIDATION PASSED: 0 errors!")
    print(f"travel-ops/: {len(poi_rows)} POIs across {sorted(city_zones.keys())}, {len(oh_rows)} opening_hours rows, {len(mat_rows)} matrix pairs, {len(dis_rows)} live disruptions, {len(warn_rows)} warnings, {len(edit_rows)} edits")
    print(f"travel-behavior/: {len(trav_rows)} travelers, {len(trip_rows)} trips, {len(chat_rows)} chat scenarios, {len(rec_rows)} recommendations, {len(ev_rows)} events, {len(dev_rows)} disruption_events, {len(comp_rows)} completed stops")
    print("Scenario coverage:", dict(sg_counts))
    print("Test type coverage:", dict(tt_counts))
    print("City coverage across chat scenarios:", dict(city_counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
