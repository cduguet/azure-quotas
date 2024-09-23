import subprocess
import json
import configparser

# Read the configuration from the .env file
config = configparser.ConfigParser()
config.read('.env')
DEFAULT_SUBSCRIPTION = config['DEFAULT']['SUBSCRIPTION_ID']


def run_az_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    return json.loads(result.stdout)

def get_all_regions():
    command = "az account list-locations --output json"
    return run_az_command(command)

def get_vms_in_region(region):
    command = f"az vm list --location {region} --output json"
    return run_az_command(command)

def get_compute_quotas(region):
    command = f"az quota list --scope /subscriptions/DEFAULT_SUBSCRIPTION/providers/Microsoft.Compute/locations/{region} --output json"
    return run_az_command(command)

def format_to_markdown_table(data, quotas):
    headers = ["Name", "Resource Group", "Location", "VM Size", "GPU", "Compute Quota", "Used Quota"]
    table = f"| {' | '.join(headers)} |\n"
    table += f"| {' | '.join(['---'] * len(headers))} |\n"
    for vm in data:
        gpu_info = vm.get("storageProfile", {}).get("imageReference", {}).get("sku", "None")
        quota_info = quotas.get(vm["location"], {})
        row = [
            vm.get("name", ""),
            vm.get("resourceGroup", ""),
            vm.get("location", ""),
            vm.get("hardwareProfile", {}).get("vmSize", ""),
            gpu_info,
            str(quota_info.get("limit", "N/A")),
            str(quota_info.get("currentValue", "N/A"))
        ]
        table += f"| {' | '.join(row)} |\n"
    return table

def main():
    regions = get_all_regions()
    all_vms = []
    quotas = {}
    for region in regions:
        region_name = region["name"]
        vms = get_vms_in_region(region_name)
        all_vms.extend(vms)
        quotas[region_name] = get_compute_quotas(region_name)
    
    markdown_table = format_to_markdown_table(all_vms, quotas)
    print(markdown_table)

if __name__ == "__main__":
    main()