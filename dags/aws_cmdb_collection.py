from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3
import json
import os

# 계정 및 리전 설정
ACCOUNTS = ["123456789123"]
REGIONS = ["us-east-1", "us-west-2", "us-east-2", "ap-northeast-1"]
S3_BUCKET = "mwaa-cmdb-bucket"

def collect_identity_policies(**context):
    """IAM, Organizations, Cognito"""
    data = {}
    for account in ACCOUNTS:
        try:
            iam = boto3.client('iam')
            # IAM 정책 수집
            policies = iam.list_policies(Scope='Local')['Policies']
            roles = iam.list_roles()['Roles']
            users = iam.list_users()['Users']
            groups = iam.list_groups()['Groups']
            
            data[account] = {
                'policies': policies,
                'roles': roles,
                'users': users,
                'groups': groups
            }
        except Exception as e:
            print(f"Error collecting identity policies for {account}: {e}")
    
    # 임시 파일로 저장
    with open('/tmp/identity_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_storage_policies(**context):
    """S3, EFS, FSx, Glacier"""
    data = {}
    for account in ACCOUNTS:
        for region in REGIONS:
            try:
                s3 = boto3.client('s3', region_name=region)
                efs = boto3.client('efs', region_name=region)
                
                # S3 버킷 정책 수집
                buckets = s3.list_buckets()['Buckets']
                bucket_policies = {}
                for bucket in buckets:
                    try:
                        policy = s3.get_bucket_policy(Bucket=bucket['Name'])
                        bucket_policies[bucket['Name']] = policy['Policy']
                    except:
                        bucket_policies[bucket['Name']] = None
                
                # EFS 파일 시스템
                file_systems = efs.describe_file_systems()['FileSystems']
                
                data[f"{account}_{region}"] = {
                    'buckets': buckets,
                    'bucket_policies': bucket_policies,
                    'file_systems': file_systems
                }
            except Exception as e:
                print(f"Error collecting storage policies for {account}_{region}: {e}")
    
    with open('/tmp/storage_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_compute_policies(**context):
    """EC2, Lambda, ECS, EKS, Auto Scaling"""
    data = {}
    for account in ACCOUNTS:
        for region in REGIONS:
            try:
                ec2 = boto3.client('ec2', region_name=region)
                lambda_client = boto3.client('lambda', region_name=region)
                
                # EC2 보안 그룹
                security_groups = ec2.describe_security_groups()['SecurityGroups']
                instances = ec2.describe_instances()['Reservations']
                
                # Lambda 함수
                functions = lambda_client.list_functions()['Functions']
                
                data[f"{account}_{region}"] = {
                    'security_groups': security_groups,
                    'instances': instances,
                    'lambda_functions': functions
                }
            except Exception as e:
                print(f"Error collecting compute policies for {account}_{region}: {e}")
    
    with open('/tmp/compute_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_database_policies(**context):
    """RDS, DynamoDB, ElastiCache"""
    data = {}
    for account in ACCOUNTS:
        for region in REGIONS:
            try:
                rds = boto3.client('rds', region_name=region)
                dynamodb = boto3.client('dynamodb', region_name=region)
                
                # RDS 인스턴스
                db_instances = rds.describe_db_instances()['DBInstances']
                
                # DynamoDB 테이블
                tables = dynamodb.list_tables()['TableNames']
                
                data[f"{account}_{region}"] = {
                    'rds_instances': db_instances,
                    'dynamodb_tables': tables
                }
            except Exception as e:
                print(f"Error collecting database policies for {account}_{region}: {e}")
    
    with open('/tmp/database_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_network_policies(**context):
    """VPC, CloudFront, Route53, ELB"""
    data = {}
    for account in ACCOUNTS:
        for region in REGIONS:
            try:
                ec2 = boto3.client('ec2', region_name=region)
                elbv2 = boto3.client('elbv2', region_name=region)
                
                # VPC 정보
                vpcs = ec2.describe_vpcs()['Vpcs']
                subnets = ec2.describe_subnets()['Subnets']
                route_tables = ec2.describe_route_tables()['RouteTables']
                
                # Load Balancers
                load_balancers = elbv2.describe_load_balancers()['LoadBalancers']
                
                data[f"{account}_{region}"] = {
                    'vpcs': vpcs,
                    'subnets': subnets,
                    'route_tables': route_tables,
                    'load_balancers': load_balancers
                }
            except Exception as e:
                print(f"Error collecting network policies for {account}_{region}: {e}")
    
    with open('/tmp/network_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_analytics_policies(**context):
    """Kinesis, Glue, Athena, QuickSight"""
    data = {}
    for account in ACCOUNTS:
        for region in REGIONS:
            try:
                kinesis = boto3.client('kinesis', region_name=region)
                glue = boto3.client('glue', region_name=region)
                
                # Kinesis 스트림
                streams = kinesis.list_streams()['StreamNames']
                
                # Glue 데이터베이스
                databases = glue.get_databases()['DatabaseList']
                
                data[f"{account}_{region}"] = {
                    'kinesis_streams': streams,
                    'glue_databases': databases
                }
            except Exception as e:
                print(f"Error collecting analytics policies for {account}_{region}: {e}")
    
    with open('/tmp/analytics_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_security_policies(**context):
    """KMS, Secrets Manager, ACM, WAF"""
    data = {}
    for account in ACCOUNTS:
        for region in REGIONS:
            try:
                kms = boto3.client('kms', region_name=region)
                secrets = boto3.client('secretsmanager', region_name=region)
                
                # KMS 키
                keys = kms.list_keys()['Keys']
                
                # Secrets Manager
                secret_list = secrets.list_secrets()['SecretList']
                
                data[f"{account}_{region}"] = {
                    'kms_keys': keys,
                    'secrets': secret_list
                }
            except Exception as e:
                print(f"Error collecting security policies for {account}_{region}: {e}")
    
    with open('/tmp/security_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_devops_policies(**context):
    """CodeCommit, CodeBuild, CodePipeline"""
    data = {}
    for account in ACCOUNTS:
        for region in REGIONS:
            try:
                codecommit = boto3.client('codecommit', region_name=region)
                codebuild = boto3.client('codebuild', region_name=region)
                
                # CodeCommit 리포지토리
                repos = codecommit.list_repositories()['repositories']
                
                # CodeBuild 프로젝트
                projects = codebuild.list_projects()['projects']
                
                data[f"{account}_{region}"] = {
                    'codecommit_repos': repos,
                    'codebuild_projects': projects
                }
            except Exception as e:
                print(f"Error collecting devops policies for {account}_{region}: {e}")
    
    with open('/tmp/devops_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_messaging_policies(**context):
    """SNS, SQS, EventBridge"""
    data = {}
    for account in ACCOUNTS:
        for region in REGIONS:
            try:
                sns = boto3.client('sns', region_name=region)
                sqs = boto3.client('sqs', region_name=region)
                
                # SNS 토픽
                topics = sns.list_topics()['Topics']
                
                # SQS 큐
                queues = sqs.list_queues().get('QueueUrls', [])
                
                data[f"{account}_{region}"] = {
                    'sns_topics': topics,
                    'sqs_queues': queues
                }
            except Exception as e:
                print(f"Error collecting messaging policies for {account}_{region}: {e}")
    
    with open('/tmp/messaging_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def collect_monitoring_policies(**context):
    """CloudWatch, CloudTrail, Config"""
    data = {}
    for account in ACCOUNTS:
        for region in REGIONS:
            try:
                cloudwatch = boto3.client('cloudwatch', region_name=region)
                cloudtrail = boto3.client('cloudtrail', region_name=region)
                
                # CloudWatch 알람
                alarms = cloudwatch.describe_alarms()['MetricAlarms']
                
                # CloudTrail
                trails = cloudtrail.describe_trails()['trailList']
                
                data[f"{account}_{region}"] = {
                    'cloudwatch_alarms': alarms,
                    'cloudtrail_trails': trails
                }
            except Exception as e:
                print(f"Error collecting monitoring policies for {account}_{region}: {e}")
    
    with open('/tmp/monitoring_policies.json', 'w') as f:
        json.dump(data, f, default=str)

def upload_to_s3(**context):
    """수집된 데이터를 S3에 업로드"""
    s3 = boto3.client('s3')
    execution_date = context['execution_date'].strftime('%Y%m%d')
    
    files = [
        'identity_policies.json',
        'storage_policies.json', 
        'compute_policies.json',
        'database_policies.json',
        'network_policies.json',
        'analytics_policies.json',
        'security_policies.json',
        'devops_policies.json',
        'messaging_policies.json',
        'monitoring_policies.json'
    ]
    
    for file in files:
        try:
            s3.upload_file(
                f'/tmp/{file}',
                S3_BUCKET,
                f'aws-policies/{execution_date}/{file}'
            )
            print(f"Uploaded {file} to S3")
        except Exception as e:
            print(f"Error uploading {file}: {e}")

with DAG(
    'aws_cmdb_collection',
    default_args={
        'owner': 'data-team',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': True,
        'email_on_retry': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5)
    },
    description='AWS CMDB 데이터 수집',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1,
    tags=['aws', 'cmdb', 'governance']
) as dag:

    # 정책 수집 Task들
    identity_task = PythonOperator(
        task_id='collect_identity_policies',
        python_callable=collect_identity_policies
    )
    
    storage_task = PythonOperator(
        task_id='collect_storage_policies',
        python_callable=collect_storage_policies
    )
    
    compute_task = PythonOperator(
        task_id='collect_compute_policies',
        python_callable=collect_compute_policies
    )
    
    database_task = PythonOperator(
        task_id='collect_database_policies',
        python_callable=collect_database_policies
    )
    
    network_task = PythonOperator(
        task_id='collect_network_policies',
        python_callable=collect_network_policies
    )
    
    analytics_task = PythonOperator(
        task_id='collect_analytics_policies',
        python_callable=collect_analytics_policies
    )
    
    security_task = PythonOperator(
        task_id='collect_security_policies',
        python_callable=collect_security_policies
    )
    
    devops_task = PythonOperator(
        task_id='collect_devops_policies',
        python_callable=collect_devops_policies
    )
    
    messaging_task = PythonOperator(
        task_id='collect_messaging_policies',
        python_callable=collect_messaging_policies
    )
    
    monitoring_task = PythonOperator(
        task_id='collect_monitoring_policies',
        python_callable=collect_monitoring_policies
    )

    # S3 업로드
    upload_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3
    )

    # Task 의존성 정의
    policy_tasks = [
        identity_task, storage_task, compute_task, database_task,
        network_task, analytics_task, security_task, devops_task,
        messaging_task, monitoring_task
    ]
    
    # 모든 정책 수집 완료 후 S3 업로드
    policy_tasks >> upload_task
