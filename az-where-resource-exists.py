import subprocess
import json
import sys
import configparser

def get_quota_limits(subscription, resource_name):
    try:
        # Get the list of all regions
        regions_result = subprocess.run(['az', 'account', 'list-locations', '--output', 'json'], capture_output=True, text=True)
        regions = json.loads(regions_result.stdout)

        non_zero_regions = {}
        zero_regions = []
        error_regions = []

        print(f"Checking quota limits for {resource_name}")
        total_regions = len(regions)
        for index, region in enumerate(regions):
            region_name = region['name']
            scope = f"/subscriptions/{subscription}/providers/Microsoft.Compute/locations/{region_name}"
            progress_percentage = (index + 1) / total_regions * 100
            print(f"Progress: {progress_percentage:.1f}% - Querying {region_name}".ljust(80), end='\r')

            # Get the quota limits for the resource in the region
            quota_result = subprocess.run(['az', 'quota', 'show', '--scope', scope, '--resource-name', resource_name, '--query', 'properties.limit.value'], capture_output=True, text=True)
                
            if quota_result.returncode == 0:
                try:
                    quota_limit = int(quota_result.stdout.strip())
                    if quota_limit > 0:
                        non_zero_regions[region_name] = quota_limit
                        print(f"Progress: {progress_percentage:.1f}% - Querying {region_name} - FOUND {quota_limit}".ljust(80), end='\r')
                    else:
                        zero_regions.append(region_name)
                except ValueError:
                    print(f"Failed to convert quota limit to int for {resource_name} in {region_name}")
                    error_regions.append(region_name)
            else:
                error_regions.append(region_name)

        # Print non-zero regions in a table format
        if non_zero_regions:
            print(f"\n{'Region':<20}|{'Quota Limit':<10}")
            print("-" * 30)
            for region, limit in non_zero_regions.items():
                print(f"{region:<20}|{limit:<10}")
        else:
            print(f"No regions with non-zero quota limit for {resource_name}")

        # Print zero and error regions
        print(f"\nRegions with zero quota limit for {resource_name}:\n {zero_regions}")
        print(f"\nRegions which returned error:\n {error_regions}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return None

def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: python az-where-resource-exists.py <resource_name> [subscription_id]")
        sys.exit(1)

    resource_name = sys.argv[1]

    config = configparser.ConfigParser()
    config.read('.env')
    subscription_id = sys.argv[2] if len(sys.argv) == 3 else config['DEFAULT']['SUBSCRIPTION_ID'] 

    get_quota_limits(subscription_id, resource_name)
    # print(json.dumps(quota_limits, indent=2))

if __name__ == "__main__":
    main()