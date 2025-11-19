import os

# Google OAuth Configuration

GOOGLE_CLIENT_SECRETS_FILE = "credentials.json"

# The scopes allow us to add events to user's calendar
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# for local environment

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
