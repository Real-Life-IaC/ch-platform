import aws_cdk as cdk
import aws_cdk.aws_iam as iam

from aws_cdk import aws_ssm as ssm
from constructs import Construct
from constructs_package.constants import AwsStage


class B2GithubOidc(Construct):
    """
    Set up Github Open ID Connect (OIDC)

    This allows github actions to connect to AWS without access keys.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        stage: AwsStage,
    ) -> None:
        super().__init__(scope, id)

        oidc_provider = iam.OpenIdConnectProvider(
            scope=self,
            id="Provider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"],
            thumbprints=[
                "6938fd4d98bab03faadb97b34396831e3780aea1",
                "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
            ],
        )

        # Only allow connections from Real-Life-IaC org
        # Only allows access when using github environments.
        permissions = [
            f"repo:Real-Life-IaC/*:environment:{stage}",
        ]
        # Allow pushing to sandbox account from any branch/environment
        if stage == AwsStage.SANDBOX:
            permissions.append("repo:Real-Life-IaC/*:*")

        # Allow assuming CDK roles (created with cdk bootstrap)
        deployer_role = iam.Role(
            scope=self,
            id="DeployerRole",
            assumed_by=iam.WebIdentityPrincipal(
                identity_provider=oidc_provider.open_id_connect_provider_arn,
                conditions={
                    "ForAnyValue:StringLike": {
                        "token.actions.githubusercontent.com:sub": permissions
                    },
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                    },
                },
            ),
            inline_policies={
                "AllowAssumeRole": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=["sts:AssumeRole"],
                            resources=[
                                f"arn:aws:iam::{cdk.Aws.ACCOUNT_ID}:role/cdk-*-{cdk.Aws.ACCOUNT_ID}-*"
                            ],
                        )
                    ]
                )
            },
        )

        # Create a SSM parameter for the private hosted zone name
        ssm.StringParameter(
            scope=self,
            id="DeployerRoleArn",
            string_value=deployer_role.role_arn,
            description="Deployer Role Arn",
            parameter_name="/platform/github-oidc/deployer-role/arn",
        )
