AUTOSCALING_LAMBDA_EVENT = {
    "version": "0",
    "id": "601dce79-d826-6d29-8ae5-08f9b3144315",
    "detail-type": "nops_scheduler_start_stop",
    "source": "aws.partner/nops.io/12345677901/nops_uat_notification_14875_nopsqa-UAT-demo",
    "account": "12345677901",
    "time": "2022-12-05T20:00:00Z",
    "region": "eu-north-1",
    "resources": [
        "arn:aws:autoscaling:us-east-1:12345677901:autoScalingGroup:71f448aa-8436-4cdb-888e-b9d417bb12c8:autoScalingGroupName/JENKINS-SLAVE-TEST"
    ],
    "detail": {
        "event_type": "scheduler_start_stop",
        "action": "update_ec2_auto_scaling",
        "action_details": {"DesiredCapacity": 2},
        "action_id": 607,
        "event_timestamp": 1.6702704e9,
        "scheduler": {
            "id": "db140d55-bb88-4283-b24f-5fbb8e528598",
            "client": 14875,
            "project": 17637,
            "user": 3127,
            "name": "liza-5 dec-dynamic",
            "account_number": "12345677901",
            "resources": [
                {
                    "id": 535,
                    "created": "2022-12-05T19:17:25.311392Z",
                    "modified": "2022-12-05T19:17:25.311392Z",
                    "item_type": "autoscaling_groups",
                    "item_id": "1234556",
                    "resource_id": "arn:aws:autoscaling:us-east-1:12345677901:autoScalingGroup:71f448aa-8436-4cdb-888e-b9d417bb12c8:autoScalingGroupName/JENKINS-SLAVE-TEST",
                    "resource_name": "JENKINS-SLAVE-TEST",
                    "resource_arn": None,
                    "state": "active",
                    "region": "us-east-1",
                    "scheduler": "db140d55-bb88-4283-b24f-5fbb8e528598",
                }
            ],
            "actions": [
                {
                    "id": 607,
                    "created": "2022-12-05T19:17:25.308255Z",
                    "modified": "2022-12-05T19:17:25.308255Z",
                    "action": "update_auto_scaling_group",
                    "action_details": {"DesiredCapacity": 2},
                    "action_type": "selected_day_of_week",
                    "day_of_week": ["mon"],
                    "hour": 20,
                    "minute": 0,
                    "state": "active",
                    "last_run": None,
                    "last_manual_trigger": None,
                    "run_date": None,
                    "scheduler": "db140d55-bb88-4283-b24f-5fbb8e528598",
                },
                {
                    "id": 608,
                    "created": "2022-12-05T19:17:25.310165Z",
                    "modified": "2022-12-05T19:17:25.310165Z",
                    "action": "update_auto_scaling_group",
                    "action_details": {"DesiredCapacity": 3},
                    "action_type": "selected_day_of_week",
                    "day_of_week": ["mon"],
                    "hour": 8,
                    "minute": 0,
                    "state": "active",
                    "last_run": None,
                    "last_manual_trigger": None,
                    "run_date": None,
                    "scheduler": "db140d55-bb88-4283-b24f-5fbb8e528598",
                },
            ],
            "state": "active",
            "eventbridge_configuration": "1e17e4ad-1590-4401-baf6-d0a472394c0b",
            "scheduler_for": "scheduler_start_stop",
        },
        "triggered_by": "automatically",
    },
}

NODEGROUP_START_LAMBDA_EVENT = {
    "version": "0",
    "id": "601dce79-d826-6d29-8ae5-08f9b3144315",
    "detail-type": "nops_scheduler_start_stop",
    "source": "aws.partner/nops.io/12345677901/nops_uat_notification_14875_nopsqa-UAT-demo",
    "account": "12345677901",
    "time": "2022-12-05T20:00:00Z",
    "region": "eu-north-1",
    "resources": [],
    "detail": {
        "event_type": "scheduler_start_stop",
        "action": "start",
        "action_id": 607,
        "event_timestamp": 1.6702704e9,
        "scheduler": {
            "id": "db140d55-bb88-4283-b24f-5fbb8e528598",
            "client": 14875,
            "project": 17637,
            "user": 3127,
            "name": "liza-5 dec-dynamic",
            "account_number": "12345677901",
            "resources": [],
            "actions": [],
            "state": "active",
            "eventbridge_configuration": "1e17e4ad-1590-4401-baf6-d0a472394c0b",
            "scheduler_for": "scheduler_start_stop",
        },
        "triggered_by": "automatically",
    },
}
