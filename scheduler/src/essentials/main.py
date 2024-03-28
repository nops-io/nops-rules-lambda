import json
import logging

from idle import ebs_delete_volume
from rightsizing import ec2_rightsizing
from scheduler import modify_db_instance
from scheduler import start_autoscaling_group
from scheduler import start_ec2_instance
from scheduler import start_nodegroup
from scheduler import start_rds_cluster
from scheduler import start_rds_instance
from scheduler import stop_autoscaling_group
from scheduler import stop_ec2_instance
from scheduler import stop_nodegroup
from scheduler import stop_rds_cluster
from scheduler import stop_rds_instance
from scheduler import update_ec2_auto_scaling
from storage import asg_ebs_migration
from storage import ec2_ebs_migration
from tagging import update_tag_autoscaling_group
from tagging import update_tag_ec2
from tagging import update_tag_nodegroup
from tagging import update_tag_rds
from tagging import update_tag_rds_cluster


HANDLER_MAP = {
    "scheduler_start_stop": {
        "ec2": {
            "start": start_ec2_instance,
            "stop": stop_ec2_instance,
        },
        "rds": {
            "start": start_rds_instance,
            "stop": stop_rds_instance,
            "modify": modify_db_instance,
        },
        "rds_cluster": {
            "start": start_rds_cluster,
            "stop": stop_rds_cluster,
        },
        "autoscaling_groups": {
            "update_ec2_auto_scaling": update_ec2_auto_scaling,
            "start": start_autoscaling_group,
            "stop": stop_autoscaling_group,
        },
        "eks_nodegroup": {
            "start": start_nodegroup,
            "stop": stop_nodegroup,
        },
    },
    "nops_scheduler_tag_resource": {
        "ec2": {"update_tag": update_tag_ec2},
        "rds": {"update_tag": update_tag_rds},
        "rds_cluster": {"update_tag": update_tag_rds_cluster},
        "autoscaling_groups": {"update_tag": update_tag_autoscaling_group},
        "eks_nodegroup": {"update_tag": update_tag_nodegroup},
    },
    "nswitch_essential": {
        "ebs": {"ebs_migration": ec2_ebs_migration},
        "asg": {"ebs_migration": asg_ebs_migration},
        "ec2": {"ec2_rightsizing": ec2_rightsizing},  # Essentials Rightsizing
    },
    "essentials_idle_resources": {
        "ec2": {
            "stop": stop_ec2_instance,
        },
        "ebs": {
            "delete_volume": ebs_delete_volume,
        }
    },
}


def lambda_handler(event, context):
    event_type = event["detail"]["event_type"]
    if event_type not in (
        "scheduler_start_stop",  # Essentials Scheduler
        "nops_scheduler_tag_resource",  # Essentials Scheduler
        "nswitch_essential",  # Essentials Storage, Essentials Rightsizing
        "essentials_idle_resources",  # Essentials Idle Resources
    ):
        return {"Message": "Event type not supported"}

    action = event["detail"]["action"]
    resources = event["detail"]["scheduler"]["resources"]
    messages = []
    for resource in resources:
        try:
            handler = HANDLER_MAP.get(resource.get("item_type"), {}).get(action)
            messages.append(handler(resource))
        except Exception as e:
            logging.error(e)
            print(e)

    msg = {"results": messages}
    print(msg)

    return {"Message": json.dumps(msg)}
