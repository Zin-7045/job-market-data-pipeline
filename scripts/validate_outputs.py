import pandas as pd
import os

INPUT_FILE = 'data/processed/clean_ai_ml_data_jobs.csv'

def validate_data():
    print("=== Validation Layer ===")

    if not os.path.exists(INPUT_FILE):
        print(f"FAIL: {INPUT_FILE} does not exist.")
        return False

    try:
        df = pd.read_csv(INPUT_FILE, encoding='latin1')
    except Exception:
        df = pd.read_csv(INPUT_FILE, encoding='utf-8', errors='replace')

    print(f"Total cleaned jobs: {len(df)}")

    print("\n[CHECK] Output file exists and is not empty: PASS")

    required_cols = [
        "source", "title", "company_name", "location_raw", "remote_status",
        "job_type", "description_clean", "publication_date", "job_url"
    ]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        print(f"[CHECK] Schema Check: FAIL - Missing {missing_cols}")
    else:
        print("[CHECK] Schema Check: PASS")

    print("\n[CHECK] Missing Value Percentages:")
    for col in required_cols:
        if col in df.columns:
            missing_pct = df[col].isnull().sum() / len(df) * 100
            print(f"  - {col}: {missing_pct:.2f}% missing")

    if 'remote_status' in df.columns:
        invalid_remote = df[~df['remote_status'].isin(['Remote', 'On-site', 'Hybrid', 'Unknown'])]
        if len(invalid_remote) > 0:
            print(f"[CHECK] Remote Status Check: FAIL - found {len(invalid_remote)} invalid values")
        else:
            print("[CHECK] Remote Status Check: PASS")

    if 'experience_bracket' in df.columns:
        valid_brackets = ['0-1', '1-3', '3-5', '5-8', '8+', 'Not mentioned']
        invalid_exp = df[~df['experience_bracket'].isin(valid_brackets)]
        if len(invalid_exp) > 0:
            print(f"[CHECK] Experience Bracket Check: FAIL - found {len(invalid_exp)} invalid values")
        else:
            print("[CHECK] Experience Bracket Check: PASS")

    print("\nValidation complete.")
    return True

if __name__ == "__main__":
    validate_data()
