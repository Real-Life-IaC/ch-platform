import aws_cdk as cdk

from aws_cdk import aws_cloudtrail as cloudtrail
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class B2Cloudtrail(Construct):
    """Create resources for auditing with cloudtrail"""

    def __init__(
        self,
        scope: Construct,
        id: str,
        kms_key: kms.Key,
    ) -> None:
        super().__init__(scope, id)

        bucket = s3.Bucket(
            scope=self,
            id="Bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=False,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            enforce_ssl=False,
        )

        bucket.add_lifecycle_rule(
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                    transition_after=cdk.Duration.days(amount=60),
                )
            ],
        )

        trail = cloudtrail.Trail(
            scope=self,
            id="Cloudtrail",
            bucket=bucket,
            trail_name="cloudtrail",
            encryption_key=kms_key,
            send_to_cloud_watch_logs=True,
            cloud_watch_logs_retention=logs.RetentionDays.FOUR_MONTHS,
            enable_file_validation=True,
            include_global_service_events=True,
            is_multi_region_trail=True,
            is_organization_trail=False,
            management_events=cloudtrail.ReadWriteType.ALL,
            insight_types=[
                cloudtrail.InsightType.API_CALL_RATE,
                cloudtrail.InsightType.API_ERROR_RATE,
            ],
        )
        kms_key.grant_encrypt_decrypt(
            iam.ServicePrincipal(
                service="cloudtrail.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "aws:SourceArn": f"arn:aws:cloudtrail:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:trail/cloudtrail"  # noqa: B950
                    },
                    "StringLike": {
                        "kms:EncryptionContext:aws:cloudtrail:arn": f"arn:aws:cloudtrail:*:{cdk.Aws.ACCOUNT_ID}:trail/*"  # noqa: B950
                    },
                },
            )
        )

        trail.log_all_lambda_data_events()
        trail.log_all_s3_data_events()

        ssm.StringParameter(
            scope=self,
            id="BucketArn",
            string_value=bucket.bucket_arn,
            description="Cloudtrail bucket ARN",
            parameter_name="/platform/cloudtrail/bucket/arn",
        )

        ssm.StringParameter(
            scope=self,
            id="BucketName",
            string_value=bucket.bucket_name,
            description="Cloudtrail bucket name",
            parameter_name="/platform/cloudtrail/bucket/name",
        )

        ssm.StringParameter(
            scope=self,
            id="TrailArn",
            string_value=trail.trail_arn,
            description="Cloudtrail trail ARN",
            parameter_name="/platform/cloudtrail/trail/arn",
        )
