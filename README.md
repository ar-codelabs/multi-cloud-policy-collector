# 🔍 MWAA CMDB 수집 파이프라인

AWS MWAA를 사용하여 AWS와 GCP의 정책 및 리소스 정보를 수집하는 CMDB(Configuration Management Database) 파이프라인입니다.

## 📋 프로젝트 개요

멀티 클라우드 환경에서 AWS와 GCP의 정책, 리소스, 보안 설정을 자동으로 수집하여 S3에 저장하는 데이터 파이프라인입니다.

### 🎯 주요 기능

- **AWS 정책 수집**: IAM, S3, EC2, RDS 등 10개 카테고리별 정책 수집
- **GCP 정책 수집**: IAM, Compute, Storage 정책 수집
- **S3 저장**: 수집된 데이터를 날짜별로 파티셔닝하여 저장
- **자동화**: 일일 스케줄 실행

## 🏗️ 아키텍처

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│     AWS     │───▶│     MWAA     │───▶│   S3 CMDB       │
│   Policies  │    │   Pipeline   │    │   Bucket        │
└─────────────┘    └──────────────┘    └─────────────────┘
┌─────────────┐           │
│     GCP     │───────────┘
│   Policies  │
└─────────────┘
```

## 📊 DAG 구성

### 1. AWS CMDB Collection DAG (`aws_cmdb_collection`)

#### Task 구성 (10개)
1. **collect_identity_policies**: IAM, Organizations, Cognito
2. **collect_storage_policies**: S3, EFS, FSx, Glacier
3. **collect_compute_policies**: EC2, Lambda, ECS, EKS
4. **collect_database_policies**: RDS, DynamoDB, ElastiCache
5. **collect_network_policies**: VPC, CloudFront, Route53, ELB
6. **collect_analytics_policies**: Kinesis, Glue, Athena
7. **collect_security_policies**: KMS, Secrets Manager, ACM, WAF
8. **collect_devops_policies**: CodeCommit, CodeBuild, CodePipeline
9. **collect_messaging_policies**: SNS, SQS, EventBridge
10. **collect_monitoring_policies**: CloudWatch, CloudTrail, Config

### 2. GCP CMDB Collection DAG (`gcp_cmdb_collection`)

#### Task 구성
1. **collect_gcp_iam_policies**: GCP IAM 정책
2. **collect_gcp_compute_policies**: Compute Engine 정책
3. **collect_gcp_storage_policies**: Cloud Storage 정책

## 📁 디렉토리 구조

```
.
├── .github/workflows/              # GitHub Actions
│   └── github-actions-sync-to-s3.yml
├── dags/                           # Airflow DAG 파일
│   ├── aws_cmdb_collection.py      # AWS 정책 수집 DAG
│   ├── gcp_cmdb_collection.py      # GCP 정책 수집 DAG
├── docker/                         # 커스텀 Docker 이미지
│   ├── Dockerfile.mwaa_custom
│   └── requirements.txt            # CMDB 관련 패키지 추가
├── local/                          # 로컬 개발 환경
│   ├── docker-compose.yml
│   └── .env                        # CMDB 환경 변수 추가
└── README_CMDB.md                  # 이 파일
```

## 🔧 환경 설정

### 필수 AWS 리소스

| 리소스 | 설명 |
|--------|------|
| **MWAA 환경** | {mwaa-env 입력} |
| **S3 CMDB 버킷** | {s3 버킷 입력} |
| **IAM 권한** | {멀티 계정 접근 권한} |

### 환경 변수 설정

```bash
# CMDB 설정
MWAA_CMDB_BUCKET={s3 버킷 입력}
AWS_ACCOUNTS={멀티 계정 입력}
AWS_REGIONS=us-east-1,us-west-2,us-east-2,ap-northeast-1
GCP_PROJECT_ID=your-gcp-project-id
```

### 계정 및 리전 설정

```python
# AWS 설정
ACCOUNTS = ["123456789123","234567891234"]
REGIONS = ["us-east-1", "us-west-2", "us-east-2", "ap-northeast-1"]

# GCP 설정
GCP_PROJECTS = ["your-gcp-project-id"]
```

## 🚀 MWAA 배포 및 실행

### 1. GitHub Actions 자동 배포
```bash
git add .
git commit -m "Add CMDB collection DAGs"
git push origin main
```

### 2. 로컬 테스트
```bash
cd local/
docker compose up -d
```

### 3. MWAA 웹 UI 확인
- AWS MWAA 콘솔에서 웹 UI 접속
- `aws_cmdb_collection` DAG 활성화
- `gcp_cmdb_collection` DAG 활성화

## 📊 데이터 저장 구조

### S3 버킷 구조 (예시)
```
s3://mwaa-cmdb-bucket/
├── aws-policies/
│   └── 20241201/
│       ├── identity_policies.json
│       ├── storage_policies.json
│       ├── compute_policies.json
│       └── ...
└── gcp-policies/
    └── 20241201/
        ├── gcp_iam_policies.json
        ├── gcp_compute_policies.json
        └── gcp_storage_policies.json
```

## 🔐 필수 IAM 권한

### AWS 권한
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:List*",
                "s3:*",
                "ec2:Describe*",
                "rds:Describe*",
                "lambda:List*",
                "kms:List*",
                "secretsmanager:List*",
                "cloudwatch:Describe*",
                "cloudtrail:Describe*"
            ],
            "Resource": "*"
        }
    ]
}
```




## 📈 모니터링

### CloudWatch 메트릭
- DAG 실행 성공/실패율
- Task 실행 시간
- S3 업로드 용량

### 알림 설정 (향후 설정할 수 있음)
- DAG 실패 시 이메일 알림
- 데이터 수집 완료 알림

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
