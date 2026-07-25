"""
ETL Script: Denormalize Police Records CSVs -> track1_dataset.json
=================================================================
Joins CaseMaster, CrimeHead, Unit, District, Accused, and Victim
tables into a single flat JSON array ready for RAG pipeline ingestion.
"""

import os
import json
import pandas as pd

# -- Configuration -------------------------------------------------------------
CSV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalyst_csv_bundle")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "track1_dataset.json")

# -- Helper: safe CSV loader ---------------------------------------------------
def load_csv(filename):
    """Load a CSV from CSV_DIR; raises FileNotFoundError on missing file."""
    path = os.path.join(CSV_DIR, filename)
    try:
        df = pd.read_csv(path, low_memory=False)
        print(f"  [OK] Loaded {filename:<35} -> {len(df):>7,} rows")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Required file not found: {path}\n"
            "Please ensure all CSVs are present in the catalyst_csv_bundle directory."
        )
    except Exception as exc:
        raise RuntimeError(f"Error reading {filename}: {exc}") from exc


# -- Helper: aggregate names per case ------------------------------------------
def aggregate_names(df, name_col, placeholder):
    """
    Group df by CaseMasterID and concatenate name_col values.
    NaN names are replaced with placeholder before joining.
    Returns a Series indexed by CaseMasterID.
    """
    df = df.copy()
    df[name_col] = df[name_col].fillna(placeholder)
    return (
        df.groupby("CaseMasterID")[name_col]
        .apply(lambda names: ", ".join(names.astype(str).str.strip()))
        .rename(name_col)
    )


# -- Helper: clean scalar value ------------------------------------------------
def clean(value, fallback="Unknown"):
    """Return a stripped string or fallback for NaN / None / empty values."""
    if pd.isna(value) or str(value).strip() in ("", "nan", "NaT", "None"):
        return fallback
    return str(value).strip()


# -- Main ETL ------------------------------------------------------------------
def main():
    print("\n" + "=" * 60)
    print("  Police Records ETL  ->  track1_dataset.json")
    print("=" * 60)

    # 1. Load all required tables
    print("\n[1/5] Loading CSV tables ...")
    try:
        case_master = load_csv("CaseMaster.csv")
        crime_head  = load_csv("CrimeHead.csv")
        unit        = load_csv("Unit.csv")
        district    = load_csv("District.csv")
        accused     = load_csv("Accused.csv")
        victim      = load_csv("Victim.csv")
    except (FileNotFoundError, RuntimeError) as err:
        print(f"\n[ERROR] {err}")
        return

    # 2. Crime-type join
    print("\n[2/5] Joining crime type ...")
    case_master["CrimeMajorHeadID"] = pd.to_numeric(
        case_master["CrimeMajorHeadID"], errors="coerce"
    )
    crime_head["CrimeHeadID"] = pd.to_numeric(
        crime_head["CrimeHeadID"], errors="coerce"
    )

    merged = case_master.merge(
        crime_head[["CrimeHeadID", "CrimeGroupName"]],
        left_on="CrimeMajorHeadID",
        right_on="CrimeHeadID",
        how="left",
    )
    print(f"  [OK] After crime-type join: {len(merged):,} rows")

    # 3. Two-step district join
    print("\n[3/5] Joining district (two-step via Unit) ...")
    merged["PoliceStationID"] = pd.to_numeric(merged["PoliceStationID"], errors="coerce")
    unit["UnitID"] = pd.to_numeric(unit["UnitID"], errors="coerce")
    unit["DistrictID"] = pd.to_numeric(unit["DistrictID"], errors="coerce")
    district["DistrictID"] = pd.to_numeric(district["DistrictID"], errors="coerce")

    merged = merged.merge(
        unit[["UnitID", "DistrictID"]],
        left_on="PoliceStationID",
        right_on="UnitID",
        how="left",
    )
    merged = merged.merge(
        district[["DistrictID", "DistrictName"]],
        on="DistrictID",
        how="left",
    )
    print(f"  [OK] After district join:   {len(merged):,} rows")

    # 4. Aggregate accused & victim names
    print("\n[4/5] Aggregating accused and victim names ...")
    accused_agg = aggregate_names(accused, "AccusedName", "Unidentified")
    victim_agg  = aggregate_names(victim,  "VictimName",  "Unidentified")

    merged = merged.merge(accused_agg, on="CaseMasterID", how="left")
    merged = merged.merge(victim_agg,  on="CaseMasterID", how="left")

    merged["AccusedName"] = merged["AccusedName"].fillna("Unidentified")
    merged["VictimName"]  = merged["VictimName"].fillna("Unidentified")
    print(f"  [OK] People aggregation complete: {len(merged):,} rows")

    # 5. Build JSON array
    print("\n[5/5] Building JSON records ...")
    records = []

    for _, row in merged.iterrows():
        brief_facts   = clean(row.get("BriefFacts"),          "No details available")
        accused_names = clean(row.get("AccusedName"),         "Unidentified")
        victim_names  = clean(row.get("VictimName"),          "Unidentified")

        narrative = (
            f"{brief_facts}. "
            f"The accused identified in this case are: {accused_names}. "
            f"The victims involved are: {victim_names}."
        )

        record = {
            "fir_id":     clean(row.get("CrimeNo"),              "Unknown"),
            "crime_type": clean(row.get("CrimeGroupName"),       "Unknown"),
            "district":   clean(row.get("DistrictName"),         "Unknown"),
            "date_filed": clean(row.get("CrimeRegisteredDate"),  "Unknown"),
            "text":       narrative,
        }
        records.append(record)

    # 6. Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fout:
        json.dump(records, fout, ensure_ascii=False, indent=2)

    # Summary
    print("\n" + "=" * 60)
    print(f"  ETL complete!")
    print(f"  Total records processed : {len(records):,}")
    print(f"  Output saved to         : {OUTPUT_FILE}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
