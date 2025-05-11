import os
import re
import json
import yaml
import requests

token = os.environ["GITHUB_TOKEN"]
repo = os.environ["GITHUB_REPOSITORY"]
event_path = os.environ["GITHUB_EVENT_PATH"]

with open(event_path) as f:
    event_data = json.load(f)

# Determine comment body and response URL
if "comment" in event_data:
    body = event_data["comment"]["body"]
    post_url = event_data["issue"]["comments_url"]  # <- safer
elif "issue" in event_data:
    body = event_data["issue"].get("body", "")
    post_url = event_data["issue"]["comments_url"]
elif "pull_request" in event_data:
    body = event_data["pull_request"].get("body", "")
    post_url = event_data["pull_request"]["comments_url"]
else:
    exit(0)

# Load config
with open(".github/mention-config.yml") as f:
    config = yaml.safe_load(f)

inactive_users = set(u.lower() for u in config.get("inactive_users", []))

# Find mentions
mentioned = set(u.lower() for u in re.findall(r'@([a-zA-Z0-9_-]+)', body))

# Post message if an inactive user was mentioned
for user in mentioned:
    if user in inactive_users:
        message = f"**@{user}** — This person is no longer maintaining this repository."
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        r= requests.post(post_url, headers=headers, json={"body": message})
        if r.status_code >= 400:
            print(f"Error posting comment: {r.status_code} - {r.text}")
        else:
            print(f"Posted comment for @{user}")