import pandas as pd
import os
import datetime

def merge_sources():
    print("=== Merging All Sources ===")

    scrape_date = datetime.date.today().isoformat()
    os.makedirs("data/merged", exist_ok=True)

    # ── 1. Load all 4 raw files ──────────────────────────────────────────────

    dfs = []

    files = {
        "Arbeitnow":     "data/raw/raw_arbeitnow_jobs.csv",
        "RemoteOK":      "data/raw/raw_remoteok_jobs.csv",
        "Himalayas":     "data/raw/raw_himalayas_jobs.csv",
        "RemoteJobs.org":"data/raw/raw_remotejobs_jobs.csv",
    }

    for source, path in files.items():
        if os.path.exists(path):
            df = pd.read_csv(path, dtype=str).fillna("")
            print(f"  Loaded {len(df)} rows from {source}")
            dfs.append(df)
        else:
            print(f"  WARNING: {path} not found — skipping")

    if not dfs:
        print("ERROR: No files loaded. Run extraction scripts first.")
        return

    # ── 2. Standardize each dataframe to common schema ───────────────────────

    standard_cols = [
        "source", "job_id", "title", "company_name",
        "location_raw", "remote_status", "job_type",
        "category_raw", "tags_raw", "description",
        "publication_date", "job_url",
        "salary_text_raw", "salary_min_raw", "salary_max_raw",
        "currency_raw", "scrape_date"
    ]

    standardized = []

    for df in dfs:
        # Add any missing columns with empty string
        for col in standard_cols:
            if col not in df.columns:
                df[col] = ""

        # Fix Himalayas pubDate → publication_date
        if "pubDate" in df.columns:
            mask = df["publication_date"] == ""
            df.loc[mask, "publication_date"] = df.loc[mask, "pubDate"]

        # Fix Himalayas currency field
        if "currency" in df.columns:
            mask = df["currency_raw"] == ""
            df.loc[mask, "currency_raw"] = df.loc[mask, "currency"]

        # Keep only standard columns
        df = df[standard_cols].copy()
        standardized.append(df)

    # ── 3. Concatenate all sources ───────────────────────────────────────────

    merged = pd.concat(standardized, ignore_index=True)
    print(f"\nTotal rows before deduplication: {len(merged)}")

    # ── 4. Deduplicate ───────────────────────────────────────────────────────

    before = len(merged)

    # Primary dedup: by job_url (most reliable)
    url_mask = merged["job_url"] != ""
    dedup_by_url = merged[url_mask].drop_duplicates(subset=["job_url"], keep="first")
    no_url = merged[~url_mask]

    # Secondary dedup for rows without URL: title + company + source
    dedup_no_url = no_url.drop_duplicates(
        subset=["title", "company_name", "source"], keep="first"
    )

    merged = pd.concat([dedup_by_url, dedup_no_url], ignore_index=True)
    after = len(merged)

    print(f"Duplicates removed: {before - after}")
    print(f"Total rows after deduplication: {after}")

    # ── 5. Clean up basic fields ─────────────────────────────────────────────

    # Strip whitespace from all string fields
    for col in merged.columns:
        merged[col] = merged[col].astype(str).str.strip()

    # Replace "nan" strings with empty string
    merged = merged.replace("nan", "")

    # Standardize remote_status values
    def fix_remote(val):
        val = str(val).strip().lower()
        if val in ["remote", "true", "yes", "1"]:
            return "Remote"
        elif val in ["on-site", "onsite", "office", "false", "no", "0"]:
            return "On-site"
        elif "hybrid" in val:
            return "Hybrid"
        else:
            return "Remote" if val == "" else "Unknown"

    merged["remote_status"] = merged["remote_status"].apply(fix_remote)

    # Standardize job_type values
    def fix_job_type(val):
        val = str(val).strip().lower()
        if "full" in val:
            return "Full-time"
        elif "part" in val:
            return "Part-time"
        elif "contract" in val:
            return "Contract"
        elif "freelance" in val:
            return "Freelance"
        elif "intern" in val:
            return "Internship"
        else:
            return "Unknown"

    merged["job_type"] = merged["job_type"].apply(fix_job_type)

    # ── 6. Show source breakdown ─────────────────────────────────────────────

    print("\n--- Jobs by Source ---")
    print(merged["source"].value_counts().to_string())

    print("\n--- Remote Status Breakdown ---")
    print(merged["remote_status"].value_counts().to_string())

    print("\n--- Job Type Breakdown ---")
    print(merged["job_type"].value_counts().to_string())

    # ── 7. Save merged file ──────────────────────────────────────────────────

    output_path = "data/merged/merged_raw_jobs.csv"
    merged.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nSaved merged file: {output_path}")
    print(f"Total jobs in merged file: {len(merged)}")
    print("=== Merge DONE ===\n")

if __name__ == "__main__":
    merge_sources()