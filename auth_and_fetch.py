import os, sys, webbrowser, urllib.parse, requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

CID = os.getenv("STRAVA_CLIENT_ID")
SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT = os.getenv("STRAVA_REDIRECT_URI")

if not all([CID, SECRET, REDIRECT]):
    print("Missing STRAVA_CLIENT_ID/STRAVA_CLIENT_SECRET/STRAVA_REDIRECT_URI in .env")
    sys.exit(1)

# Strava OAuth scopes
scopes = ["read", "activity:read_all"]

# Step 1: Generate authorization URL
auth_url = (
    "https://www.strava.com/oauth/authorize?"
    + urllib.parse.urlencode({
        "client_id": CID,
        "redirect_uri": REDIRECT,
        "response_type": "code",
        "scope": ",".join(scopes),
        "approval_prompt": "auto"
      })
)

print("Open this URL to authorize:\n", auth_url)

try:
    webbrowser.open(auth_url)
except Exception:
    pass

# Step 2: Get code from user
code = input("\nPaste the 'code' from your redirected URL: ").strip()

# Step 3: Exchange code for tokens
r = requests.post(
    "https://www.strava.com/oauth/token",
    data={
        "client_id": CID,
        "client_secret": SECRET,
        "code": code,
        "grant_type": "authorization_code"
    },
    timeout=30
)
r.raise_for_status()
tok = r.json()
access = tok["access_token"]

# Step 4: Fetch athlete profile
print("\nFetching athlete profile...")
me = requests.get(
    "https://www.strava.com/api/v3/athlete",
    headers={"Authorization": f"Bearer {access}"},
    timeout=30
).json()
print("Athlete:", me.get("username") or me.get("id"))

# Step 5: Fetch most recent activity
print("\nFetching most recent activity...")
acts = requests.get(
    "https://www.strava.com/api/v3/athlete/activities",
    headers={"Authorization": f"Bearer {access}"},
    params={"per_page": 1, "page": 1},
    timeout=30
).json()

if acts:
    a = acts[0]
    print(f"- {a.get('name')} | distance: {a.get('distance')} m | moving_time: {a.get('moving_time')} s")
else:
    print("No recent activities found.")
