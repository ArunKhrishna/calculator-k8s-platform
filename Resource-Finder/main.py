#!/usr/bin/env python3
"""
AWS Resource Monitor Script - Production Grade Enhanced Version
Comprehensive monitoring and cost optimization tool for AWS resources
"""

import os
import json
import boto3
import gspread
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from google.oauth2.service_account import Credentials
import logging
import pytz
from collections import defaultdict
import re
from botocore.exceptions import ClientError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ResourceInfo:
    """Enhanced data class for resource information"""
    resource_type: str
    resource_id: str
    resource_name: str
    created_time: str
    created_by: str
    state: str
    tags: Dict[str, str]
    usage_info: str
    estimated_cost: str
    region: str
    vpc_id: str = ""
    subnet_id: str = ""
    instance_type: str = ""
    is_unused: bool = False
    is_new: bool = False
    additional_info: str = ""
    # New fields for enhanced monitoring
    security_groups: List[str] = field(default_factory=list)
    public_ip: str = ""
    private_ip: str = ""
    last_accessed: str = ""
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    cost_optimization_suggestions: List[str] = field(default_factory=list)
    risk_level: str = "Low"  # Low, Medium, High
    environment: str = ""  # Production, Staging, Dev, etc.
    owner_email: str = ""
    department: str = ""
    project: str = ""
    backup_status: str = ""
    monitoring_enabled: bool = False
    auto_scaling_enabled: bool = False
    encryption_status: str = ""
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    associated_resources: List[str] = field(default_factory=list)
    termination_protection: bool = False
    data_transfer_cost: str = ""
    storage_optimization: str = ""

class AWSResourceMonitor:
    """Enhanced main class for monitoring AWS resources"""
    
    def __init__(self):
        # AWS Configuration
        self.aws_account_id = os.environ.get('AWS_ACCOUNT_ID')
        self.aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Google Sheets Configuration
        self.spreadsheet_id = os.environ.get('SPREADSHEET_ID')
        
        # Slack Configuration
        self.slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        
        # Initialize AWS clients
        self.session = boto3.Session(
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )

        # Get Google credentials from Secrets Manager
        self.google_creds = self.get_secret_from_aws()
        
        # Initialize all AWS service clients
        self.ec2_client = self.session.client('ec2')
        self.elb_client = self.session.client('elb')
        self.elbv2_client = self.session.client('elbv2')
        self.rds_client = self.session.client('rds')
        self.s3_client = self.session.client('s3')
        self.lambda_client = self.session.client('lambda')
        self.ecs_client = self.session.client('ecs')
        self.eks_client = self.session.client('eks')
        self.cloudtrail_client = self.session.client('cloudtrail')
        self.cloudwatch_client = self.session.client('cloudwatch')
        self.autoscaling_client = self.session.client('autoscaling')
        self.ecr_client = self.session.client('ecr')
        self.iam_client = self.session.client('iam')
        self.sns_client = self.session.client('sns')
        self.sqs_client = self.session.client('sqs')
        self.dynamodb_client = self.session.client('dynamodb')
        self.elasticache_client = self.session.client('elasticache')
        self.redshift_client = self.session.client('redshift')
        self.route53_client = self.session.client('route53')
        self.cloudfront_client = self.session.client('cloudfront')
        self.apigateway_client = self.session.client('apigateway')
        self.backup_client = self.session.client('backup')
        
        # Time configuration
        self.ist = pytz.timezone('Asia/Kolkata')
        self.cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Cost thresholds for optimization
        self.cost_thresholds = {
            'ec2': {'daily': 5, 'monthly': 150},
            'rds': {'daily': 10, 'monthly': 300},
            'unused_threshold': {'daily': 1, 'monthly': 30}
        }
        
        logger.info(f"Initialized Enhanced AWS Resource Monitor for region: {self.aws_region}")

    def get_secret_from_aws(self):
        """Retrieve Google service account credentials from AWS Secrets Manager"""
        secret_name = "google-service-account"
        region_name = "ap-south-1"  # Secret is stored in us-east-1
        
        try:
            client = self.session.client(
                service_name='secretsmanager',
                region_name=region_name
            )
            
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
            
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                logger.info("Successfully retrieved Google credentials from AWS Secrets Manager")
                return json.loads(secret)
            else:
                raise ValueError("Secret is in binary format, expected JSON string")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.error(f"Secret {secret_name} not found")
            elif error_code == 'InvalidRequestException':
                logger.error(f"Invalid request: {e}")
            elif error_code == 'InvalidParameterException':
                logger.error(f"Invalid parameter: {e}")
            elif error_code == 'DecryptionFailure':
                logger.error(f"Decryption failure: {e}")
            elif error_code == 'InternalServiceError':
                logger.error(f"Internal service error: {e}")
            raise
    
    def authenticate_gspread(self):
        """Authenticate with Google Sheets using credentials from Secrets Manager"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_info(
                self.google_creds,
                scopes=scopes
            )
            
            gc = gspread.authorize(creds)
            logger.info("Successfully authenticated with Google Sheets")
            return gc
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            raise    

    def detect_environment_from_tags(self, tags: Dict[str, str]) -> str:
        """Detect environment from resource tags"""
        env_keywords = {
            'production': ['prod', 'production', 'prd'],
            'staging': ['staging', 'stage', 'stg'],
            'development': ['dev', 'development', 'develop'],
            'testing': ['test', 'testing', 'qa'],
            'demo': ['demo', 'poc', 'sandbox']
        }
        
        tag_values = ' '.join([str(v).lower() for v in tags.values()])
        tag_keys = ' '.join([str(k).lower() for k in tags.keys()])
        combined = f"{tag_values} {tag_keys}"
        
        for env, keywords in env_keywords.items():
            for keyword in keywords:
                if keyword in combined:
                    return env.capitalize()
        
        return 'Unknown'

    def analyze_security_compliance(self, instance: dict) -> Dict[str, bool]:
        """Analyze security compliance for EC2 instance"""
        compliance = {
            'public_ip_restricted': not bool(instance.get('PublicIpAddress')),
            'encrypted_volumes': True,
            'imdsv2_enforced': False,
            'monitoring_enabled': instance.get('Monitoring', {}).get('State') == 'enabled',
            'termination_protection': False,
            'security_groups_reviewed': True
        }
        
        # Check volume encryption
        for bdm in instance.get('BlockDeviceMappings', []):
            if 'Ebs' in bdm and not bdm['Ebs'].get('Encrypted', False):
                compliance['encrypted_volumes'] = False
                break
        
        # Check IMDSv2
        metadata_options = instance.get('MetadataOptions', {})
        if metadata_options.get('HttpTokens') == 'required':
            compliance['imdsv2_enforced'] = True
        
        # Check termination protection
        try:
            response = self.ec2_client.describe_instance_attribute(
                InstanceId=instance['InstanceId'],
                Attribute='disableApiTermination'
            )
            compliance['termination_protection'] = response.get('DisableApiTermination', {}).get('Value', False)
        except:
            pass
        
        return compliance

    def get_cost_optimization_suggestions(self, resource: ResourceInfo) -> List[str]:
        """Generate cost optimization suggestions"""
        suggestions = []
        
        if resource.resource_type == 'EC2 Instance':
            # Check for underutilization
            if 'Avg CPU' in resource.usage_info:
                avg_cpu = float(re.search(r'Avg CPU.*?: ([\d.]+)%', resource.usage_info).group(1))
                if avg_cpu < 5:
                    suggestions.append("Consider downsizing instance or using Spot/Savings Plans")
                elif avg_cpu < 20:
                    suggestions.append("Instance appears underutilized - review sizing")
            
            # Check for old generation instances
            if resource.instance_type.startswith(('t2', 'm3', 'm4', 'c3', 'c4')):
                suggestions.append("Migrate to newer generation instances for better price/performance")
            
            # Check for missing reserved instances
            if resource.environment == 'Production' and resource.state == 'running':
                suggestions.append("Consider Reserved Instances or Savings Plans for production workloads")
        
        elif resource.resource_type == 'EBS Volume':
            if 'gp2' in resource.usage_info:
                suggestions.append("Convert gp2 volumes to gp3 for 20% cost savings")
            
            if resource.is_unused:
                suggestions.append("Create snapshot and delete unused volume")
        
        elif 'Load Balancer' in resource.resource_type:
            if resource.is_unused:
                suggestions.append("Delete unused load balancer to save $16-20/month")
        
        # General suggestions
        if resource.is_unused:
            suggestions.append(f"Resource unused - potential savings: {resource.estimated_cost}")
        
        if not resource.tags or len(resource.tags) < 3:
            suggestions.append("Add comprehensive tagging for better cost allocation")
        
        return suggestions

    def calculate_risk_level(self, resource: ResourceInfo) -> str:
        """Calculate risk level based on various factors"""
        risk_score = 0
        
        # Check for public exposure
        if resource.public_ip and resource.public_ip != 'N/A':
            risk_score += 3
        
        # Check for missing encryption
        if 'Encrypted: False' in resource.additional_info:
            risk_score += 2
        
        # Check for unused resources (waste risk)
        if resource.is_unused:
            risk_score += 2
        
        # Check for production resources without backup
        if resource.environment == 'Production' and 'No backup' in resource.backup_status:
            risk_score += 3
        
        # Check compliance status
        if resource.compliance_status:
            failed_checks = sum(1 for v in resource.compliance_status.values() if not v)
            risk_score += failed_checks
        
        # Determine risk level
        if risk_score >= 6:
            return "High"
        elif risk_score >= 3:
            return "Medium"
        else:
            return "Low"

    def get_all_ec2_instances(self) -> Tuple[List[ResourceInfo], List[ResourceInfo]]:
        """Enhanced EC2 instance fetching with comprehensive details"""
        new_resources = []
        unused_resources = []
        
        try:
            response = self.ec2_client.describe_instances()
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    if instance['State']['Name'] == 'terminated':
                        continue
                        
                    launch_time = instance['LaunchTime']
                    is_new = launch_time >= self.cutoff_time
                    
                    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    
                    # Enhanced checks
                    usage_info, is_unused = self.check_ec2_usage(instance['InstanceId'])
                    creator = self.get_resource_creator(
                        instance['InstanceId'],
                        'AWS::EC2::Instance',
                        launch_time
                    ) if is_new else tags.get('CreatedBy', 'Unknown')
                    
                    cost = self.estimate_ec2_cost(instance['InstanceType'])
                    associations = self.get_ec2_associations(instance)
                    
                    # Get security groups
                    security_groups = [sg['GroupName'] for sg in instance.get('SecurityGroups', [])]
                    
                    # Analyze compliance
                    compliance = self.analyze_security_compliance(instance)
                    
                    # Detect environment
                    environment = self.detect_environment_from_tags(tags)
                    
                    # Get backup status
                    backup_status = self.check_backup_status(instance['InstanceId'], 'EC2')
                    
                    # Get owner details from tags
                    owner_email = tags.get('Owner', tags.get('Email', tags.get('owner', '')))
                    department = tags.get('Department', tags.get('Team', tags.get('CostCenter', '')))
                    project = tags.get('Project', tags.get('Application', ''))
                    
                    # Check auto-scaling
                    auto_scaling = self.check_auto_scaling(instance['InstanceId'])
                    
                    # Get performance metrics
                    perf_metrics = self.get_detailed_performance_metrics(instance['InstanceId'])
                    
                    resource = ResourceInfo(
                        resource_type='EC2 Instance',
                        resource_id=instance['InstanceId'],
                        resource_name=tags.get('Name', 'N/A'),
                        created_time=launch_time.astimezone(self.ist).strftime('%Y-%m-%d %H:%M:%S IST'),
                        created_by=creator,
                        state=instance['State']['Name'],
                        tags=tags,
                        usage_info=usage_info,
                        estimated_cost=cost,
                        region=self.aws_region,
                        vpc_id=instance.get('VpcId', 'N/A'),
                        subnet_id=instance.get('SubnetId', 'N/A'),
                        instance_type=instance['InstanceType'],
                        is_unused=is_unused,
                        is_new=is_new,
                        additional_info=associations,
                        security_groups=security_groups,
                        public_ip=instance.get('PublicIpAddress', 'N/A'),
                        private_ip=instance.get('PrivateIpAddress', 'N/A'),
                        compliance_status=compliance,
                        environment=environment,
                        owner_email=owner_email,
                        department=department,
                        project=project,
                        backup_status=backup_status,
                        monitoring_enabled=instance.get('Monitoring', {}).get('State') == 'enabled',
                        auto_scaling_enabled=auto_scaling,
                        encryption_status='Encrypted' if compliance.get('encrypted_volumes') else 'Not Encrypted',
                        performance_metrics=perf_metrics,
                        termination_protection=compliance.get('termination_protection', False)
                    )
                    
                    # Generate optimization suggestions
                    resource.cost_optimization_suggestions = self.get_cost_optimization_suggestions(resource)
                    
                    # Calculate risk level
                    resource.risk_level = self.calculate_risk_level(resource)
                    
                    if is_new:
                        new_resources.append(resource)
                    if is_unused and not is_new:
                        unused_resources.append(resource)
                        
        except Exception as e:
            logger.error(f"Error fetching EC2 instances: {str(e)}")
            
        return new_resources, unused_resources

    def check_backup_status(self, resource_id: str, resource_type: str) -> str:
        """Check if resource has backup configured"""
        try:
            response = self.backup_client.list_recovery_points_by_resource(
                ResourceArn=f"arn:aws:ec2:{self.aws_region}:{self.aws_account_id}:{resource_type.lower()}/{resource_id}"
            )
            
            if response.get('RecoveryPoints'):
                latest_backup = sorted(
                    response['RecoveryPoints'],
                    key=lambda x: x['CreationDate'],
                    reverse=True
                )[0]
                
                days_since_backup = (datetime.now(timezone.utc) - latest_backup['CreationDate']).days
                if days_since_backup == 0:
                    return "Backed up today"
                elif days_since_backup <= 7:
                    return f"Last backup: {days_since_backup} days ago"
                else:
                    return f"Outdated backup: {days_since_backup} days old"
            else:
                return "No backup configured"
        except:
            return "Backup status unknown"

    def check_auto_scaling(self, instance_id: str) -> bool:
        """Check if instance is part of auto-scaling group"""
        try:
            response = self.autoscaling_client.describe_auto_scaling_instances(
                InstanceIds=[instance_id]
            )
            return len(response.get('AutoScalingInstances', [])) > 0
        except:
            return False

    def get_detailed_performance_metrics(self, instance_id: str) -> Dict[str, float]:
        """Get detailed performance metrics for last 7 days"""
        metrics = {}
        
        metric_names = [
            'CPUUtilization',
            'NetworkIn',
            'NetworkOut',
            'DiskReadBytes',
            'DiskWriteBytes',
            'CPUCreditBalance'
        ]
        
        for metric_name in metric_names:
            try:
                response = self.cloudwatch_client.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName=metric_name,
                    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                    StartTime=datetime.now(timezone.utc) - timedelta(days=7),
                    EndTime=datetime.now(timezone.utc),
                    Period=604800,  # 7 days
                    Statistics=['Average', 'Maximum']
                )
                
                if response['Datapoints']:
                    metrics[f"{metric_name}_Avg"] = response['Datapoints'][0].get('Average', 0)
                    metrics[f"{metric_name}_Max"] = response['Datapoints'][0].get('Maximum', 0)
            except:
                continue
        
        return metrics

    def get_all_rds_instances(self) -> Tuple[List[ResourceInfo], List[ResourceInfo]]:
        """Fetch all RDS instances with enhanced details"""
        new_resources = []
        unused_resources = []
        
        try:
            response = self.rds_client.describe_db_instances()
            
            for db in response['DBInstances']:
                create_time = db['InstanceCreateTime']
                is_new = create_time >= self.cutoff_time
                
                # Get tags
                tags_response = self.rds_client.list_tags_for_resource(
                    ResourceName=db['DBInstanceArn']
                )
                tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
                
                # Check usage
                usage_info, is_unused = self.check_rds_usage(db['DBInstanceIdentifier'])
                
                # Detect environment
                environment = self.detect_environment_from_tags(tags)
                
                # Get backup status
                backup_retention = db.get('BackupRetentionPeriod', 0)
                backup_status = f"Retention: {backup_retention} days" if backup_retention > 0 else "No backup"
                
                # Cost estimation
                cost = self.estimate_rds_cost(db['DBInstanceClass'], db.get('Engine', ''))
                
                resource = ResourceInfo(
                    resource_type='RDS Instance',
                    resource_id=db['DBInstanceIdentifier'],
                    resource_name=db['DBInstanceIdentifier'],
                    created_time=create_time.astimezone(self.ist).strftime('%Y-%m-%d %H:%M:%S IST'),
                    created_by=tags.get('CreatedBy', 'Unknown'),
                    state=db['DBInstanceStatus'],
                    tags=tags,
                    usage_info=usage_info,
                    estimated_cost=cost,
                    region=self.aws_region,
                    vpc_id=db.get('DBSubnetGroup', {}).get('VpcId', 'N/A'),
                    is_unused=is_unused,
                    is_new=is_new,
                    additional_info=f"Engine: {db.get('Engine')}, Version: {db.get('EngineVersion')}",
                    environment=environment,
                    backup_status=backup_status,
                    encryption_status='Encrypted' if db.get('StorageEncrypted') else 'Not Encrypted',
                    monitoring_enabled=db.get('PerformanceInsightsEnabled', False),
                    owner_email=tags.get('Owner', ''),
                    department=tags.get('Department', ''),
                    project=tags.get('Project', '')
                )
                
                # Generate suggestions
                resource.cost_optimization_suggestions = self.get_rds_optimization_suggestions(db)
                resource.risk_level = self.calculate_risk_level(resource)
                
                if is_new:
                    new_resources.append(resource)
                if is_unused and not is_new:
                    unused_resources.append(resource)
                    
        except Exception as e:
            logger.error(f"Error fetching RDS instances: {str(e)}")
            
        return new_resources, unused_resources

    def check_rds_usage(self, db_identifier: str) -> tuple[str, bool]:
        """Check RDS instance usage"""
        try:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='DatabaseConnections',
                Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_identifier}],
                StartTime=datetime.now(timezone.utc) - timedelta(days=7),
                EndTime=datetime.now(timezone.utc),
                Period=604800,
                Statistics=['Average', 'Maximum']
            )
            
            if response['Datapoints']:
                avg_conn = response['Datapoints'][0].get('Average', 0)
                max_conn = response['Datapoints'][0].get('Maximum', 0)
                
                usage_info = f"Avg Connections (7d): {avg_conn:.0f}, Max: {max_conn:.0f}"
                is_unused = avg_conn < 1 and max_conn < 5
                
                return usage_info, is_unused
            else:
                return "No connection metrics available", True
                
        except Exception as e:
            logger.error(f"Error checking RDS usage: {str(e)}")
            return "Metrics unavailable", False

    def estimate_rds_cost(self, instance_class: str, engine: str) -> str:
        """Estimate RDS instance cost"""
        # Simplified cost estimation - in production, use AWS Pricing API
        base_costs = {
            'db.t3.micro': 15,
            'db.t3.small': 30,
            'db.t3.medium': 60,
            'db.t3.large': 120,
            'db.m5.large': 200,
            'db.m5.xlarge': 400,
            'db.r5.large': 250,
            'db.r5.xlarge': 500
        }
        
        monthly_cost = base_costs.get(instance_class, 150)
        
        # Add storage and backup costs estimate
        storage_cost = 20  # Approximate
        total_monthly = monthly_cost + storage_cost
        
        return f"${total_monthly:.2f}/month (instance: ${monthly_cost}, storage: ~${storage_cost})"

    def get_rds_optimization_suggestions(self, db_instance: dict) -> List[str]:
        """Generate RDS-specific optimization suggestions"""
        suggestions = []
        
        # Check for old generation instances
        if db_instance['DBInstanceClass'].startswith(('db.t2', 'db.m3', 'db.m4')):
            suggestions.append("Upgrade to newer generation instance class for better performance/cost")
        
        # Check multi-AZ for non-production
        if db_instance.get('MultiAZ') and 'prod' not in db_instance['DBInstanceIdentifier'].lower():
            suggestions.append("Consider disabling Multi-AZ for non-production to save 50% cost")
        
        # Check backup retention
        if db_instance.get('BackupRetentionPeriod', 0) > 7:
            suggestions.append("Review backup retention period - consider using snapshots for long-term backup")
        
        return suggestions

    def get_all_s3_buckets(self) -> Tuple[List[ResourceInfo], List[ResourceInfo]]:
        """Fetch all S3 buckets with enhanced analysis"""
        new_resources = []
        unused_resources = []
        
        try:
            response = self.s3_client.list_buckets()
            
            for bucket in response['Buckets']:
                bucket_name = bucket['Name']
                creation_date = bucket['CreationDate']
                is_new = creation_date >= self.cutoff_time
                
                # Get bucket details
                try:
                    # Get tags
                    tags = {}
                    try:
                        tag_response = self.s3_client.get_bucket_tagging(Bucket=bucket_name)
                        tags = {tag['Key']: tag['Value'] for tag in tag_response.get('TagSet', [])}
                    except:
                        pass
                    
                    # Get bucket size and object count
                    size_info, is_unused = self.get_s3_bucket_metrics(bucket_name)
                    
                    # Check encryption
                    encryption = "Enabled"
                    try:
                        self.s3_client.get_bucket_encryption(Bucket=bucket_name)
                    except:
                        encryption = "Not Enabled"
                    
                    # Check versioning
                    versioning = "Disabled"
                    try:
                        vers_response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
                        versioning = vers_response.get('Status', 'Disabled')
                    except:
                        pass
                    
                    # Cost estimation
                    cost = self.estimate_s3_cost(bucket_name)
                    
                    resource = ResourceInfo(
                        resource_type='S3 Bucket',
                        resource_id=bucket_name,
                        resource_name=bucket_name,
                        created_time=creation_date.astimezone(self.ist).strftime('%Y-%m-%d %H:%M:%S IST'),
                        created_by=tags.get('CreatedBy', 'Unknown'),
                        state='active',
                        tags=tags,
                        usage_info=size_info,
                        estimated_cost=cost,
                        region=self.aws_region,
                        is_unused=is_unused,
                        is_new=is_new,
                        additional_info=f"Versioning: {versioning}, Encryption: {encryption}",
                        environment=self.detect_environment_from_tags(tags),
                        encryption_status=encryption,
                        owner_email=tags.get('Owner', ''),
                        department=tags.get('Department', ''),
                        project=tags.get('Project', '')
                    )
                    
                    # Generate suggestions
                    resource.cost_optimization_suggestions = self.get_s3_optimization_suggestions(
                        bucket_name, versioning, encryption, is_unused
                    )
                    resource.risk_level = self.calculate_risk_level(resource)
                    
                    if is_new:
                        new_resources.append(resource)
                    if is_unused and not is_new:
                        unused_resources.append(resource)
                        
                except Exception as e:
                    logger.error(f"Error processing bucket {bucket_name}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error fetching S3 buckets: {str(e)}")
            
        return new_resources, unused_resources

    def get_s3_bucket_metrics(self, bucket_name: str) -> tuple[str, bool]:
        """Get S3 bucket size and usage metrics"""
        try:
            # Get bucket size from CloudWatch
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'}
                ],
                StartTime=datetime.now(timezone.utc) - timedelta(days=2),
                EndTime=datetime.now(timezone.utc),
                Period=86400,
                Statistics=['Average']
            )
            
            size_bytes = 0
            if response['Datapoints']:
                size_bytes = response['Datapoints'][0]['Average']
            
            # Get object count
            object_count = 0
            try:
                response = self.cloudwatch_client.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName='NumberOfObjects',
                    Dimensions=[
                        {'Name': 'BucketName', 'Value': bucket_name},
                        {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                    ],
                    StartTime=datetime.now(timezone.utc) - timedelta(days=2),
                    EndTime=datetime.now(timezone.utc),
                    Period=86400,
                    Statistics=['Average']
                )
                
                if response['Datapoints']:
                    object_count = int(response['Datapoints'][0]['Average'])
            except:
                pass
            
            # Format size
            size_gb = size_bytes / (1024**3)
            size_info = f"Size: {size_gb:.2f} GB, Objects: {object_count:,}"
            
            # Consider unused if empty or very small
            is_unused = size_gb < 0.001 and object_count < 10
            
            return size_info, is_unused
            
        except Exception as e:
            logger.error(f"Error getting S3 metrics for {bucket_name}: {str(e)}")
            return "Metrics unavailable", False

    def estimate_s3_cost(self, bucket_name: str) -> str:
        """Estimate S3 bucket cost"""
        try:
            # Get size from metrics
            size_info, _ = self.get_s3_bucket_metrics(bucket_name)
            size_gb = float(re.search(r'Size: ([\d.]+) GB', size_info).group(1)) if 'Size:' in size_info else 0
            
            # S3 Standard pricing (simplified)
            storage_cost = size_gb * 0.023  # $0.023 per GB
            request_cost = 0.5  # Estimated request costs
            
            total_monthly = storage_cost + request_cost
            
            return f"${total_monthly:.2f}/month (storage: ${storage_cost:.2f}, requests: ~${request_cost:.2f})"
            
        except Exception as e:
            logger.error(f"Error estimating S3 cost for {bucket_name}: {str(e)}")
            return "Cost estimation unavailable"

    def get_s3_optimization_suggestions(self, bucket_name: str, versioning: str, 
                                       encryption: str, is_unused: bool) -> List[str]:
        """Generate S3-specific optimization suggestions"""
        suggestions = []
        
        if is_unused:
            suggestions.append("Delete empty bucket or archive old data to Glacier")
        
        if versioning == 'Enabled':
            suggestions.append("Configure lifecycle policies to delete old versions")
        
        if encryption == 'Not Enabled':
            suggestions.append("Enable default encryption for security compliance")
        
        # Check for lifecycle policies
        try:
            self.s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        except:
            suggestions.append("Add lifecycle policies to move old data to cheaper storage classes")
        
        return suggestions

    def get_all_lambda_functions(self) -> Tuple[List[ResourceInfo], List[ResourceInfo]]:
        """Fetch all Lambda functions with usage analysis"""
        new_resources = []
        unused_resources = []
        
        try:
            response = self.lambda_client.list_functions()
            
            for function in response['Functions']:
                # Get function details
                func_name = function['FunctionName']
                last_modified = datetime.fromisoformat(function['LastModified'].replace('Z', '+00:00'))
                is_new = last_modified >= self.cutoff_time
                
                # Get tags
                tags_response = self.lambda_client.list_tags(Resource=function['FunctionArn'])
                tags = tags_response.get('Tags', {})
                
                # Check usage
                usage_info, is_unused = self.check_lambda_usage(func_name)
                
                # Detect environment
                environment = self.detect_environment_from_tags(tags)
                
                # Cost estimation
                memory = function.get('MemorySize', 128)
                timeout = function.get('Timeout', 3)
                cost = self.estimate_lambda_cost(memory, timeout)
                
                resource = ResourceInfo(
                    resource_type='Lambda Function',
                    resource_id=func_name,
                    resource_name=func_name,
                    created_time=last_modified.astimezone(self.ist).strftime('%Y-%m-%d %H:%M:%S IST'),
                    created_by=tags.get('CreatedBy', 'Unknown'),
                    state=function.get('State', 'Active'),
                    tags=tags,
                    usage_info=usage_info,
                    estimated_cost=cost,
                    region=self.aws_region,
                    is_unused=is_unused,
                    is_new=is_new,
                    additional_info=f"Runtime: {function.get('Runtime', 'N/A')}, Memory: {memory}MB, Timeout: {timeout}s",
                    environment=environment,
                    owner_email=tags.get('Owner', ''),
                    department=tags.get('Department', ''),
                    project=tags.get('Project', '')
                )
                
                # Generate suggestions
                if is_unused:
                    resource.cost_optimization_suggestions.append("Delete unused Lambda function")
                if memory > 1024:
                    resource.cost_optimization_suggestions.append("Review memory allocation - may be over-provisioned")
                
                resource.risk_level = self.calculate_risk_level(resource)
                
                if is_new:
                    new_resources.append(resource)
                if is_unused and not is_new:
                    unused_resources.append(resource)
                    
        except Exception as e:
            logger.error(f"Error fetching Lambda functions: {str(e)}")
            
        return new_resources, unused_resources

    def check_lambda_usage(self, function_name: str) -> tuple[str, bool]:
        """Check Lambda function usage"""
        try:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Invocations',
                Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                StartTime=datetime.now(timezone.utc) - timedelta(days=30),
                EndTime=datetime.now(timezone.utc),
                Period=2592000,  # 30 days
                Statistics=['Sum']
            )
            
            invocations = 0
            if response['Datapoints']:
                invocations = int(response['Datapoints'][0]['Sum'])
            
            usage_info = f"Invocations (30d): {invocations:,}"
            is_unused = invocations == 0
            
            return usage_info, is_unused
            
        except Exception as e:
            logger.error(f"Error checking Lambda usage: {str(e)}")
            return "Metrics unavailable", False

    def estimate_lambda_cost(self, memory_mb: int, timeout_seconds: int) -> str:
        """Estimate Lambda function cost"""
        # Simplified estimation
        price_per_gb_second = 0.0000166667
        price_per_request = 0.0000002
        
        # Assume average execution time is half of timeout
        avg_execution_time = timeout_seconds / 2
        gb_seconds = (memory_mb / 1024) * avg_execution_time
        
        # Assume 1000 invocations per month for active functions
        monthly_invocations = 1000
        compute_cost = gb_seconds * monthly_invocations * price_per_gb_second
        request_cost = monthly_invocations * price_per_request
        
        total = compute_cost + request_cost
        
        return f"${total:.4f}/month (est. 1K invocations)"

    def get_all_load_balancers(self) -> Tuple[List[ResourceInfo], List[ResourceInfo]]:
        """Enhanced Load Balancer fetching with detailed analysis"""
        new_resources = []
        unused_resources = []
        
        # Check Classic Load Balancers
        try:
            response = self.elb_client.describe_load_balancers()
            for lb in response['LoadBalancerDescriptions']:
                created_time = lb['CreatedTime']
                is_new = created_time >= self.cutoff_time
                
                # Get detailed usage info
                usage_info = f"Instances: {len(lb.get('Instances', []))}, Zones: {', '.join(lb.get('AvailabilityZones', []))}"
                is_unused = len(lb.get('Instances', [])) == 0
                
                creator = self.get_resource_creator(
                    lb['LoadBalancerName'],
                    'AWS::ElasticLoadBalancing::LoadBalancer',
                    created_time
                ) if is_new else "Unknown"
                
                # Check health check configuration
                health_check = lb.get('HealthCheck', {})
                health_info = f"Target: {health_check.get('Target', 'N/A')}"
                
                resource = ResourceInfo(
                    resource_type='Classic Load Balancer',
                    resource_id=lb['LoadBalancerName'],
                    resource_name=lb['LoadBalancerName'],
                    created_time=created_time.astimezone(self.ist).strftime('%Y-%m-%d %H:%M:%S IST'),
                    created_by=creator,
                    state='active',
                    tags={},
                    usage_info=usage_info,
                    estimated_cost=self.estimate_lb_cost('classic'),
                    region=self.aws_region,
                    vpc_id=lb.get('VPCId', 'N/A'),
                    is_unused=is_unused,
                    is_new=is_new,
                    additional_info=health_info,
                    security_groups=lb.get('SecurityGroups', [])
                )
                
                if is_unused:
                    resource.cost_optimization_suggestions.append("Migrate to ALB/NLB or delete if unused")
                
                resource.risk_level = self.calculate_risk_level(resource)
                
                if is_new:
                    new_resources.append(resource)
                if is_unused and not is_new:
                    unused_resources.append(resource)
                    
        except Exception as e:
            logger.error(f"Error fetching Classic Load Balancers: {str(e)}")
        
        # Check Application/Network Load Balancers
        try:
            response = self.elbv2_client.describe_load_balancers()
            for lb in response['LoadBalancers']:
                created_time = lb['CreatedTime']
                is_new = created_time >= self.cutoff_time
                
                # Get tags
                tags_response = self.elbv2_client.describe_tags(
                    ResourceArns=[lb['LoadBalancerArn']]
                )
                tags = {}
                if tags_response['TagDescriptions']:
                    tags = {tag['Key']: tag['Value'] 
                           for tag in tags_response['TagDescriptions'][0].get('Tags', [])}
                
                creator = self.get_resource_creator(
                    lb['LoadBalancerName'],
                    'AWS::ElasticLoadBalancingV2::LoadBalancer',
                    created_time
                ) if is_new else tags.get('CreatedBy', 'Unknown')
                
                # Enhanced usage check
                usage_info, is_unused = self.check_lb_usage(lb['LoadBalancerArn'])
                
                # Get listeners
                listeners_response = self.elbv2_client.describe_listeners(
                    LoadBalancerArn=lb['LoadBalancerArn']
                )
                listener_count = len(listeners_response.get('Listeners', []))
                
                # Detect environment
                environment = self.detect_environment_from_tags(tags)
                
                resource = ResourceInfo(
                    resource_type=f"{lb['Type'].upper()} Load Balancer",
                    resource_id=lb['LoadBalancerArn'].split('/')[-1],
                    resource_name=lb['LoadBalancerName'],
                    created_time=created_time.astimezone(self.ist).strftime('%Y-%m-%d %H:%M:%S IST'),
                    created_by=creator,
                    state=lb['State']['Code'],
                    tags=tags,
                    usage_info=f"{usage_info}, Listeners: {listener_count}",
                    estimated_cost=self.estimate_lb_cost(lb['Type']),
                    region=self.aws_region,
                    vpc_id=lb.get('VpcId', 'N/A'),
                    is_unused=is_unused,
                    is_new=is_new,
                    additional_info=f"Scheme: {lb.get('Scheme', 'N/A')}, DNS: {lb.get('DNSName', 'N/A')}",
                    environment=environment,
                    owner_email=tags.get('Owner', ''),
                    department=tags.get('Department', ''),
                    project=tags.get('Project', ''),
                    security_groups=lb.get('SecurityGroups', [])
                )
                
                # Generate optimization suggestions
                if is_unused:
                    resource.cost_optimization_suggestions.append(f"Delete unused {lb['Type']} load balancer")
                if lb['Type'] == 'application' and listener_count > 5:
                    resource.cost_optimization_suggestions.append("Consider consolidating listeners to reduce complexity")
                
                resource.risk_level = self.calculate_risk_level(resource)
                
                if is_new:
                    new_resources.append(resource)
                if is_unused and not is_new:
                    unused_resources.append(resource)
                    
        except Exception as e:
            logger.error(f"Error fetching ALB/NLB: {str(e)}")
            
        return new_resources, unused_resources

    def get_all_ebs_volumes(self) -> Tuple[List[ResourceInfo], List[ResourceInfo]]:
        """Enhanced EBS volume fetching with detailed analysis"""
        new_resources = []
        unused_resources = []
        
        try:
            response = self.ec2_client.describe_volumes()
            
            for volume in response['Volumes']:
                create_time = volume['CreateTime']
                is_new = create_time >= self.cutoff_time
                
                tags = {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])}
                
                # Enhanced attachment check
                is_attached = len(volume.get('Attachments', [])) > 0
                attachment_info = "Not attached"
                attached_instance = None
                
                if is_attached:
                    attachment = volume['Attachments'][0]
                    attached_instance = attachment['InstanceId']
                    attachment_info = f"Attached to: {attached_instance}, Device: {attachment['Device']}"
                
                is_unused = not is_attached and volume['State'] == 'available'
                
                # Check for snapshots
                snapshot_info = self.check_volume_snapshots(volume['VolumeId'])
                
                # Detect environment
                environment = self.detect_environment_from_tags(tags)
                
                # Calculate IOPS cost if applicable
                iops_cost = ""
                if volume['VolumeType'] in ['io1', 'io2']:
                    iops = volume.get('Iops', 0)
                    iops_monthly_cost = iops * 0.065  # $0.065 per IOPS/month
                    iops_cost = f", IOPS: ${iops_monthly_cost:.2f}/month"
                
                resource = ResourceInfo(
                    resource_type='EBS Volume',
                    resource_id=volume['VolumeId'],
                    resource_name=tags.get('Name', 'N/A'),
                    created_time=create_time.astimezone(self.ist).strftime('%Y-%m-%d %H:%M:%S IST'),
                    created_by=self.get_resource_creator(volume['VolumeId'], 'AWS::EC2::Volume', create_time) if is_new else tags.get('CreatedBy', 'Unknown'),
                    state=volume['State'],
                    tags=tags,
                    usage_info=f"Size: {volume['Size']} GB, Type: {volume['VolumeType']}, {attachment_info}",
                    estimated_cost=f"{self.estimate_ebs_cost(volume['Size'], volume['VolumeType'])}{iops_cost}",
                    region=self.aws_region,
                    is_unused=is_unused,
                    is_new=is_new,
                    additional_info=f"IOPS: {volume.get('Iops', 'N/A')}, Encrypted: {volume.get('Encrypted', False)}, {snapshot_info}",
                    environment=environment,
                    encryption_status='Encrypted' if volume.get('Encrypted') else 'Not Encrypted',
                    associated_resources=[attached_instance] if attached_instance else [],
                    owner_email=tags.get('Owner', ''),
                    department=tags.get('Department', ''),
                    project=tags.get('Project', ''),
                    backup_status=snapshot_info
                )
                
                # Generate optimization suggestions
                resource.cost_optimization_suggestions = self.get_ebs_optimization_suggestions(volume, is_attached)
                resource.risk_level = self.calculate_risk_level(resource)
                
                if is_new:
                    new_resources.append(resource)
                if is_unused and not is_new:
                    unused_resources.append(resource)
                    
        except Exception as e:
            logger.error(f"Error fetching EBS volumes: {str(e)}")
            
        return new_resources, unused_resources

    def check_volume_snapshots(self, volume_id: str) -> str:
        """Check if volume has recent snapshots"""
        try:
            response = self.ec2_client.describe_snapshots(
                Filters=[
                    {'Name': 'volume-id', 'Values': [volume_id]},
                    {'Name': 'status', 'Values': ['completed']}
                ]
            )
            
            if response['Snapshots']:
                latest_snapshot = sorted(response['Snapshots'], 
                                       key=lambda x: x['StartTime'], 
                                       reverse=True)[0]
                days_since = (datetime.now(timezone.utc) - latest_snapshot['StartTime']).days
                return f"Last snapshot: {days_since} days ago"
            else:
                return "No snapshots"
        except:
            return "Snapshot status unknown"

    def get_ebs_optimization_suggestions(self, volume: dict, is_attached: bool) -> List[str]:
        """Generate EBS-specific optimization suggestions"""
        suggestions = []
        
        # Volume type optimization
        if volume['VolumeType'] == 'gp2':
            suggestions.append("Migrate from gp2 to gp3 for 20% cost savings and better performance")
        
        # Unused volume
        if not is_attached:
            suggestions.append("Create snapshot and delete unattached volume to save costs")
        
        # Over-provisioned IOPS
        if volume['VolumeType'] in ['io1', 'io2'] and volume.get('Iops', 0) > 10000:
            suggestions.append("Review IOPS requirements - may be over-provisioned")
        
        # Large volumes
        if volume['Size'] > 500:
            suggestions.append("Review large volume usage - consider archiving old data")
        
        # Encryption
        if not volume.get('Encrypted'):
            suggestions.append("Enable encryption for compliance and security")
        
        return suggestions

    def get_all_elastic_ips(self) -> Tuple[List[ResourceInfo], List[ResourceInfo]]:
        """Enhanced Elastic IP fetching with association details"""
        new_resources = []
        unused_resources = []
        
        try:
            response = self.ec2_client.describe_addresses()
            
            for eip in response['Addresses']:
                if 'AllocationId' in eip:
                    allocation_time = self.get_resource_allocation_time(eip['AllocationId'])
                    is_new = allocation_time and allocation_time >= self.cutoff_time
                    
                    # Enhanced association check
                    is_associated = 'InstanceId' in eip or 'NetworkInterfaceId' in eip
                    association_info = "Not associated"
                    associated_resource = None
                    
                    if 'InstanceId' in eip:
                        associated_resource = eip['InstanceId']
                        association_info = f"Associated with EC2: {associated_resource}"
                    elif 'NetworkInterfaceId' in eip:
                        associated_resource = eip['NetworkInterfaceId']
                        association_info = f"Associated with ENI: {associated_resource}"
                    
                    # Get tags
                    tags = {tag['Key']: tag['Value'] for tag in eip.get('Tags', [])}
                    
                    # Detect environment
                    environment = self.detect_environment_from_tags(tags)
                    
                    # Calculate monthly cost
                    monthly_cost = 0 if is_associated else 3.60  # $0.005 per hour when not associated
                    
                    resource = ResourceInfo(
                        resource_type='Elastic IP',
                        resource_id=eip['AllocationId'],
                        resource_name=eip.get('PublicIp', 'N/A'),
                        created_time=allocation_time.astimezone(self.ist).strftime('%Y-%m-%d %H:%M:%S IST') if allocation_time else 'Unknown',
                        created_by=tags.get('CreatedBy', 'Unknown'),
                        state='allocated',
                        tags=tags,
                        usage_info=association_info,
                        estimated_cost=f'${monthly_cost:.2f}/month',
                        region=self.aws_region,
                        is_unused=not is_associated,
                        is_new=is_new,
                        additional_info=f"Domain: {eip.get('Domain', 'vpc')}, IP: {eip.get('PublicIp', 'N/A')}",
                        public_ip=eip.get('PublicIp', 'N/A'),
                        associated_resources=[associated_resource] if associated_resource else [],
                        environment=environment,
                        owner_email=tags.get('Owner', ''),
                        department=tags.get('Department', ''),
                        project=tags.get('Project', '')
                    )
                    
                    # Generate suggestions
                    if not is_associated:
                        resource.cost_optimization_suggestions.append("Release unassociated Elastic IP to save $3.60/month")
                    
                    resource.risk_level = self.calculate_risk_level(resource)
                    
                    if is_new:
                        new_resources.append(resource)
                    if not is_associated and not is_new:
                        unused_resources.append(resource)
                        
        except Exception as e:
            logger.error(f"Error fetching Elastic IPs: {str(e)}")
            
        return new_resources, unused_resources

    def send_to_google_sheets(self, new_resources: List[ResourceInfo], unused_resources: List[ResourceInfo]):
        """Enhanced Google Sheets reporting with comprehensive data"""
        try:
            # creds = Credentials.from_service_account_file(
            #     self.google_creds_file,
            #     scopes=[
            #         "https://www.googleapis.com/auth/spreadsheets",
            #         "https://www.googleapis.com/auth/drive"
            #     ]
            # )
            
            # client = gspread.authorize(creds)
            client = self.authenticate_gspread()
            
            sheet = client.open_by_key(self.spreadsheet_id)
            
            today = datetime.now(self.ist).strftime('%Y-%m-%d')
            
            try:
                worksheet = sheet.worksheet(today)
                worksheet.clear()
            except gspread.exceptions.WorksheetNotFound:
                worksheet = sheet.add_worksheet(title=today, rows=2000, cols=30)
            
            # Enhanced headers with new fields
            headers = [
                'Category', 'Timestamp', 'Resource Type', 'Resource ID', 'Resource Name',
                'Created Time', 'Created By', 'State', 'Environment', 'Risk Level',
                'VPC ID', 'Subnet ID', 'Instance Type', 'Public IP', 'Private IP',
                'Security Groups', 'Tags', 'Usage Info', 'Is Unused',
                'Estimated Cost', 'Backup Status', 'Encryption Status', 'Monitoring',
                'Auto-Scaling', 'Owner Email', 'Department', 'Project',
                'Optimization Suggestions', 'Compliance Status', 'Performance Metrics',
                'Additional Info', 'Region'
            ]
            
            data_rows = [headers]
            timestamp = datetime.now(self.ist).strftime('%Y-%m-%d %H:%M:%S IST')
            
            # Helper function to format resource row
            def format_resource_row(category: str, resource: ResourceInfo) -> List:
                return [
                    category,
                    timestamp,
                    resource.resource_type,
                    resource.resource_id,
                    resource.resource_name,
                    resource.created_time,
                    resource.created_by,
                    resource.state,
                    resource.environment,
                    resource.risk_level,
                    resource.vpc_id,
                    resource.subnet_id,
                    resource.instance_type,
                    resource.public_ip,
                    resource.private_ip,
                    ', '.join(resource.security_groups) if resource.security_groups else '',
                    json.dumps(resource.tags) if resource.tags else '',
                    resource.usage_info,
                    'Yes' if resource.is_unused else 'No',
                    resource.estimated_cost,
                    resource.backup_status,
                    resource.encryption_status,
                    'Yes' if resource.monitoring_enabled else 'No',
                    'Yes' if resource.auto_scaling_enabled else 'No',
                    resource.owner_email,
                    resource.department,
                    resource.project,
                    ' | '.join(resource.cost_optimization_suggestions) if resource.cost_optimization_suggestions else '',
                    json.dumps(resource.compliance_status) if resource.compliance_status else '',
                    json.dumps(resource.performance_metrics) if resource.performance_metrics else '',
                    resource.additional_info,
                    resource.region
                ]
            
            # Add NEW resources
            if new_resources:
                data_rows.append(['=== NEW RESOURCES (Last 24 Hours) ==='])
                for resource in new_resources:
                    data_rows.append(format_resource_row('NEW', resource))
            
            # Add UNUSED resources
            if unused_resources:
                data_rows.append([])
                data_rows.append(['=== UNUSED RESOURCES (All Time) ==='])
                for resource in unused_resources:
                    data_rows.append(format_resource_row('UNUSED', resource))
            
            # Enhanced summary section
            data_rows.append([])
            data_rows.append(['=== EXECUTIVE SUMMARY ==='])
            data_rows.append(['Metric', 'Value'])
            data_rows.append(['Total NEW Resources (24h)', len(new_resources)])
            data_rows.append(['Total UNUSED Resources', len(unused_resources)])
            
            # Risk analysis
            high_risk = sum(1 for r in new_resources + unused_resources if r.risk_level == 'High')
            medium_risk = sum(1 for r in new_resources + unused_resources if r.risk_level == 'Medium')
            data_rows.append(['High Risk Resources', high_risk])
            data_rows.append(['Medium Risk Resources', medium_risk])
            
            # Environment breakdown
            environments = defaultdict(int)
            for r in new_resources + unused_resources:
                environments[r.environment] += 1
            
            data_rows.append([])
            data_rows.append(['=== ENVIRONMENT BREAKDOWN ==='])
            for env, count in environments.items():
                data_rows.append([env, count])
            
            # Cost analysis
            total_monthly_savings = 0
            total_monthly_cost = 0
            
            for r in unused_resources:
                try:
                    if '$' in r.estimated_cost and 'month' in r.estimated_cost:
                        cost_str = r.estimated_cost.split('$')[1].split('/month')[0].split(' ')[0]
                        total_monthly_savings += float(cost_str.replace(',', ''))
                except:
                    pass
            
            for r in new_resources + unused_resources:
                try:
                    if '$' in r.estimated_cost and 'month' in r.estimated_cost:
                        cost_str = r.estimated_cost.split('$')[1].split('/month')[0].split(' ')[0]
                        total_monthly_cost += float(cost_str.replace(',', ''))
                except:
                    pass
            
            data_rows.append([])
            data_rows.append(['=== COST ANALYSIS ==='])
            data_rows.append(['Total Monthly Cost (All Resources)', f'${total_monthly_cost:.2f}'])
            data_rows.append(['Potential Monthly Savings (Unused)', f'${total_monthly_savings:.2f}'])
            data_rows.append(['Annual Savings Opportunity', f'${total_monthly_savings * 12:.2f}'])
            
            # Top optimization opportunities
            data_rows.append([])
            data_rows.append(['=== TOP OPTIMIZATION OPPORTUNITIES ==='])
            
            # Sort by potential savings
            savings_opportunities = []
            for r in unused_resources[:10]:  # Top 10
                try:
                    cost_value = 0
                    if '$' in r.estimated_cost:
                        cost_str = r.estimated_cost.split('$')[1].split('/')[0].split(' ')[0]
                        cost_value = float(cost_str.replace(',', ''))
                    
                    savings_opportunities.append((r, cost_value))
                except:
                    pass
            
            savings_opportunities.sort(key=lambda x: x[1], reverse=True)
            
            for r, savings in savings_opportunities[:10]:
                data_rows.append([
                    f"{r.resource_type} - {r.resource_id}",
                    f"${savings:.2f}/month",
                    ' | '.join(r.cost_optimization_suggestions[:2]) if r.cost_optimization_suggestions else ''
                ])
            
            # Update worksheet
            worksheet.update('A1', data_rows)
            
            # Format headers
            worksheet.format('A1:AF1', {
                "backgroundColor": {"red": 0.2, "green": 0.5, "blue": 0.8},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                "horizontalAlignment": "CENTER"
            })
            
            # Format section headers
            for i, row in enumerate(data_rows):
                if row and str(row[0]).startswith('==='):
                    worksheet.format(f'A{i+1}:AF{i+1}', {
                        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                        "textFormat": {"bold": True}
                    })
            
            logger.info(f"Successfully updated Google Sheet for {today}")
            
        except Exception as e:
            logger.error(f"Error updating Google Sheets: {str(e)}")

    def send_slack_notification(self, new_resources: List[ResourceInfo], unused_resources: List[ResourceInfo]):
        """Enhanced Slack notification showing ALL resources"""
        try:
            # Calculate totals and statistics
            new_unused_count = sum(1 for r in new_resources if r.is_unused)
            total_monthly_savings = 0
            
            for r in unused_resources:
                try:
                    if '$' in r.estimated_cost and 'month' in r.estimated_cost:
                        cost_str = r.estimated_cost.split('$')[1].split('/month')[0].split(' ')[0]
                        total_monthly_savings += float(cost_str.replace(',', ''))
                except:
                    pass
            
            # Risk assessment
            high_risk_resources = [r for r in (new_resources + unused_resources) if r.risk_level == 'High']
            medium_risk_resources = [r for r in (new_resources + unused_resources) if r.risk_level == 'Medium']
            
            # First message: Header and comprehensive summary
            summary_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚀 AWS Resource Monitor - Comprehensive Daily Report"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Account:* {self.aws_account_id}\n*Region:* {self.aws_region}\n*Report Time:* {datetime.now(self.ist).strftime('%Y-%m-%d %H:%M:%S IST')}"
                    }
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*📊 EXECUTIVE SUMMARY*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*🆕 New Resources (24h):* {len(new_resources)}"},
                        {"type": "mrkdwn", "text": f"*🔴 Unused Resources:* {len(unused_resources)}"},
                        {"type": "mrkdwn", "text": f"*⚠️ New & Unused:* {new_unused_count}"},
                        {"type": "mrkdwn", "text": f"*💰 Monthly Savings:* ${total_monthly_savings:.2f}"},
                        {"type": "mrkdwn", "text": f"*📈 Annual Savings:* ${total_monthly_savings * 12:.2f}"},
                        {"type": "mrkdwn", "text": f"*🔥 High Risk:* {len(high_risk_resources)} resources"},
                        {"type": "mrkdwn", "text": f"*⚡ Medium Risk:* {len(medium_risk_resources)} resources"},
                        {"type": "mrkdwn", "text": f"*📝 Total Monitored:* {len(new_resources) + len(unused_resources)}"}
                    ]
                },
                {"type": "divider"}
            ]
            
            # Send summary message
            summary_message = {
                "text": f"AWS Resource Monitor - {len(new_resources)} new, {len(unused_resources)} unused resources",
                "blocks": summary_blocks
            }
            
            response = requests.post(self.slack_webhook_url, json=summary_message)
            if response.status_code != 200:
                logger.error(f"Failed to send summary: {response.status_code}")
            
            # Helper function to create resource blocks
            def create_resource_block(resource: ResourceInfo, index: int) -> List[dict]:
                risk_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(resource.risk_level, "⚪")
                status_emoji = "🔴" if resource.is_unused else "🟢"
                env_emoji = {"Production": "🏭", "Staging": "🎭", "Development": "💻", 
                            "Testing": "🧪", "Demo": "🎯"}.get(resource.environment, "📦")
                
                blocks = []
                
                # Resource header
                resource_text = f"{status_emoji} *#{index}. {resource.resource_type}* {risk_emoji} _{resource.risk_level} Risk_\n"
                resource_text += f"└─ {env_emoji} *Environment:* {resource.environment}\n"
                resource_text += f"├─ *ID:* `{resource.resource_id}`\n"
                resource_text += f"├─ *Name:* {resource.resource_name}\n"
                resource_text += f"├─ *Created:* {resource.created_time}\n"
                resource_text += f"├─ *Creator:* {resource.created_by}\n"
                resource_text += f"├─ *State:* {resource.state}\n"
                resource_text += f"├─ *Cost:* {resource.estimated_cost}\n"
                
                # Add detailed info based on resource type
                if resource.resource_type == 'EC2 Instance':
                    resource_text += f"├─ *Type:* {resource.instance_type}\n"
                    if resource.public_ip and resource.public_ip != 'N/A':
                        resource_text += f"├─ *Public IP:* {resource.public_ip}\n"
                    if resource.private_ip:
                        resource_text += f"├─ *Private IP:* {resource.private_ip}\n"
                    resource_text += f"├─ *VPC:* {resource.vpc_id} | *Subnet:* {resource.subnet_id}\n"
                    resource_text += f"├─ *Backup:* {resource.backup_status}\n"
                    resource_text += f"├─ *Encryption:* {resource.encryption_status}\n"
                    if resource.security_groups:
                        resource_text += f"├─ *Security Groups:* {', '.join(resource.security_groups[:3])}\n"
                
                resource_text += f"├─ *Usage:* {resource.usage_info}\n"
                
                # Add owner info if available
                if resource.owner_email:
                    resource_text += f"├─ *Owner:* {resource.owner_email}\n"
                if resource.department:
                    resource_text += f"├─ *Department:* {resource.department}\n"
                if resource.project:
                    resource_text += f"├─ *Project:* {resource.project}\n"
                
                # Add optimization suggestions
                if resource.cost_optimization_suggestions:
                    resource_text += f"└─ *💡 Recommendations:*\n"
                    for suggestion in resource.cost_optimization_suggestions[:3]:
                        resource_text += f"   • {suggestion}\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": resource_text[:3000]  # Slack limit per block
                    }
                })
                
                return blocks
            
            # Send NEW resources in batches
            if new_resources:
                # Group by resource type for better organization
                resources_by_type = defaultdict(list)
                for r in new_resources:
                    resources_by_type[r.resource_type].append(r)
                
                message_blocks = [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🆕 NEW RESOURCES (Last 24 Hours)"
                        }
                    },
                    {"type": "divider"}
                ]
                
                index = 1
                for resource_type, resources in resources_by_type.items():
                    message_blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{resource_type}s ({len(resources)} total)*"
                        }
                    })
                    
                    for resource in resources:
                        resource_blocks = create_resource_block(resource, index)
                        message_blocks.extend(resource_blocks)
                        index += 1
                        
                        # Send message when approaching Slack limits
                        if len(message_blocks) > 40:  # Slack allows 50 blocks max
                            message = {
                                "text": f"New Resources Report - Part {index // 20}",
                                "blocks": message_blocks
                            }
                            response = requests.post(self.slack_webhook_url, json=message)
                            if response.status_code != 200:
                                logger.error(f"Failed to send new resources batch: {response.status_code}")
                            
                            # Start new message
                            message_blocks = [
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": f"*...continued (NEW Resources)*"
                                    }
                                },
                                {"type": "divider"}
                            ]
                
                # Send remaining blocks
                if len(message_blocks) > 2:
                    message = {
                        "text": "New Resources Report - Final",
                        "blocks": message_blocks
                    }
                    response = requests.post(self.slack_webhook_url, json=message)
                    if response.status_code != 200:
                        logger.error(f"Failed to send final new resources: {response.status_code}")
            
            # Send UNUSED resources in batches
            if unused_resources:
                # Sort by cost for priority
                unused_sorted = sorted(unused_resources, 
                                     key=lambda x: float(re.search(r'([\d.]+)', x.estimated_cost).group(1)) if re.search(r'([\d.]+)', x.estimated_cost) else 0,
                                     reverse=True)
                
                resources_by_type = defaultdict(list)
                for r in unused_sorted:
                    resources_by_type[r.resource_type].append(r)
                
                message_blocks = [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🔴 UNUSED RESOURCES (All Time)"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*⚠️ Action Required:* {len(unused_resources)} unused resources detected\n*💰 Monthly Savings Opportunity:* ${total_monthly_savings:.2f}"
                        }
                    },
                    {"type": "divider"}
                ]
                
                index = 1
                for resource_type, resources in resources_by_type.items():
                    message_blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{resource_type}s ({len(resources)} unused)*"
                        }
                    })
                    
                    for resource in resources:
                        resource_blocks = create_resource_block(resource, index)
                        message_blocks.extend(resource_blocks)
                        index += 1
                        
                        # Send message when approaching limits
                        if len(message_blocks) > 40:
                            message = {
                                "text": f"Unused Resources Report - Part {index // 20}",
                                "blocks": message_blocks
                            }
                            response = requests.post(self.slack_webhook_url, json=message)
                            if response.status_code != 200:
                                logger.error(f"Failed to send unused resources batch: {response.status_code}")
                            
                            # Start new message
                            message_blocks = [
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": f"*...continued (UNUSED Resources)*"
                                    }
                                },
                                {"type": "divider"}
                            ]
                
                # Send remaining blocks
                if len(message_blocks) > 2:
                    message = {
                        "text": "Unused Resources Report - Final",
                        "blocks": message_blocks
                    }
                    response = requests.post(self.slack_webhook_url, json=message)
                    if response.status_code != 200:
                        logger.error(f"Failed to send final unused resources: {response.status_code}")
            
            # Send final action items and links
            action_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📋 ACTION ITEMS & NEXT STEPS"
                    }
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🎯 Top Priority Actions:*"
                    }
                }
            ]
            
            # Add high-risk items
            if high_risk_resources:
                action_text = "*🔴 High Risk Resources Requiring Immediate Attention:*\n"
                for r in high_risk_resources[:5]:
                    action_text += f"• {r.resource_type} `{r.resource_id}` - {r.risk_level} risk\n"
                
                action_blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": action_text}
                })
            
            # Add cost optimization priorities
            if unused_resources:
                opt_text = "*💰 Top Cost Optimization Opportunities:*\n"
                for r in unused_sorted[:5]:
                    opt_text += f"• Delete {r.resource_type} `{r.resource_id}` - Save {r.estimated_cost}\n"
                
                action_blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": opt_text}
                })
            
            # Add links and final summary
            action_blocks.extend([
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"📊 *<https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}|View Full Detailed Report in Google Sheets>*\n\n" +
                               f"*Report Generated:* {datetime.now(self.ist).strftime('%Y-%m-%d %H:%M:%S IST')}\n" +
                               f"*Next Scan:* Tomorrow at the same time\n\n" +
                               f"_For questions or to adjust monitoring settings, contact your DevOps team._"
                    }
                }
            ])
            
            # Send action items message
            action_message = {
                "text": "Action Items and Next Steps",
                "blocks": action_blocks
            }
            
            response = requests.post(self.slack_webhook_url, json=action_message)
            if response.status_code != 200:
                logger.error(f"Failed to send action items: {response.status_code}")
            
            logger.info(f"Successfully sent comprehensive Slack notification with all {len(new_resources) + len(unused_resources)} resources")
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")

    # Keep existing helper methods
    def get_resource_creator(self, resource_id: str, resource_type: str, created_time: datetime) -> str:
        """Get the creator of a resource using CloudTrail"""
        try:
            end_time = created_time + timedelta(minutes=5)
            start_time = created_time - timedelta(minutes=5)
            
            response = self.cloudtrail_client.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'ResourceName',
                        'AttributeValue': resource_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                MaxResults=10
            )
            
            for event in response.get('Events', []):
                if 'Create' in event.get('EventName', '') or 'RunInstances' in event.get('EventName', ''):
                    username = event.get('Username', 'Unknown')
                    user_type = event.get('UserIdentity', {}).get('type', '')
                    return f"{username} ({user_type})"
                    
            return 'Unknown'
        except Exception as e:
            logger.error(f"Error getting creator for {resource_id}: {str(e)}")
            return 'Unknown'

    def get_resource_allocation_time(self, allocation_id: str) -> Optional[datetime]:
        """Get allocation time for resources from CloudTrail"""
        try:
            response = self.cloudtrail_client.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'ResourceName',
                        'AttributeValue': allocation_id
                    }
                ],
                MaxResults=1
            )
            
            if response.get('Events'):
                return response['Events'][0]['EventTime']
            return None
        except:
            return None

    def check_ec2_usage(self, instance_id: str) -> tuple[str, bool]:
        """Check EC2 instance usage metrics"""
        try:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    }
                ],
                StartTime=datetime.now(timezone.utc) - timedelta(days=7),
                EndTime=datetime.now(timezone.utc),
                Period=86400,
                Statistics=['Average', 'Maximum']
            )
            
            if response['Datapoints']:
                avg_cpu = sum(d['Average'] for d in response['Datapoints']) / len(response['Datapoints'])
                max_cpu = max(d['Maximum'] for d in response['Datapoints'])
                
                net_in = self.get_metric_sum(instance_id, 'NetworkIn')
                net_out = self.get_metric_sum(instance_id, 'NetworkOut')
                
                usage_info = f"Avg CPU (7d): {avg_cpu:.2f}%, Max CPU: {max_cpu:.2f}%, Network In: {net_in:.2f} MB, Network Out: {net_out:.2f} MB"
                
                is_unused = avg_cpu < 2 and max_cpu < 10 and net_in < 100 and net_out < 100
                
                return usage_info, is_unused
            else:
                return "No metrics available", True
                
        except Exception as e:
            logger.error(f"Error checking EC2 usage for {instance_id}: {str(e)}")
            return "Metrics unavailable", False

    def get_metric_sum(self, instance_id: str, metric_name: str) -> float:
        """Get sum of a metric over the last 7 days"""
        try:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    }
                ],
                StartTime=datetime.now(timezone.utc) - timedelta(days=7),
                EndTime=datetime.now(timezone.utc),
                Period=604800,
                Statistics=['Sum']
            )
            
            if response['Datapoints']:
                return response['Datapoints'][0]['Sum'] / (1024 * 1024)
            return 0.0
        except:
            return 0.0

    def check_lb_usage(self, lb_arn: str) -> tuple[str, bool]:
        """Check Load Balancer usage"""
        try:
            response = self.elbv2_client.describe_target_groups(
                LoadBalancerArn=lb_arn
            )
            
            total_targets = 0
            healthy_targets = 0
            
            for tg in response['TargetGroups']:
                health = self.elbv2_client.describe_target_health(
                    TargetGroupArn=tg['TargetGroupArn']
                )
                total_targets += len(health['TargetHealthDescriptions'])
                healthy_targets += sum(1 for t in health['TargetHealthDescriptions'] 
                                     if t['TargetHealth']['State'] == 'healthy')
            
            lb_name = lb_arn.split('/')[-3] + '/' + lb_arn.split('/')[-2] + '/' + lb_arn.split('/')[-1]
            
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/ApplicationELB',
                MetricName='RequestCount',
                Dimensions=[
                    {
                        'Name': 'LoadBalancer',
                        'Value': lb_name
                    }
                ],
                StartTime=datetime.now(timezone.utc) - timedelta(days=7),
                EndTime=datetime.now(timezone.utc),
                Period=604800,
                Statistics=['Sum']
            )
            
            request_count = 0
            if response['Datapoints']:
                request_count = int(response['Datapoints'][0]['Sum'])
            
            usage_info = f"Targets: {healthy_targets}/{total_targets} healthy, Requests (7d): {request_count:,}"
            is_unused = total_targets == 0 or (healthy_targets == 0 and request_count < 100)
            
            return usage_info, is_unused
            
        except Exception as e:
            logger.error(f"Error checking LB usage: {str(e)}")
            return "Usage metrics unavailable", False

    def get_ec2_associations(self, instance: dict) -> str:
        """Get associated resources for EC2 instance"""
        associations = []
        
        sg_names = [sg['GroupName'] for sg in instance.get('SecurityGroups', [])]
        if sg_names:
            associations.append(f"SGs: {', '.join(sg_names[:3])}")
        
        volumes = [bdm['Ebs']['VolumeId'] for bdm in instance.get('BlockDeviceMappings', []) 
                  if 'Ebs' in bdm]
        if volumes:
            associations.append(f"Volumes: {len(volumes)}")
        
        if instance.get('PublicIpAddress'):
            associations.append(f"Public IP: {instance['PublicIpAddress']}")
        
        if instance.get('IamInstanceProfile'):
            associations.append(f"IAM Role: {instance['IamInstanceProfile'].get('Arn', '').split('/')[-1]}")
        
        return ', '.join(associations) if associations else 'No associations'

    def estimate_ec2_cost(self, instance_type: str) -> str:
        """Enhanced EC2 instance cost estimation"""
        try:
            # Extended cost map with more instance types
            cost_map = {
                't2.micro': 8.5, 't2.small': 17, 't2.medium': 34, 't2.large': 68, 't2.xlarge': 136,
                't3.micro': 7.6, 't3.small': 15.2, 't3.medium': 30.4, 't3.large': 60.8, 't3.xlarge': 121.6, 't3.2xlarge': 243.2,
                't3a.micro': 6.8, 't3a.small': 13.6, 't3a.medium': 27.2, 't3a.large': 54.4,
                'm5.large': 88, 'm5.xlarge': 176, 'm5.2xlarge': 352, 'm5.4xlarge': 704,
                'm5a.large': 79, 'm5a.xlarge': 158, 'm5a.2xlarge': 316,
                'm6i.large': 88, 'm6i.xlarge': 176, 'm6i.2xlarge': 352,
                'c5.large': 78, 'c5.xlarge': 156, 'c5.2xlarge': 312, 'c5.4xlarge': 624,
                'c5a.large': 70, 'c5a.xlarge': 140, 'c5a.2xlarge': 280,
                'r5.large': 116, 'r5.xlarge': 232, 'r5.2xlarge': 464,
                'r6i.large': 117, 'r6i.xlarge': 234, 'r6i.2xlarge': 468
            }
            
            monthly_cost = cost_map.get(instance_type, 100)
            daily_cost = monthly_cost / 30
            hourly_cost = monthly_cost / 720
            
            return f"${hourly_cost:.3f}/hr, ${daily_cost:.2f}/day, ${monthly_cost:.2f}/month"
        except:
            return "Cost estimation unavailable"

    def estimate_lb_cost(self, lb_type: str) -> str:
        """Enhanced Load Balancer cost estimation"""
        if lb_type == 'classic':
            return "$18/month + $0.008/GB data"
        elif lb_type == 'application':
            return "$16.20/month + $0.008/LCU"
        elif lb_type == 'network':
            return "$16.20/month + $0.006/NLCU"
        elif lb_type == 'gateway':
            return "$10/month + $0.004/GLCU"
        else:
            return "Cost estimation unavailable"

    def estimate_ebs_cost(self, size_gb: int, volume_type: str) -> str:
        """Enhanced EBS volume cost estimation"""
        costs = {
            'gp2': 0.10,
            'gp3': 0.08,
            'io1': 0.125,
            'io2': 0.125,
            'st1': 0.045,
            'sc1': 0.025,
            'standard': 0.05
        }
        
        cost_per_gb = costs.get(volume_type, 0.10)
        monthly_cost = size_gb * cost_per_gb
        daily_cost = monthly_cost / 30
        
        return f"${daily_cost:.2f}/day, ${monthly_cost:.2f}/month"

    def run(self):
        """Enhanced main execution function"""
        logger.info("="*80)
        logger.info("Starting Enhanced AWS Resource Monitor - Production Grade")
        logger.info(f"Account: {self.aws_account_id} | Region: {self.aws_region}")
        logger.info("="*80)
        
        try:
            all_new_resources = []
            all_unused_resources = []
            
            # Fetch all resource types
            resource_fetchers = [
                ("EC2 Instances", self.get_all_ec2_instances),
                ("Load Balancers", self.get_all_load_balancers),
                ("EBS Volumes", self.get_all_ebs_volumes),
                ("Elastic IPs", self.get_all_elastic_ips),
                ("RDS Instances", self.get_all_rds_instances),
                ("S3 Buckets", self.get_all_s3_buckets),
                ("Lambda Functions", self.get_all_lambda_functions)
            ]
            
            for resource_name, fetcher in resource_fetchers:
                logger.info(f"Fetching {resource_name}...")
                try:
                    new, unused = fetcher()
                    all_new_resources.extend(new)
                    all_unused_resources.extend(unused)
                    logger.info(f"  ✓ Found {len(new)} new, {len(unused)} unused {resource_name}")
                except Exception as e:
                    logger.error(f"  ✗ Error fetching {resource_name}: {str(e)}")
            
            logger.info(f"\nTotal: {len(all_new_resources)} NEW resources, {len(all_unused_resources)} UNUSED resources")
            
            # Send to Google Sheets
            logger.info("Updating Google Sheets...")
            self.send_to_google_sheets(all_new_resources, all_unused_resources)
            
            # Send comprehensive Slack notification
            logger.info("Sending comprehensive Slack notifications...")
            self.send_slack_notification(all_new_resources, all_unused_resources)
            
            # Print detailed console summary
            self.print_console_summary(all_new_resources, all_unused_resources)
            
            logger.info("\n" + "="*80)
            logger.info("AWS Resource Monitor scan completed successfully!")
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"Critical error in main execution: {str(e)}")
            raise

    def print_console_summary(self, new_resources: List[ResourceInfo], unused_resources: List[ResourceInfo]):
        """Print comprehensive console summary"""
        print(f"\n{'='*80}")
        print("🚀 AWS RESOURCE MONITOR - PRODUCTION GRADE REPORT")
        print(f"{'='*80}")
        print(f"Account: {self.aws_account_id}")
        print(f"Region: {self.aws_region}")
        print(f"Time: {datetime.now(self.ist).strftime('%Y-%m-%d %H:%M:%S IST')}")
        
        # Calculate totals
        total_monthly_cost = 0
        total_monthly_savings = 0
        
        for r in unused_resources:
            try:
                if '$' in r.estimated_cost and 'month' in r.estimated_cost:
                    cost_str = re.search(r'\$([\d.]+).*?month', r.estimated_cost).group(1)
                    total_monthly_savings += float(cost_str)
            except:
                pass
        
        print(f"\n📊 EXECUTIVE SUMMARY:")
        print(f"  • New Resources (24h): {len(new_resources)}")
        print(f"  • Unused Resources: {len(unused_resources)}")
        print(f"  • 💰 Potential Monthly Savings: ${total_monthly_savings:.2f}")
        print(f"  • 💸 Annual Savings Opportunity: ${total_monthly_savings * 12:.2f}")
        
        # Risk analysis
        high_risk = sum(1 for r in new_resources + unused_resources if r.risk_level == 'High')
        medium_risk = sum(1 for r in new_resources + unused_resources if r.risk_level == 'Medium')
        low_risk = sum(1 for r in new_resources + unused_resources if r.risk_level == 'Low')
        
        print(f"\n🎯 RISK ANALYSIS:")
        print(f"  • High Risk: {high_risk} resources")
        print(f"  • Medium Risk: {medium_risk} resources")
        print(f"  • Low Risk: {low_risk} resources")
        
        # Resource type breakdown
        print(f"\n📦 RESOURCE BREAKDOWN:")
        resource_types = defaultdict(lambda: {'new': 0, 'unused': 0})
        
        for r in new_resources:
            resource_types[r.resource_type]['new'] += 1
        for r in unused_resources:
            resource_types[r.resource_type]['unused'] += 1
        
        for res_type, counts in sorted(resource_types.items()):
            print(f"  • {res_type}: {counts['new']} new, {counts['unused']} unused")
        
        # Environment breakdown
        print(f"\n🏭 ENVIRONMENT DISTRIBUTION:")
        environments = defaultdict(int)
        for r in new_resources + unused_resources:
            environments[r.environment] += 1
        
        for env, count in sorted(environments.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {env}: {count} resources")
        
        # Detailed NEW resources
        if new_resources:
            print(f"\n🆕 NEW RESOURCES DETAILS (Last 24 Hours):")
            print("-" * 80)
            
            # Group by type
            new_by_type = defaultdict(list)
            for r in new_resources:
                new_by_type[r.resource_type].append(r)
            
            for res_type, resources in new_by_type.items():
                print(f"\n{res_type} ({len(resources)} total):")
                for i, r in enumerate(resources, 1):
                    status = "🔴 UNUSED" if r.is_unused else "🟢 IN USE"
                    risk = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(r.risk_level, "⚪")
                    
                    print(f"\n  {i}. [{status}] [{risk} {r.risk_level} Risk] {r.resource_name} ({r.resource_id})")
                    print(f"     Created: {r.created_time} by {r.created_by}")
                    print(f"     Environment: {r.environment} | State: {r.state}")
                    print(f"     Cost: {r.estimated_cost}")
                    print(f"     Usage: {r.usage_info}")
                    
                    if r.public_ip and r.public_ip != 'N/A':
                        print(f"     Public IP: {r.public_ip}")
                    if r.vpc_id and r.vpc_id != 'N/A':
                        print(f"     VPC: {r.vpc_id} | Subnet: {r.subnet_id}")
                    if r.owner_email:
                        print(f"     Owner: {r.owner_email} | Dept: {r.department} | Project: {r.project}")
                    if r.backup_status and r.backup_status != 'Backup status unknown':
                        print(f"     Backup: {r.backup_status}")
                    if r.encryption_status:
                        print(f"     Encryption: {r.encryption_status}")
                    
                    if r.cost_optimization_suggestions:
                        print(f"     💡 Recommendations:")
                        for suggestion in r.cost_optimization_suggestions[:3]:
                            print(f"        - {suggestion}")
        
        # Detailed UNUSED resources
        if unused_resources:
            print(f"\n🔴 UNUSED RESOURCES DETAILS (All Time):")
            print("-" * 80)
            
            # Sort by cost
            unused_sorted = sorted(unused_resources, 
                                 key=lambda x: float(re.search(r'([\d.]+)', x.estimated_cost).group(1)) if re.search(r'([\d.]+)', x.estimated_cost) else 0,
                                 reverse=True)
            
            # Group by type
            unused_by_type = defaultdict(list)
            for r in unused_sorted:
                unused_by_type[r.resource_type].append(r)
            
            for res_type, resources in unused_by_type.items():
                print(f"\n{res_type} ({len(resources)} unused):")
                for i, r in enumerate(resources, 1):
                    risk = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(r.risk_level, "⚪")
                    
                    print(f"\n  {i}. [🔴 UNUSED] [{risk} {r.risk_level} Risk] {r.resource_name} ({r.resource_id})")
                    print(f"     Created: {r.created_time}")
                    print(f"     Environment: {r.environment} | State: {r.state}")
                    print(f"     💰 Wasted Cost: {r.estimated_cost}")
                    print(f"     Usage: {r.usage_info}")
                    
                    if r.vpc_id and r.vpc_id != 'N/A':
                        print(f"     VPC: {r.vpc_id} | Subnet: {r.subnet_id}")
                    if r.owner_email:
                        print(f"     Owner: {r.owner_email} | Dept: {r.department} | Project: {r.project}")
                    if r.additional_info:
                        print(f"     Additional Info: {r.additional_info}")
                    
                    if r.cost_optimization_suggestions:
                        print(f"     💡 Immediate Actions:")
                        for suggestion in r.cost_optimization_suggestions:
                            print(f"        - {suggestion}")
        
        # Top cost optimization opportunities
        print(f"\n💰 TOP 10 COST OPTIMIZATION OPPORTUNITIES:")
        print("-" * 80)
        
        savings_opportunities = []
        for r in unused_resources:
            try:
                cost_value = 0
                if '$' in r.estimated_cost:
                    cost_match = re.search(r'\$([\d.]+)', r.estimated_cost)
                    if cost_match:
                        cost_value = float(cost_match.group(1))
                
                savings_opportunities.append((r, cost_value))
            except:
                pass
        
        savings_opportunities.sort(key=lambda x: x[1], reverse=True)
        
        total_top10_savings = 0
        for i, (r, savings) in enumerate(savings_opportunities[:10], 1):
            total_top10_savings += savings
            print(f"\n  {i}. Delete {r.resource_type}: {r.resource_id}")
            print(f"     Name: {r.resource_name}")
            print(f"     Monthly Savings: ${savings:.2f}")
            print(f"     Environment: {r.environment}")
            print(f"     Action: {r.cost_optimization_suggestions[0] if r.cost_optimization_suggestions else 'Delete resource'}")
        
        print(f"\n     Total Top 10 Savings: ${total_top10_savings:.2f}/month (${total_top10_savings * 12:.2f}/year)")
        
        # High risk resources requiring attention
        high_risk_resources = [r for r in (new_resources + unused_resources) if r.risk_level == 'High']
        if high_risk_resources:
            print(f"\n🔴 HIGH RISK RESOURCES REQUIRING IMMEDIATE ATTENTION:")
            print("-" * 80)
            
            for i, r in enumerate(high_risk_resources[:10], 1):
                print(f"\n  {i}. {r.resource_type}: {r.resource_id} ({r.resource_name})")
                print(f"     Risk Factors:")
                
                if r.public_ip and r.public_ip != 'N/A':
                    print(f"     - Public IP exposure: {r.public_ip}")
                if r.encryption_status == 'Not Encrypted':
                    print(f"     - Missing encryption")
                if r.is_unused:
                    print(f"     - Unused resource wasting money")
                if r.backup_status == 'No backup configured':
                    print(f"     - No backup configured")
                if r.compliance_status:
                    failed_checks = [k for k, v in r.compliance_status.items() if not v]
                    if failed_checks:
                        print(f"     - Failed compliance: {', '.join(failed_checks)}")
                
                print(f"     Recommended Action: {r.cost_optimization_suggestions[0] if r.cost_optimization_suggestions else 'Review and remediate'}")
        
        # Action summary
        print(f"\n📋 RECOMMENDED ACTION PLAN:")
        print("-" * 80)
        print(f"  1. IMMEDIATE (Today):")
        print(f"     • Review and delete {len(unused_resources)} unused resources")
        print(f"     • Address {high_risk} high-risk security issues")
        print(f"     • Estimated immediate savings: ${total_monthly_savings:.2f}/month")
        
        print(f"\n  2. SHORT TERM (This Week):")
        print(f"     • Convert {sum(1 for r in unused_resources if 'gp2' in r.usage_info)} gp2 volumes to gp3")
        print(f"     • Review {sum(1 for r in new_resources if not r.tags or len(r.tags) < 3)} resources with insufficient tagging")
        print(f"     • Enable encryption on {sum(1 for r in (new_resources + unused_resources) if r.encryption_status == 'Not Encrypted')} unencrypted resources")
        
        print(f"\n  3. LONG TERM (This Month):")
        print(f"     • Implement Reserved Instances for production workloads")
        print(f"     • Set up automated resource cleanup policies")
        print(f"     • Review and optimize instance sizing based on usage patterns")
        
        print(f"\n📊 FULL REPORT AVAILABLE:")
        print(f"  Google Sheets: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")
        print(f"  Generated: {datetime.now(self.ist).strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"  Next Scan: Tomorrow at the same time")
        
        print(f"\n{'='*80}")
        print("END OF REPORT")
        print(f"{'='*80}\n")

# Main execution
if __name__ == "__main__":
    try:
        monitor = AWSResourceMonitor()
        monitor.run()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise