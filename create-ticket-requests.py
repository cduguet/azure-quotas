import subprocess
import json
import configparser

# List of US regions
us_regions = ["eastus", "eastus2", "southcentralus", "westus2", "westus3", "centralus", "northcentralus", "westus", "westcentralus"]

# Azure subscription ID
# Read the subscription ID from the .secret file
config = configparser.ConfigParser()
config.read('.env')

subscription_id = config['DEFAULT']['SUBSCRIPTION_ID']

# Common details for the support request
service = "06bfd9d3-516b-d5c6-5802-169c800dec89"  # Service and subscription limits (quotas)
problem_classification = "e12e3d1d-7fa0-af33-c6d0-3c50df9658a3"  # Compute-VM (cores-vCPUs) subscription limit increases
problem_classification_name = f"/providers/Microsoft.Support/services/{service}/problemClassifications/{problem_classification}"

severity = "moderate"
contact_first_name = config['DEFAULT']['CONTACT_FIRST_NAME']
contact_last_name = config['DEFAULT']['CONTACT_LAST_NAME']
contact_email = config['DEFAULT']['CONTACT_EMAIL']
contact_country = config['DEFAULT']['CONTACT_COUNTRY']
contact_language = config['DEFAULT']['CONTACT_LANGUAGE']
contact_timezone = config['DEFAULT']['CONTACT_TIMEZONE']
ticket_title = "A100 needed, critical to business"
ticket_description = "Our company specializes in building Foundation models for 3D generation, and we are hitting the limits of what we can build with the A10, so we urgently need to develop our algorithms with a single A100."

quota_change_version = "1.0"
new_limit_value = 24

# Function to create a support ticket
def create_support_ticket(region):
  ticket_name = f"A100-{region}"
  quota_change_requests = json.dumps([{
    'region': region,
    'payload': json.dumps({
      "VMFamily": "NC A100 v4 Series",
      "NewLimit": new_limit_value,
      "Type": "Regional"
    })
  }])

  command = [
    "az", "support", "in-subscription", "tickets", "create",
    "--ticket-name", ticket_name,
    "--title", ticket_title,
    "--description", ticket_description,
    "--problem-classification", problem_classification_name,
    "--severity", severity,
    "--contact-first-name", contact_first_name,
    "--contact-last-name", contact_last_name,
    "--contact-method", "email",
    "--contact-email", contact_email,
    "--contact-country", contact_country,
    "--contact-language", contact_language,
    "--contact-timezone", contact_timezone,
    "--advanced-diagnostic-consent", "Yes",
    "--quota-change-version", quota_change_version,
    "--quota-change-requests", quota_change_requests
  ]

  subprocess.run(command, check=True)

# Loop through each region and create a support ticket
for region in us_regions:
  print(f"Creating support ticket for US region: {region}")
  create_support_ticket(region)
