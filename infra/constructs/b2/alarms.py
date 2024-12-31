from constructs import Construct
from constructs_package.constants import AwsStage
from infra.constructs.b1.alarm_group import B1AlarmGroup
from infra.constructs.b1.billing_alarm import B1BillingAlarm


class B2Alarms(Construct):
    """Set up Alarms"""

    def __init__(
        self,
        scope: Construct,
        id: str,
        stage: AwsStage,
    ) -> None:
        super().__init__(scope, id)

        self.platform = B1AlarmGroup(
            scope=self,
            id="PlatformGroup",
            group_name="platform",
            subscription_enabled=stage in (AwsStage.PRODUCTION, AwsStage.MANAGEMENT),
            email_subscriptions=["platform-alarms@real-life-iac.com"]
            # Add other emails such PagerDuty, Slack, etc.
        )

        self.frontend = B1AlarmGroup(
            scope=self,
            id="FrontendGroup",
            group_name="frontend",
            subscription_enabled=stage == AwsStage.PRODUCTION,
            email_subscriptions=["frontend-alarms@real-life-iac.com"],
        )

        B1BillingAlarm(
            scope=self,
            id="200UsdBillingAlarm",
            notify_topic=self.platform.topic,
            threshold_usd=200,
        )
