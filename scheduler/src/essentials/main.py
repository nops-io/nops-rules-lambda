import json
import logging

from idle import ebs_cleanup_with_snapshot
from idle import ebs_cleanup_without_snapshot
from idle import terminate_ec2_instance
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
    "essentials__scheduler": {
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
    "essentials__tag_resources": {
        "ec2": {"update_tag": update_tag_ec2},
        "rds": {"update_tag": update_tag_rds},
        "rds_cluster": {"update_tag": update_tag_rds_cluster},
        "autoscaling_groups": {"update_tag": update_tag_autoscaling_group},
        "eks_nodegroup": {"update_tag": update_tag_nodegroup},
    },
    "essentials__storage": {
        "ebs": {"ebs_migration": ec2_ebs_migration},
        "asg": {"ebs_migration": asg_ebs_migration},
    },
    "essentials__rightsizing": {
        "ec2": {"ec2_rightsizing": ec2_rightsizing},
    },
    "essentials__idle_resources": {
        "ec2": {
            "stop": stop_ec2_instance,
            "terminate": terminate_ec2_instance,
        },
        "ebs": {
            "delete_volume_with_snapshot": ebs_cleanup_with_snapshot,
            "delete_volume": ebs_cleanup_without_snapshot,
        }
    },
}


def lambda_handler(event, context):
    logging.info(f'Received event: {event}')

    event_type = event["detail"]["event_type"]
    if event_type not in (
        "essentials__scheduler",  # Essentials Scheduler
        "essentials__storage",  # Essentials Storage
        "essentials__rightsizing",  # Essentials Rightsizing
        "essentials__idle_resources",  # Essentials Idle Resources
        "essentials__tag_resources",  # Essentials Tagging
    ):
        return {"Message": "Event type not supported"}

    action = event["detail"]["action"]
    resources = event["detail"]["scheduler"]["resources"]
    messages = []
    for resource in resources:
        try:
            handler = HANDLER_MAP.get(event_type, {}).get(resource.get("item_type"), {}).get(action)
            messages.append(handler(resource))
        except Exception as e:
            logging.error(e)

    msg = {"results": messages}

    return {"Message": json.dumps(msg)}
