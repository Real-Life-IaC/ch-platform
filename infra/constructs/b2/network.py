from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm
from cdk_fck_nat import FckNatInstanceProvider
from constructs import Construct


class B2Network(Construct):
    """Create a VPC and Subnets following specific allocations"""

    def __init__(
        self,
        scope: Construct,
        id: str,
        cidr_block: str,
        max_azs: int,
        nat_gateways: int,
    ) -> None:
        super().__init__(scope, id)

        nat_provider = FckNatInstanceProvider(
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T4G, ec2.InstanceSize.NANO
            ),
            enable_cloud_watch=True,
            enable_ssm=True,
        )

        # Create the VPC using the L2 construct
        self.vpc = ec2.Vpc(
            scope=self,
            id="Vpc",
            max_azs=max_azs,
            nat_gateway_provider=nat_provider,
            subnet_configuration=self.subnet_configuration,
            ip_addresses=ec2.IpAddresses.cidr(cidr_block=cidr_block),
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )

        nat_provider.security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.all_traffic(),
        )

        # Add a flow log to the VPC
        self.vpc.add_flow_log(id="FlowLog")

        # Create a SSM parameter for the VPC ID
        ssm.StringParameter(
            scope=self,
            id="VpcId",
            string_value=self.vpc.vpc_id,
            description="VPC Id",
            parameter_name="/platform/vpc/id",
        )

    @property
    def subnet_configuration(self) -> list[ec2.SubnetConfiguration]:
        """Return the subnet configuration"""
        return [
            ec2.SubnetConfiguration(
                name="PublicSubnet",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=21,
            ),
            ec2.SubnetConfiguration(
                name="PrivateSubnet",
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                cidr_mask=19,
            ),
            ec2.SubnetConfiguration(
                name="IsolatedSubnet",
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                cidr_mask=22,
            ),
            ec2.SubnetConfiguration(
                name="VpnSubnet",
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                cidr_mask=27,
            ),
        ]
