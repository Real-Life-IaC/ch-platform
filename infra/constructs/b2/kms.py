from aws_cdk import aws_kms as kms
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class B2Kms(Construct):
    """Create a shared KMS key for encrypting/decrypting"""

    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        self.key = kms.Key(
            scope=self,
            id="DefaultKey",
            description="Default KMS key to be used for encryption/decryption",
            alias="default-key",
            enable_key_rotation=True,
        )

        ssm.StringParameter(
            scope=self,
            id="DefaultKeyArn",
            string_value=self.key.key_arn,
            description="Default KMS Key ARN",
            parameter_name="/platform/kms/default-key/arn",
        )

        ssm.StringParameter(
            scope=self,
            id="DefaultKeyId",
            string_value=self.key.key_id,
            description="Default KMS Key ID",
            parameter_name="/platform/kms/default-key/id",
        )
