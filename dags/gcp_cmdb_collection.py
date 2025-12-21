from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import os

# GCP 프로젝트 설정
GCP_PROJECTS = ["your-gcp-project-id"]  # 실제 GCP 프로젝트 ID로 변경
S3_BUCKET = "mwaa-cmdb-bucket"

def collect_gcp_iam_policies(**context):
    """GCP IAM 정책 수집"""
    data = {}
    for project in GCP_PROJECTS:
        try:
            # Google Cloud IAM API 호출 로직
            # 실제 구현 시 google-cloud-iam 라이브러리 사용
            data[project] = {
                'iam_policies': [],
                'service_accounts': [],
                'roles': []
            }
            print(f"Collected IAM policies for project: {project}")
        except Exception as e:
            print(f"Error collecting GCP IAM policies for {project}: {e}")
    
    with open('/tmp/gcp_iam_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_gcp_compute_policies(**context):
    """GCP Compute Engine 정책 수집"""
    data = {}
    for project in GCP_PROJECTS:
        try:
            # Google Cloud Compute API 호출 로직
            data[project] = {
                'instances': [],
                'firewall_rules': [],
                'networks': []
            }
            print(f"Collected Compute policies for project: {project}")
        except Exception as e:
            print(f"Error collecting GCP Compute policies for {project}: {e}")
    
    with open('/tmp/gcp_compute_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_gcp_storage_policies(**context):
    """GCP Storage 정책 수집"""
    data = {}
    for project in GCP_PROJECTS:
        try:
            # Google Cloud Storage API 호출 로직
            data[project] = {
                'buckets': [],
                'bucket_policies': []
            }
            print(f"Collected Storage policies for project: {project}")
        except Exception as e:
            print(f"Error collecting GCP Storage policies for {project}: {e}")
    
    with open('/tmp/gcp_storage_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def upload_gcp_data_to_s3(**context):
    """수집된 GCP 데이터를 S3에 업로드"""
    import boto3
    
    s3 = boto3.client('s3')
    execution_date = context['execution_date'].strftime('%Y%m%d')
    
    files = [
        'gcp_iam_policies.json',
        'gcp_compute_policies.json',
        'gcp_storage_policies.json'
    ]
    
    for file in files:
        try:
            s3.upload_file(
                f'/tmp/{file}',
                S3_BUCKET,
                f'gcp-policies/{execution_date}/{file}'
            )
            print(f"Uploaded {file} to S3")
        except Exception as e:
            print(f"Error uploading {file}: {e}")

with DAG(
    'gcp_cmdb_collection',
    default_args={
        'owner': 'data-team',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5)
    },
    description='GCP CMDB 데이터 수집',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1,
    tags=['gcp', 'cmdb', 'governance']
) as dag:

    # GCP 정책 수집 Task들
    gcp_iam_task = PythonOperator(
        task_id='collect_gcp_iam_policies',
        python_callable=collect_gcp_iam_policies
    )
    
    gcp_compute_task = PythonOperator(
        task_id='collect_gcp_compute_policies',
        python_callable=collect_gcp_compute_policies
    )
    
    gcp_storage_task = PythonOperator(
        task_id='collect_gcp_storage_policies',
        python_callable=collect_gcp_storage_policies
    )

    # S3 업로드
    gcp_upload_task = PythonOperator(
        task_id='upload_gcp_data_to_s3',
        python_callable=upload_gcp_data_to_s3
    )

    # Task 의존성 정의
    [gcp_iam_task, gcp_compute_task, gcp_storage_task] >> gcp_upload_task