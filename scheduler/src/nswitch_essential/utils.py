def get_ebs_volume_id_from_resource(resource):
    arn = resource.get("resource_arn", "")
    resource_id = resource.get("resource_id", "")
    if resource_id.startswith("vol-"):
        return resource_id
    if not arn and resource_id.startswith("arn:"):
        arn = resource_id
    if arn.startswith("arn:"):
        resource_id = arn.split("/")[-1]
    else:
        raise Exception("Invalid EBS volume id")
