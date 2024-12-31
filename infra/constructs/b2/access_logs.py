import aws_cdk as cdk

from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class B2AccessLogs(Construct):
    """Create resources for storing access logs"""

    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        bucket = s3.Bucket(
            scope=self,
            id="Bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            access_control=s3.BucketAccessControl.LOG_DELIVERY_WRITE,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=False,
        )

        bucket.add_lifecycle_rule(
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                    transition_after=cdk.Duration.days(amount=60),
                )
            ],
        )

        # Allow S3 to write access logs to the bucket
        bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:PutObject"],
                resources=[bucket.arn_for_objects("*")],
                principals=[
                    iam.ServicePrincipal(service="logging.s3.amazonaws.com"),
                ],
                conditions={"StringEquals": {"aws:SourceAccount": [cdk.Aws.ACCOUNT_ID]}},
            )
        )

        # Allow ELB to write access logs to the bucket
        bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:PutObject"],
                resources=[bucket.arn_for_objects(key_pattern="*")],
                principals=[
                    iam.AccountPrincipal(account_id="127311923021")
                ],  # us-east-1 AWS elb-account-id
            )
        )

        ssm.StringParameter(
            scope=self,
            id="BucketArn",
            string_value=bucket.bucket_arn,
            description="Access Logs bucket ARN",
            parameter_name="/platform/access-logs/bucket/arn",
        )

        ssm.StringParameter(
            scope=self,
            id="BucketName",
            string_value=bucket.bucket_name,
            description="Access Logs bucket name",
            parameter_name="/platform/access-logs/bucket/name",
        )
