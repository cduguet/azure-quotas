import subprocess
import json
import argparse
from typing import List, Dict
import configparser

# Read the configuration from the .env file
config = configparser.ConfigParser()
config.read('.env')
DEFAULT_SUBSCRIPTION = config['DEFAULT']['SUBSCRIPTION_ID']

# list with GPU types of each family
# https://docs.microsoft.com/en-us/azure/machine-learning/concept-compute-instance#gpu
GPU_TYPES = {"A10v": "A10",
             "A100v": "A100",
             "NCSv3": "V100",
             "NCv3": "V100",
             "NCv2": "P100",
             "T4": "T4",
             "H100": "H100",
             "ND": "P40",
             "NVSv3": "M60",
             "NVasv4": "AMD MI25",
             "NP": "P100"}


def get_ml_compute_list(resource_group: str, workspace: str, gpus_only: bool) -> List[Dict[str, any]]:
    cmd = f"az ml compute list-sizes -g {resource_group} -w {workspace}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    compute_list = json.loads(result.stdout)

    # Now extract the actual quotas
    cmd = f"az ml compute list-usage -g {resource_group} -w {workspace}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    compute_quotas = json.loads(result.stdout)
    
    print(f"Azure ML Compute List for Workspace: {workspace}. {'GPUs only' if gpus_only else 'All instances'}.")
    print(f"| {'Family':<25} | {'Name':<25} | GPUs | GPU_Type* | vCPUs | Limit  | Used   |")
    print(f"|{'-'*27}|{'-'*27}|{'-'*6}|{'-'*11}|{'-'*7}|{'-'*8}|{'-'*8}|")
    for compute in compute_list:
        gpus = compute.get("gpus", 0)
        if gpus != 0 or not gpus_only:
            name = compute.get("name", "N/A")
            family = compute.get("family", "N/A").replace(" ", "")
            vcpus = compute.get("v_cp_us", "N/A")
            quota = next((quota for quota in compute_quotas if quota.get("name").get("value").replace(" ", "").lower() == family.lower()), None)
            limit = quota.get("limit", "N/A") if quota else "N/A"
            gpu_type = next((gpu for key, gpu in GPU_TYPES.items() if key.lower() in family.lower()), "N/A")
            used = quota.get("current_value", "N/A") if quota else "N/A"
            print(f"| {family:<25} | {name:<25} | {gpus:<4} | {gpu_type:9} | {vcpus:<5} | {limit:<6} | {used:<6} |")
    return compute_list

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Get Azure ML compute list sizes.")
    parser.add_argument("--resource_group", help="The resource group name.", default="ng")
    parser.add_argument("--workspace", help="The workspace name.", default="nuvo-ml-workspace")
    parser.add_argument("--subscription", help="The subscription id.", default=DEFAULT_SUBSCRIPTION)
    parser.add_argument("--gpus-only", help="Only show GPU instances.", default=False, action="store_true")
    args = parser.parse_args()
    compute_list = get_ml_compute_list(args.resource_group, args.workspace, args.gpus_only)
    # print(json.dumps(compute_list, indent=2))
 