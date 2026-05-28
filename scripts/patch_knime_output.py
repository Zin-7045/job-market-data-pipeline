import pandas as pd
import os

OUTPUT_FILE = 'data/processed/clean_ai_ml_data_jobs.csv'

def patch_data():
    if not os.path.exists(OUTPUT_FILE):
        print("File not found for patching.")
        return

    try:
        df = pd.read_csv(OUTPUT_FILE, encoding='latin1')
    except:
        df = pd.read_csv(OUTPUT_FILE, encoding='utf-8', errors='replace')

    if 'salary_min_clean' in df.columns:
        df['salary_min_clean'] = pd.to_numeric(df['salary_min_clean'], errors='coerce').fillna(0)
    else:
        df['salary_min_clean'] = 0

    if 'salary_max_clean' in df.columns:
        df['salary_max_clean'] = pd.to_numeric(df['salary_max_clean'], errors='coerce').fillna(0)
    else:
        df['salary_max_clean'] = 0

    if 'currency_raw' not in df.columns:
        df['currency_raw'] = 'USD'

    def convert_to_usd(row, col):
        val = row[col]
        currency = str(row['currency_raw']).upper()
        if currency == 'EUR': return val * 1.08
        if currency == 'GBP': return val * 1.25
        if currency == 'PKR': return val * 0.0036
        return val

    df['salary_min_usd'] = df.apply(lambda r: convert_to_usd(r, 'salary_min_clean'), axis=1)
    df['salary_max_usd'] = df.apply(lambda r: convert_to_usd(r, 'salary_max_clean'), axis=1)

    df['salary_mid_usd'] = df.apply(
        lambda r: (r['salary_min_usd'] + r['salary_max_usd']) / 2 if r['salary_min_usd'] > 0 and r['salary_max_usd'] > 0 else None,
        axis=1
    )

    def extract_skills(desc):
        if pd.isna(desc): return ""
        desc = str(desc).lower()
        skills = []
        if 'python' in desc: skills.append('Python')
        if 'sql' in desc: skills.append('SQL')
        if 'tableau' in desc: skills.append('Tableau')
        if 'machine learning' in desc or ' ml ' in desc: skills.append('ML')
        if 'airflow' in desc: skills.append('Airflow')
        if 'dbt' in desc: skills.append('dbt')
        if 'power bi' in desc: skills.append('Power BI')
        if 'aws' in desc: skills.append('AWS')
        return ", ".join(skills)

    if 'description_clean' in df.columns:
        df['extracted_skills'] = df['description_clean'].apply(extract_skills)
    else:
        df['extracted_skills'] = ""

    df.to_csv(OUTPUT_FILE, index=False)
    print("Patched KNIME output with USD salaries and extracted skills.")

if __name__ == '__main__':
    patch_data()
