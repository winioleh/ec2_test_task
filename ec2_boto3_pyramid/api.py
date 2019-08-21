import botocore
from pyramid.view import view_config
import boto3


def get_client(service, region):
    """Get an AWS client for a service."""
    session = boto3.Session()
    return session.client(service, region_name=region)

def generate_rule_number(client):
    network_acls = client.describe_network_acls()['NetworkAcls']
    rule_numbers = []
    for item in network_acls:
        for entry in item['Entries']:
            rule_numbers.append(entry['RuleNumber'])
    return rule_numbers[-2]+10


def create_network_acl_ingress_entry(acl_id, protocol, cidr_block, allow, region):
    client = get_client("ec2", region)
    params = {}
    params["NetworkAclId"] = acl_id
    params["RuleNumber"] = generate_rule_number(client)
    params["Protocol"] = protocol
    params["CidrBlock"] = cidr_block
    params["Egress"] = False
    params["RuleAction"] = "ALLOW" if allow else "DENY"
    return client.create_network_acl_entry(**params)



def create_network_acl_engress_entry(acl_id, protocol, cidr_block, allow, region):
    client = get_client("ec2", region)
    params = {}
    params["NetworkAclId"] = acl_id
    params["RuleNumber"] = generate_rule_number(client)
    params["Protocol"] = protocol
    params["CidrBlock"] = cidr_block
    params["Egress"] = True
    params["RuleAction"] = "ALLOW" if allow else "DENY"
    return client.create_network_acl_entry(**params)


@view_config(route_name='api_block_access', renderer='json', request_method='POST')
def post_api_ec2_view(request):
    import re

    data = request.json_body
    ip = data.get('ip_value')
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
        ip = ip + '/24'
        if data.get('inbound_btn'):
            response = create_network_acl_ingress_entry(data.get('acl_ids'), '-1', ip, False, data.get('region'))
        elif data.get('outbound_btn'):
            response = create_network_acl_engress_entry(data.get('acl_ids'), '-1', ip, False, data.get('region'))
        else:
            response="Choose inbound of outbound access"
        return {'response': response}
    else:
        return {'response': 'Bad IP'}
