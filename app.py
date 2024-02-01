import aws_cdk as cdk

from constructs_package.constants import AwsAccountId
from constructs_package.constants import AwsRegion
from constructs_package.constants import AwsStage
from infra.stack import PlatformStack


app = cdk.App()

PlatformStack(
    scope=app,
    id=f"Platform-{AwsStage.SANDBOX}",
    env=cdk.Environment(
        account=AwsAccountId.SANDBOX, region=AwsRegion.US_EAST_1
    ),
    stage=AwsStage.SANDBOX,
    cidr_block="10.112.0.0/16",
    max_azs=2,
    nat_gateways=0,
)

PlatformStack(
    scope=app,
    id=f"Platform-{AwsStage.STAGING}",
    env=cdk.Environment(
        account=AwsAccountId.STAGING, region=AwsRegion.US_EAST_1
    ),
    stage=AwsStage.STAGING,
    cidr_block="10.80.0.0/16",
    max_azs=2,
    nat_gateways=0,
)

PlatformStack(
    scope=app,
    id=f"Platform-{AwsStage.PRODUCTION}",
    env=cdk.Environment(
        account=AwsAccountId.PRODUCTION, region=AwsRegion.US_EAST_1
    ),
    stage=AwsStage.PRODUCTION,
    cidr_block="10.16.0.0/16",
    max_azs=3,
    nat_gateways=0,  # In real-life #NATs = #AZs
)  # TODO: Add NATs to the production VPC

PlatformStack(
    scope=app,
    id=f"Platform-{AwsStage.MANAGEMENT}",
    env=cdk.Environment(
        account=AwsAccountId.MANAGEMENT, region=AwsRegion.US_EAST_1
    ),
    stage=AwsStage.MANAGEMENT,
    cidr_block="10.144.0.0/16",
    max_azs=3,
    nat_gateways=0,
)

app.synth()
