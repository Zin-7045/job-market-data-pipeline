import pandas as pd
import json
import os
from datetime import datetime

INPUT_FILE = 'data/processed/clean_ai_ml_data_jobs.csv'
OUTPUT_FILE = 'data/processed/metrics_summary.json'

def generate_metrics():
    print(f"Loading: {INPUT_FILE}")

    if not os.path.exists(INPUT_FILE):
        print("Error: Cleaned CSV not found. Ensure KNIME ran successfully.")
        return

    try:
        df = pd.read_csv(INPUT_FILE, encoding='latin1')
    except Exception:
        df = pd.read_csv(INPUT_FILE, encoding='utf-8', errors='replace')

    entry_level_count = int(len(df[df['experience_bracket'] == '0-1'])) if 'experience_bracket' in df.columns else 0

    if 'remote_status' in df.columns:
        remote_counts = df['remote_status'].value_counts()
        remote = int(remote_counts.get('Remote', 0))
        onsite = int(remote_counts.get('On-site', 0))
        hybrid = int(remote_counts.get('Hybrid', 0))
    else:
        remote, onsite, hybrid = 0, 0, 0

    avg_salary = 0
    if 'salary_mid_usd' in df.columns:
        valid_salary = df['salary_mid_usd'].dropna()
        if len(valid_salary) > 0:
            avg_salary = round(valid_salary.mean(), 2)

    source_counts = df['source'].value_counts().to_dict() if 'source' in df.columns else {}

    metrics = {
        "status": "Success",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_jobs": int(len(df)),
        "jobs_by_source": source_counts,
        "remote_ratio": {"Remote": remote, "On-site": onsite, "Hybrid": hybrid},
        "entry_level_0_to_1_jobs": entry_level_count,
        "average_salary_usd": avg_salary,
        "top_category": df['job_category_clean'].value_counts().idxmax() if 'job_category_clean' in df.columns else "N/A"
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(metrics, f, indent=4)

    print(f"Success! Metrics saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_metrics()
