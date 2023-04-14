#!/usr/bin/env python3

## automation to create the special purpose storage class inside the workload clusters

import helper
import interpolate
import pmsg
import os

yaml_source = os.environ["config_file"]
template_file = "templates/custom_storage_class.yaml"
output_file = "/tmp/sc_result"
interpolate.interpolate_from_yaml_to_template(yaml_source, template_file, output_file)
customsc = os.environ["custom_storage_class_name"]
storagepolicy = os.environ["storage_policy_name"]

# Make sure K8s context is set to workload cluster prior to running below commands 
# Does this storage class exist in workload cluster?
if helper.run_a_command("kubectl get sc " + customsc) == 0:
    pmsg.green("Custom Storage Class with desired reclaimPolicy & Bind mode exists")
    exit(0)

# Construct the kubectl apply command
pmsg.normal("Publishing Custom Storage class...")
cmd = ['kubectl', 'apply', '-f', output_file]
if helper.check_for_result(cmd,"storageclass.storage.k8s.io.* created") :
    if helper.check_for_result_for_a_time(["kubectl","get","sc",customsc,"-o","jsonpath='{.parameters.svStorageClass}'"],storagepolicy, 5, 5):
        pmsg.green("Storage class " + customsc + " OK.")   
    else: 
        pmsg.fail("Failed to create the storage class, check cluster events")
        exit(1)
else:
    pmsg.fail ("Failed to apply the custom storage class create YAML")
    exit(1)
exit(0)
