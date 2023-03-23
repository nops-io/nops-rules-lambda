def get_ec2_instance_id_from_resource(resource):
    arn = resource.get("resource_arn", "")
    resource_id = resource.get("resource_id", "")
    if resource_id.startswith("i-"):
        return resource_id
    if not arn and resource_id.startswith("arn:"):
        arn = resource_id
    if arn.startswith("arn:"):
        resource_id = arn.split("/")[-1]
    else:
        raise Exception("Invalid EC2 instance id")


def get_db_identifier_from_resource(resource):
    # We might have arn or cluser identifier in resource_id
    arn = resource.get("resource_arn", "") or resource.get("resource_id", "")
    return arn.split(":")[-1]


def get_autoscaling_name_from_resource(resource):
    arn = resource.get("resource_arn", "") or resource.get("resource_id", "")
    if arn:
        return arn.split("/")[-1]
    return resource.get("resource_name")


def get_arn_from_resource(resource):
    return resource.get("resource_arn", "") or resource.get("resource_id", "")
