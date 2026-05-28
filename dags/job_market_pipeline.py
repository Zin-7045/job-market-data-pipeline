from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from pathlib import Path

# Project root (parent of dags/ directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_PATH = PROJECT_ROOT / 'scripts'
KNIME_EXE = r'"C:\Program Files\KNIME\knime.exe"'
KNIME_WF = PROJECT_ROOT / 'knime_workflow' / 'job_market_cleaning.knwf'

default_args = {
    'owner': 'Muhammad Taha',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'job_market_pipeline',
    default_args=default_args,
    description='Automated Job Market Pipeline: Scrape -> Merge -> Clean -> Metrics',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # 1. Extraction Layer (Parallel)
    t1 = BashOperator(task_id='ext_arbeitnow', bash_command=f'python "{SCRIPTS_PATH / "extract_arbeitnow.py"}"')
    t2 = BashOperator(task_id='ext_remoteok', bash_command=f'python "{SCRIPTS_PATH / "extract_remoteok.py"}"')
    t3 = BashOperator(task_id='ext_himalayas', bash_command=f'python "{SCRIPTS_PATH / "extract_himalayas.py"}"')
    t4 = BashOperator(task_id='ext_remotejobs', bash_command=f'python "{SCRIPTS_PATH / "extract_remotejobs.py"}"')

    # 2. Consolidation Layer
    t5 = BashOperator(task_id='merge_sources', bash_command=f'python "{SCRIPTS_PATH / "merge_sources.py"}"')

    # 3. Cleaning Layer (Automated KNIME Workflow)
    t6 = BashOperator(
        task_id='run_knime_workflow',
        bash_command=f'{KNIME_EXE} -nosplash -application org.knime.product.KNIME_BATCH_APPLICATION -workflowFile="{KNIME_WF}"'
    )

    # 3b. Patch KNIME Output
    t6b = BashOperator(task_id='patch_knime_output', bash_command=f'python "{SCRIPTS_PATH / "patch_knime_output.py"}"')

    # 4. Validation Layer
    t7 = BashOperator(task_id='validate_clean_output', bash_command=f'python "{SCRIPTS_PATH / "validate_outputs.py"}"')

    # 5. Reporting Layer
    t8 = BashOperator(task_id='calculate_metrics', bash_command=f'python "{SCRIPTS_PATH / "calculate_metrics.py"}"')

    # 6. Notification & Archive Layer
    t9 = BashOperator(task_id='trigger_n8n_workflow', bash_command='curl -X POST http://localhost:5678/webhook/job-market-trigger || echo "n8n webhook failed, but continuing"')
    t10 = BashOperator(task_id='archive_outputs', bash_command='echo "Archiving outputs..."')

    # Define Workflow Dependencies
    [t1, t2, t3, t4] >> t5 >> t6 >> t6b >> t7 >> t8 >> t9 >> t10