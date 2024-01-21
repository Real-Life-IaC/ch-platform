from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as sub
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class B1AlarmGroup(Construct):
    """Create a topic to fan out alarms to subscribers"""

    def __init__(
        self,
        scope: Construct,
        id: str,
        group_name: str,
        subscription_enabled: bool,
        email_subscriptions: list[str],
    ) -> None:
        super().__init__(scope, id)

        self.topic = sns.Topic(
            scope=self,
            id="Topic",
            display_name=f"{group_name}-alarm-topic",
        )

        if subscription_enabled:
            for email in email_subscriptions:
                self.topic.add_subscription(
                    topic_subscription=sub.EmailSubscription(
                        email_address=email,
                    )
                )

        ssm.StringParameter(
            scope=self,
            id="TopicArn",
            string_value=self.topic.topic_arn,
            description="Topic that send alarms to the {group_name} group",
            parameter_name=f"/platform/alarms/{group_name}/sns/arn",
        )
