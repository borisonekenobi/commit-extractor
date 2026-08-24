import requests
import json
import time

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
GHE_DOMAIN = "" # TODO
USERNAME = "" # TODO
TOKEN = "" # TODO
OUTPUT_FILE = "all_contributions.txt"
# ────────────────────────────────────────────────────────────────────────────

url = f"https://{GHE_DOMAIN}/api/graphql"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. First, we find out which years you have been active on this server
years_query = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionYears
    }
  }
}
"""

try:
    response = requests.post(url, json={"query": years_query, "variables": {"username": USERNAME}}, headers=headers)
    active_years = response.json()['data']['user']['contributionsCollection']['contributionYears']
    print(f"Detected activity in years: {active_years}")
except Exception as e:
    print(f"Error querying active years: {e}")
    exit(1)

# 2. Loop through each year and extract the exact daily contribution counts
calendar_query = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

all_dates = []

for year in active_years:
    print(f"Fetching contribution calendar for {year}...")
    variables = {
        "username": USERNAME,
        "from": f"{year}-01-01T00:00:00Z",
        "to": f"{year}-12-31T23:59:59Z"
    }

    res = requests.post(url, json={"query": calendar_query, "variables": variables}, headers=headers)
    if res.status_code != 200:
        print(f"Failed to fetch data for {year}: {res.text}")
        continue

    try:
        weeks = res.json()['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        for week in weeks:
            for day in week['contributionDays']:
                count = day['contributionCount']
                # If you had activity on this day, record it
                if count > 0:
                    for _ in range(count):
                        all_dates.append(day['date'])
    except Exception as e:
        print(f"Parsing error for year {year}: {e}")

# Save the final list to a text file
with open(OUTPUT_FILE, "w") as f:
    for date in all_dates:
        f.write(f"{date}T12:00:00Z\n")  # Appending mid-day timestamp for safe commit spacing

print(f"\nSuccess! Found a grand total of {len(all_dates)} contributions.")
print(f"Saved exact timeline to {OUTPUT_FILE}")
