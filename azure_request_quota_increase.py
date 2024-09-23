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

# Details for the support request
resource_name="StandardNCADSA10v4Family"
resource_type="dedicated"
limit_value=36
contact_email = config['DEFAULT']['CONTACT_EMAIL']

# Function to create a quota request
def create_quota_request(region):
    scope = f"/subscriptions/{subscription_id}/providers/Microsoft.Compute/locations/{region}"
    limit_object = f"value={limit_value}"
    
    print(f"Creating quota request for region: {region}")
    subprocess.run([
        "az", "quota", "create",
        "--resource-name", resource_name,
        "--scope", scope,
        "--limit-object", limit_object,
        "--no-wait", "yes",
        "--resource-type", resource_type,
        "--properties", "{'notes':'At least 3 A10 needed, critical to business. Our company specializes in building Foundation models for 3D generation, and after successfully building with A10s, we urgently need to test our algorithms with multiple A10s.'}",
        "--output", "table"
    ])

# Loop through each region and create a quota request
for region in us_regions + other_regions:
    create_quota_request(region)