import subprocess
import configparser

# Read the configuration from the .env file
config = configparser.ConfigParser()
config.read('.env')

# Azure subscription ID
subscription_id = config['DEFAULT']['SUBSCRIPTION_ID']

# List of US regions
us_regions = [
    "eastus", "eastus2", "southcentralus", "westus2", "westus3", 
    "centralus", "northcentralus", "westus", "westcentralus"
]

# List of other regions
other_regions = [
    "australiaeast", "southeastasia", "northeurope", "swedencentral", "uksouth", 
    "westeurope", "southafricanorth", "centralindia", "eastasia", "japaneast", 
    "koreacentral", "canadacentral", "francecentral", "germanywestcentral", 
    "italynorth", "norwayeast", "polandcentral", "switzerlandnorth", "mexicocentral", 
    "uaenorth", "brazilsouth", "israelcentral", "qatarcentral", "eastasiastage", 
    "southeastasiastage", "brazilus", "japanwest", "jioindiawest", "centraluseuap", 
    "eastus2euap", "southafricawest", "australiacentral", "australiacentral2", 
    "australiasoutheast", "jioindiacentral", "koreasouth", "southindia", "westindia", 
    "canadaeast", "francesouth", "germanynorth", "norwaywest", "switzerlandwest", 
    "ukwest", "uaecentral", "brazilsoutheast"
]

# Function to check quota status
def check_quota_status(region):
    scope = f"/subscriptions/{subscription_id}/providers/Microsoft.Compute/locations/{region}"
    print(f"Checking quota status for region: {region}")
    subprocess.run(["az", "quota", "request", "list", "--scope", scope, "--output", "table"])

# Check quota status for US regions
print("Checking quota status for US regions...")
for region in us_regions:
    check_quota_status(region)

# Check quota status for other regions
print("Checking quota status for other regions...")
for region in other_regions:
    check_quota_status(region)