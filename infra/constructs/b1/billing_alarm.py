import aws_cdk as cdk

from aws_cdk import aws_cloudwatch as cw
from aws_cdk import aws_cloudwatch_actions as cw_actions
from aws_cdk import aws_sns as sns
from constructs import Construct


class B1BillingAlarm(Construct):
    """Create an alarm for billing estimated charges"""

    def __init__(
        self,
        scope: Construct,
        id: str,
        notify_topic: sns.ITopic,
        threshold_usd: int,
    ) -> None:
        super().__init__(scope, id)

        estimated_charges_metric = cw.Metric(
            metric_name="EstimatedCharges",
            namespace="AWS/Billing",
            statistic="Maximum",
            dimensions_map={"Currency": "USD"},
            period=cdk.Duration.hours(9),
        )

        alarm = cw.Alarm(
            scope=self,
            id="EstimatedChargesAlarm",
            alarm_description=f"Exceeded {threshold_usd} USD in estimated charges",
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            evaluation_periods=1,
            metric=estimated_charges_metric,
            threshold=threshold_usd,
        )

        alarm.add_alarm_action(
            cw_actions.SnsAction(
                topic=notify_topic,
            )
        )
