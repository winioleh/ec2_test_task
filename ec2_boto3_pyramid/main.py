import boto3
from pyramid.view import view_config

from ec2_boto3_pyramid.api import get_client


@view_config(route_name='home', renderer='templates/index.jinja2', request_method='GET')
def index_view(request):
    session = boto3.Session()
    ec2_regions = session.get_available_regions(service_name='ec2')
    response = []
    errors = []
    for region in ec2_regions:
        ec2 = boto3.resource('ec2', region_name=region)
        instances = ec2.instances.all()
        try:
            for instance in instances:
                sgs = list(ec2.security_groups.all())
                sqs_ids = [i.id for i in sgs]
                client = get_client('ec2', region)
                security_groups = client.describe_security_groups(GroupIds=sqs_ids)
                acls = list(ec2.network_acls.all())
                als_ids = [i.id for i in acls]
                network_acls = client.describe_network_acls()

                instance_info = {
                    "id": instance.id,
                    "state": instance.state,
                    "launch_time": str(instance.launch_time),
                    "root_device_name": instance.root_device_name,
                    "architecture": instance.architecture,
                    "private_ip_address": instance.private_ip_address,
                    'region': str(region),
                    "acl_ids": als_ids[0],
                    "security_info": security_groups,
                    "network_acls": network_acls
                }
                if instance_info:
                    response.append(instance_info)
        except Exception as e:
            pass
    return {"response": response, "errors": errors}
