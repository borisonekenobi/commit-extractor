import requests

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
GHE_DOMAIN = "" # TODO
USERNAME = "" # TODO
TOKEN = "" # TODO
# ────────────────────────────────────────────────────────────────────────────

url = f"https://{GHE_DOMAIN}/api/graphql"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Fetch the target years again to loop through them precisely
years_query = "query($u:String!){user(login:$u){contributionsCollection{contributionYears}}}"
res_years = requests.post(url, json={"query": years_query, "variables": {"u": USERNAME}}, headers=headers)
active_years = res_years.json()['data']['user']['contributionsCollection']['contributionYears']

# 2. Query the exact totalContributions summary cache integer per year
server_total_sum = 0
summary_query = """
query($u: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $u) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
      }
    }
  }
}
"""

print("Checking server side metrics...")
for year in active_years:
    variables = {"u": USERNAME, "from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"}
    res = requests.post(url, json={"query": summary_query, "variables": variables}, headers=headers)
    year_total = res.json()['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
    print(f"  • Server confirms {year}: {year_total} contributions")
    server_total_sum += year_total

print(f"\n==============================================")
print(f"🔒 SERVER AUDIT BALANCE: {server_total_sum}")
print(f"==============================================")
