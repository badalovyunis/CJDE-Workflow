import argparse
import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def deploy_to_splunk(url, token, rule_name, spl_query, actions):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Rule var mı yoxla
    check_url = f"{url}/servicesNS/admin/search/saved/searches/{rule_name}"
    response = requests.get(check_url, headers=headers, verify=False)
    rule_exists = response.status_code == 200

    # Rule data
    data = {
        "name": rule_name,
        "search": spl_query,
        "cron_schedule": "*/5 * * * *",
        "is_scheduled": "1",
        "alert_type": "number of events",
        "alert_comparator": "greater than",
        "alert_threshold": "0",
        "alert.severity": "3",
        "actions": actions
    }

    if rule_exists:
        # Update et
        post_url = f"{url}/servicesNS/admin/search/saved/searches/{rule_name}"
        del data["name"]
    else:
        # Yeni yarat
        post_url = f"{url}/servicesNS/admin/search/saved/searches"

    response = requests.post(post_url, headers=headers, data=data, verify=False)

    if response.status_code in [200, 201]:
        print(f"✓ Rule '{rule_name}' uğurla deploy edildi!")
        return True
    else:
        print(f"✗ Xəta: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--rule", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--actions", default="log")
    args = parser.parse_args()

    success = deploy_to_splunk(
        args.url, args.token, args.rule, args.query, args.actions
    )
    sys.exit(0 if success else 1)
