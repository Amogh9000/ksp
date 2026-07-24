"""
Faker-based synthetic data generator for the KSP Intelligence Platform.

Produces:
  - 20 Karnataka police stations (one per district)
  - 60 officers spread across stations
  - 3 000 criminals (with ~15 % repeat-offenders)
  - 10 000+ FIR records
  - criminal_links entries (accused, co-accused, associates)

Run from the backend/ directory:
    python -m scripts.seed_data
"""
from __future__ import annotations

import json
import os
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

import psycopg2
import psycopg2.extras
from faker import Faker
from passlib.context import CryptContext
from app.config import get_settings

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

# ---------------------------------------------------------------------------
# Karnataka districts
# ---------------------------------------------------------------------------
KARNATAKA_DISTRICTS = [
    "Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban",
    "Bidar", "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga",
    "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan",
    "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal",
    "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga",
    "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir",
    "Vijayanagara",
]
SEED_DISTRICTS = KARNATAKA_DISTRICTS[:20]

CRIME_CATEGORIES = [
    "murder", "attempt_to_murder", "kidnapping", "robbery", "dacoity",
    "theft", "burglary", "cheating", "fraud", "cyber_crime",
    "drug_offence", "assault", "sexual_assault", "domestic_violence",
    "motor_vehicle_theft", "extortion", "arson", "forgery", "other",
]

IPC_SECTIONS = {
    "murder": "302 IPC", "attempt_to_murder": "307 IPC",
    "kidnapping": "363 IPC, 365 IPC", "robbery": "392 IPC",
    "dacoity": "395 IPC", "theft": "379 IPC",
    "burglary": "454 IPC, 457 IPC", "cheating": "420 IPC",
    "fraud": "420 IPC, 406 IPC", "cyber_crime": "66C IT Act, 66D IT Act",
    "drug_offence": "20 NDPS Act, 22 NDPS Act", "assault": "323 IPC, 324 IPC",
    "sexual_assault": "376 IPC", "domestic_violence": "498A IPC, DV Act",
    "motor_vehicle_theft": "379 IPC, 411 IPC", "extortion": "384 IPC",
    "arson": "435 IPC, 436 IPC", "forgery": "468 IPC, 471 IPC",
    "other": "Varies",
}

FIR_STATUSES   = ["registered", "under_investigation", "chargesheeted", "closed", "transferred", "final_report"]
STATUS_WEIGHTS = [5, 35, 25, 20, 5, 10]
RANKS  = ["constable", "head_constable", "asi", "si", "psi", "pi", "dysp", "sp"]
ROLES  = ["officer", "officer", "officer", "supervisor", "analyst"]
GENDERS = ["Male", "Male", "Male", "Female", "Female", "Other"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rand_date(start_year: int = 2018, end_year: int = 2024) -> datetime:
    start = datetime(start_year, 1, 1, tzinfo=timezone.utc)
    end   = datetime(end_year, 12, 31, tzinfo=timezone.utc)
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))


def rand_phone() -> str:
    return f"+91{random.randint(6000000000, 9999999999)}"


def execute_batch(cur, sql: str, rows: list, batch: int = 200):
    """Use psycopg2 execute_values for fast bulk inserts."""
    for i in range(0, len(rows), batch):
        psycopg2.extras.execute_values(cur, sql, rows[i: i + batch])


def get_conn():
    """Return a plain (non-pooled) connection with autocommit OFF."""
    # Strip ?sslmode=... style params that psycopg2 doesn't accept in DSN
    dsn = settings.SYNC_DATABASE_URL
    return psycopg2.connect(dsn)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def seed():
    conn = get_conn()
    conn.autocommit = True          # each statement commits immediately
    cur = conn.cursor()

    # ------------------------------------------------------------------
    # Enable pgvector
    # ------------------------------------------------------------------
    print("🌱  Enabling pgvector extension...")
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # ------------------------------------------------------------------
    # Wipe existing data in FK-safe order (autocommit = each runs alone)
    # ------------------------------------------------------------------
    print("🧹  Clearing existing data...")
    for tbl in ["audit_logs", "criminal_links", "firs", "criminals", "officers", "stations"]:
        cur.execute(f"DELETE FROM {tbl};")
        print(f"    cleared {tbl}")

    # ------------------------------------------------------------------
    # 1. Stations
    # ------------------------------------------------------------------
    print("🏛️   Seeding stations...")
    station_ids: dict[str, str] = {}   # district -> str(uuid)
    station_rows = []

    for idx, district in enumerate(SEED_DISTRICTS):
        sid = str(uuid.uuid4())
        station_ids[district] = sid
        code = f"KSP-ST{idx:02d}-001"   # index-based, always unique
        station_rows.append((
            sid,
            f"{district} Central Police Station",
            code,
            district,
            district,
            fake.address().replace("\n", ", ")[:200],
            rand_phone(),
            round(random.uniform(50, 500), 2),
        ))

    execute_batch(
        cur,
        """INSERT INTO stations
           (id, name, code, district, taluk, address, phone, jurisdiction_area_sqkm)
           VALUES %s ON CONFLICT DO NOTHING""",
        station_rows,
    )
    print(f"    inserted {len(station_rows)} stations")

    # Verify stations are actually in DB before proceeding
    cur.execute("SELECT COUNT(*) FROM stations;")
    count = cur.fetchone()[0]
    print(f"    verified {count} stations in DB")
    assert count == len(station_rows), "Station insert failed!"

    # ------------------------------------------------------------------
    # 2. Officers
    # ------------------------------------------------------------------
    print("👮  Seeding officers...")
    officer_ids: list[tuple[str, str]] = []   # (str_uuid, district)
    officer_rows = []

    admin_id = str(uuid.uuid4())
    first_district = SEED_DISTRICTS[0]
    officer_rows.append((
        admin_id, "KSP-ADMIN-001", "Admin Officer", "admin@ksp.gov.in",
        pwd_context.hash("Admin@1234"),
        "sp", "admin",
        station_ids[first_district], first_district, True,
    ))
    officer_ids.append((admin_id, first_district))

    for i, district in enumerate(SEED_DISTRICTS):
        for j in range(3):
            oid = str(uuid.uuid4())
            badge = f"KSP-D{i:02d}-{100 + j}"
            officer_rows.append((
                oid, badge, fake.name(),
                f"officer_{i}_{j}@ksp.gov.in",
                pwd_context.hash("Officer@1234"),
                random.choice(RANKS), random.choice(ROLES),
                station_ids[district], district, True,
            ))
            officer_ids.append((oid, district))

    execute_batch(
        cur,
        """INSERT INTO officers
           (id, badge_number, full_name, email, hashed_password,
            rank, role, station_id, jurisdiction_district, is_active)
           VALUES %s ON CONFLICT DO NOTHING""",
        officer_rows,
    )

    cur.execute("SELECT COUNT(*) FROM officers;")
    count = cur.fetchone()[0]
    print(f"    verified {count} officers in DB")
    assert count == len(officer_rows), f"Officer insert failed! Expected {len(officer_rows)}, got {count}"

    # ------------------------------------------------------------------
    # 3. Criminals
    # ------------------------------------------------------------------
    print("🦹  Seeding criminals (3 000)...")
    NUM_CRIMINALS = 3_000
    criminal_ids: list[str] = []
    criminal_rows = []

    for i in range(NUM_CRIMINALS):
        cid = str(uuid.uuid4())
        criminal_ids.append(cid)
        criminal_rows.append((
            cid,
            f"KSP-CRM-{i+1:06d}",
            fake.name(),
            fake.name() if random.random() < 0.3 else None,
            fake.date_of_birth(minimum_age=18, maximum_age=65) if random.random() > 0.05 else None,
            random.choice(GENDERS),
            "Indian",
            random.choice(KARNATAKA_DISTRICTS),
            "Karnataka",
            fake.address().replace("\n", ", ")[:300],
            random.random() < 0.15,
            False,
            0,
        ))

    execute_batch(
        cur,
        """INSERT INTO criminals
           (id, ksp_criminal_id, full_name, alias, date_of_birth,
            gender, nationality, district, state, present_address,
            is_repeat_offender, is_wanted, total_cases)
           VALUES %s ON CONFLICT DO NOTHING""",
        criminal_rows,
    )

    cur.execute("SELECT COUNT(*) FROM criminals;")
    count = cur.fetchone()[0]
    print(f"    verified {count} criminals in DB")
    assert count == NUM_CRIMINALS, "Criminal insert failed!"

    # ------------------------------------------------------------------
    # 4. FIRs  +  CriminalLinks
    # ------------------------------------------------------------------
    print("📋  Seeding 10 500 FIRs and criminal links (this takes a moment)...")
    NUM_FIRS = 10_500
    fir_rows  = []
    link_rows = []

    criminal_case_count: dict[str, int] = {cid: 0 for cid in criminal_ids}
    fir_counter: dict[str, int] = {d: 1 for d in SEED_DISTRICTS}
    repeat_pool = random.sample(criminal_ids, k=int(NUM_CRIMINALS * 0.15))

    officer_by_district: dict[str, list[str]] = {}
    for oid, district in officer_ids:
        officer_by_district.setdefault(district, []).append(oid)

    for _ in range(NUM_FIRS):
        fid      = str(uuid.uuid4())
        district = random.choice(SEED_DISTRICTS)
        station_id = station_ids[district]
        year     = random.randint(2018, 2024)
        seq      = fir_counter[district]
        fir_counter[district] += 1
        fir_number = f"CR-D{SEED_DISTRICTS.index(district):02d}-{seq:04d}/{year}"

        category   = random.choice(CRIME_CATEGORIES)
        status     = random.choices(FIR_STATUSES, weights=STATUS_WEIGHTS)[0]
        incident_dt = rand_date(year, year)

        io_id = random.choice(officer_by_district.get(district, [officer_ids[0][0]]))

        fir_rows.append((
            fid, fir_number, year,
            station_id, io_id,
            category, IPC_SECTIONS.get(category, "Varies"),
            status, incident_dt,
            fake.street_address(), district,
            fake.name() if random.random() > 0.1 else None,
            rand_phone() if random.random() > 0.3 else None,
            fake.text(max_nb_chars=300),
            round(random.uniform(0, 500000), 2)
                if category in ("theft","burglary","robbery","dacoity","fraud","cheating") else None,
            random.random() < 0.05,
            random.random() < 0.08,
        ))

        num_accused = random.choices([1,2,3,4,5,6], weights=[40,25,15,10,6,4])[0]

        accused_pool: list[str] = []
        for _ in range(num_accused):
            accused_pool.append(
                random.choice(repeat_pool) if random.random() < 0.30 else random.choice(criminal_ids)
            )

        seen: set[str] = set()
        unique_accused: list[str] = []
        for cid in accused_pool:
            if cid not in seen:
                seen.add(cid)
                unique_accused.append(cid)

        link_id_list: list[str] = []
        for idx, cid in enumerate(unique_accused):
            lid = str(uuid.uuid4())
            link_id_list.append(lid)
            role = "main_accused" if idx == 0 else random.choice(["co_accused","co_accused","abettor","suspect"])
            arr_status = random.choices(
                ["not_arrested","arrested","absconding","bailed","convicted"],
                weights=[20,35,15,20,10],
            )[0]
            arr_date = (incident_dt + timedelta(days=random.randint(1, 90))).isoformat() \
                if arr_status in ("arrested","bailed","convicted") else None
            criminal_case_count[cid] += 1
            link_rows.append((lid, fid, cid, role, arr_status, arr_date, None, None))

        # back-fill known_associates_ids
        if len(link_id_list) > 1:
            start = len(link_rows) - len(link_id_list)
            for i_link in range(len(link_id_list)):
                associates = [x for j, x in enumerate(link_id_list) if j != i_link]
                row = link_rows[start + i_link]
                link_rows[start + i_link] = row[:-1] + (json.dumps(associates),)

    execute_batch(
        cur,
        """INSERT INTO firs
           (id, fir_number, year, station_id, investigating_officer_id,
            crime_category, sections_applied, status, incident_date,
            incident_location, district, complainant_name, complainant_phone,
            description, property_value, is_organized_crime, is_inter_district)
           VALUES %s ON CONFLICT DO NOTHING""",
        fir_rows,
    )

    cur.execute("SELECT COUNT(*) FROM firs;")
    print(f"    verified {cur.fetchone()[0]} FIRs in DB")

    execute_batch(
        cur,
        """INSERT INTO criminal_links
           (id, fir_id, criminal_id, role, arrest_status,
            arrest_date, role_notes, known_associates_ids)
           VALUES %s ON CONFLICT DO NOTHING""",
        link_rows,
    )

    cur.execute("SELECT COUNT(*) FROM criminal_links;")
    print(f"    verified {cur.fetchone()[0]} criminal links in DB")

    # ------------------------------------------------------------------
    # 5. Update case counts
    # ------------------------------------------------------------------
    print("🔢  Updating criminal case counts...")
    update_rows = [
        (count, count > 1, cid)
        for cid, count in criminal_case_count.items()
        if count > 0
    ]
    psycopg2.extras.execute_values(
        cur,
        "UPDATE criminals SET total_cases = data.c, is_repeat_offender = data.r "
        "FROM (VALUES %s) AS data(c, r, id) WHERE criminals.id = data.id::uuid",
        [(c, r, i) for c, r, i in update_rows],
    )

    cur.close()
    conn.close()

    print(f"\n✅  Seeding complete!")
    print(f"   Stations       : {len(station_rows)}")
    print(f"   Officers       : {len(officer_rows)}")
    print(f"   Criminals      : {NUM_CRIMINALS}")
    print(f"   FIRs           : {len(fir_rows)}")
    print(f"   Criminal links : {len(link_rows)}")
    print("\n🔑  Default admin credentials:")
    print("     Email   : admin@ksp.gov.in")
    print("     Password: Admin@1234")


if __name__ == "__main__":
    seed()
