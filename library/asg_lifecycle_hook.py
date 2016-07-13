#!/usr/bin/env python
from troposphere import Base64, Parameter, Output, Ref, Template, Join
from troposphere.autoscaling import LifecycleHook
import collections
from ansible import utils, errors
import json
import yaml
import sys
from ansible.module_utils.basic import *


def create_parameters(template,module):
    parameters = {}
    asg_name = template.add_parameter(Parameter(
        "ASGName",
        Description="Name of the AutoScaling group to which to add the LifecycleHook",
        Type="String",
    ))
    parameters['asg_name'] = asg_name

    notification_arn = template.add_parameter(Parameter(
        "NotificationTargetARN",
        Description="ARN of resource targetted by LifecycleHook",
        Type="String",
    ))
    parameters['notification_arn'] = notification_arn

    iam_role_arn = template.add_parameter(Parameter(
        "IAMRoleARN",
        Description="ARN of the IAM role used by the LifecycleHook",
        Type="String",
    ))
    parameters['iam_role_arn'] = iam_role_arn

    lifecycle_transition = template.add_parameter(Parameter(
        "LifecycleTransition",
        Description="The state of the Amazon EC2 instance to which you want to attach the lifecycle hook",
        Type="String",
    ))
    parameters['lifecycle_transition'] = lifecycle_transition

    if module.params.get("asg_hook_default_result"):
        parameters['default_result'] = module.params.get("asg_hook_default_result")

    if module.params.get("asg_hook_heartbeat_timeout"):
        parameters['heartbeat_timeout']=module.params.get("asg_hook_heartbeat_timeout")

    if module.params.get("asg_hook_notification_metadata"):
        parameters['notification_metadata']=module.params.get("asg_hook_notification_metadata")

    return parameters


def create_hook(template,parameters):
    hook = template.add_resource(LifecycleHook("AOEU",
        AutoScalingGroupName=Ref(parameters['asg_name']),
        NotificationTargetARN=Ref(parameters['notification_arn']),
        RoleARN=Ref(parameters['iam_role_arn']),
        LifecycleTransition=Ref(parameters['lifecycle_transition'])
    ))

    if 'default_result' in parameters:
        hook.DefaultResult = parameters['default_result']

    if 'heartbeat_timeout' in parameters:
        hook.HeartbeatTimeout = parameters['heartbeat_timeout']

    if 'notification_metadata' in parameters:
        hook.NotificationMetadata = parameters['notification_metadata']

    return hook

def main():
    module = AnsibleModule(
        argument_spec = dict(
          asg_hook_default_result = dict(required=False, type='str'),
          asg_hook_heartbeat_timeout = dict(required=False, type='int'),
          asg_hook_notification_metadata = dict(required=False, type='str')

        )
    )
    template = Template()
    parameters = create_parameters(template, module)
    hook = create_hook(template, parameters)

    module.exit_json(
        Changed=False,
        Failed=False,
        Result=template.to_json()
    )

if __name__ == "__main__":
    main()
