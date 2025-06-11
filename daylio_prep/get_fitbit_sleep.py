import fitbit
import datetime
from datetime import timedelta
import pandas as pd
from dotenv import load_dotenv
from fitbit import gather_keys_oauth2 as Oauth2
import os
import json
import requests

load_dotenv()

fitbit_tokens_path = "data\\fitbit_tokens.json"

CLIENT_ID = os.getenv('FITBIT_CLIENT_ID', 'your_client_id')
CLIENT_SECRET = os.getenv('FITBIT_CLIENT_SECRET', 'your_client_secret')
OAUTHLIB_INSECURE_TRANSPORT = os.getenv('OAUTHLIB_INSECURE_TRANSPORT', '1')
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = OAUTHLIB_INSECURE_TRANSPORT

# Load saved token
with open(fitbit_tokens_path) as f:
    token_data = json.load(f)

# Create Fitbit client with token refresh support
authd_client = fitbit.Fitbit(
    CLIENT_ID,
    CLIENT_SECRET,
    access_token=token_data['access_token'],
    refresh_token=token_data['refresh_token'],
    expires_at=token_data['expires_at'],
    refresh_cb=lambda t: json.dump(t, open(fitbit_tokens_path, "w"), indent=2)
)

start = datetime.date.today() - datetime.timedelta(days=90)
end = datetime.date.today()

response = authd_client.make_request(
    f"https://api.fitbit.com/1.2/user/-/sleep/date/{start}/{end}.json"
)

entries = []
if isinstance(response, dict):
    # Print all sleep entries
    for entry in response["sleep"]:
        print(entry["dateOfSleep"], entry["minutesAsleep"], "minutes asleep")
        entries.append(entry)

with open("data\\fitbit_sleep_data.json", "w") as f:
    json.dump(entries, f, indent=4)

cleaned_entries = []


def nap_or_full(duration_hours, start_time, end_time):
    sleep_type = "full"
    nap_hours = 3
    if (start_time.hour in range(8, 19, 1) and duration_hours <= nap_hours):
        sleep_type = "nap"
    elif start_time.date() == end_time.date() and duration_hours <= nap_hours:
        sleep_type = "nap"
    elif start_time.date() == end_time.date() and duration_hours > nap_hours:
        sleep_type = "full"
    elif start_time.date() != end_time.date() and duration_hours > nap_hours:
        sleep_type = "full"
    elif start_time.date() != end_time.date() and duration_hours <= nap_hours:
        sleep_type = "nap"
    else:
        sleep_type = "full"
    return sleep_type


for entry in entries:
    duration = entry.get('duration', 0)

    duration_td = datetime.timedelta(milliseconds=duration)
    formatted_time = str(duration_td)

    start_time_obj = datetime.datetime.strptime(
        entry['startTime'], "%Y-%m-%dT%H:%M:%S.%f")
    end_time_obj = datetime.datetime.strptime(
        entry['endTime'], "%Y-%m-%dT%H:%M:%S.%f")
    
    sleep_type = nap_or_full(round(duration / 3600000), start_time_obj, end_time_obj)
    
    if start_time_obj.date() < end_time_obj.date() and sleep_type == "full":
        sleep_date = start_time_obj.date()
    elif start_time_obj.date() == end_time_obj.date() and sleep_type == "full" and start_time_obj.hour in range(0, 8, 1):
        sleep_date = start_time_obj.date() - timedelta(days=1)
    elif sleep_type == "nap":
        sleep_date = start_time_obj.date()
   

    start_time_readable = start_time_obj.strftime("%Y-%m-%d %H:%M")
    end_time_readable = end_time_obj.strftime("%Y-%m-%d %H:%M")

    sleep_date = datetime.datetime.strptime(
        entry['dateOfSleep'], '%Y-%m-%d').date()

    sleep_log_type = entry.get('type', 'unknown')

    summary = entry.get('levels', {}).get('summary', {})

    if sleep_log_type == "classic":
        asleep_count = sum(1 for entry in entry.get("levels", {}).get(
            "data", []) if entry["level"] == "asleep")
        awake_count = sum(1 for entry in entry.get("levels", {}).get(
            "data", []) if entry["level"] == "awake")
        restless_count = sum(1 for entry in entry.get("levels", {}).get(
            "data", []) if entry["level"] == "restless")
    else:
        asleep_count = None
        awake_count = None
        restless_count = None

    

    cleaned_entries.append({
        "date": sleep_date,
        "date_ymd": sleep_date.strftime('%Y-%m-%d'),
        "duration_milliseconds": duration,
        # Convert ms to seconds
        "duration_seconds": round(duration_td.total_seconds()),
        "duration_minutes": round(duration / 60000),  # Convert ms to minutes
        "duration_hours": round(duration / 3600000),  # Convert ms to hours
        "duration_hhmmss": formatted_time,
        "sleep_type": sleep_type,
        "night_of_sleep": sleep_date if sleep_type == "full" else None,
        "day_of_nap": sleep_date if sleep_type == "nap" else None,
        "start_time": start_time_obj,
        "start_time_ymdhm": start_time_readable,
        "end_time": end_time_obj,
        "end_time_ymdhm": end_time_readable,
        "efficiency": entry['efficiency'],
        "minutes_asleep": entry['minutesAsleep'],
        "minutes_awake": entry['minutesAwake'],
        "main_sleep": entry['isMainSleep'],
        "deep_sleep_count": summary.get('deep', {}).get('count', None),
        "deep_sleep_minutes": summary.get('deep', {}).get('minutes', None),
        "light_sleep_count": summary.get('light', {}).get('count', None),
        "light_sleep_minutes": summary.get('light', {}).get('minutes', None),
        "rem_sleep_count": summary.get('rem', {}).get('count', None),
        "rem_sleep_minutes": summary.get('rem', {}).get('minutes', None),
        "wake_count": summary.get('wake', {}).get('count', None),
        "wake_minutes": summary.get('wake', {}).get('minutes', None),
        "asleep_count": asleep_count,
        "asleep_minutes": summary.get('asleep', {}).get('minutes', None),
        "awake_count": awake_count,
        "awake_minutes": summary.get('awake', {}).get('minutes', None),
        "restless_count": restless_count,
        "restless_minutes": summary.get('restless', {}).get('minutes', None),
        "sleep_log_type": sleep_log_type,
    })

sleep_df = pd.DataFrame(cleaned_entries)
# Save the DataFrame to a CSV file
sleep_df.to_csv("data\\fitbit_sleep_data.csv", index=False)
# Print the DataFrame
print(sleep_df.head())
