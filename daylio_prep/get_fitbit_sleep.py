import fitbit
import datetime
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

with open("data/fitbit_sleep_data.json", "w") as f:
    json.dump(entries, f, indent=2)
 
cleaned_entries = []   
for entry in entries:
    duration = entry.get('duration', 0)
    
    duration_td = datetime.timedelta(milliseconds=duration)
    formatted_time = str(duration_td)
    
    start_time_obj = datetime.datetime.strptime(entry['startTime'], "%Y-%m-%dT%H:%M:%S.%f")
    end_time_obj = datetime.datetime.strptime(entry['endTime'], "%Y-%m-%dT%H:%M:%S.%f")
    
    start_time_readable = start_time_obj.strftime("%Y-%m-%d %H:%M")
    end_time_readable = end_time_obj.strftime("%Y-%m-%d %H:%M")
    
    cleaned_entries.append({
        "date": entry['dateOfSleep'],
        "date_object": datetime.datetime.strptime(entry['dateOfSleep'], '%Y-%m-%d').date(),
        "duration_milliseconds": duration,
        "duration_seconds": duration_td.total_seconds,  # Convert ms to seconds
        "duration_minutes": duration// 60000,  # Convert ms to minutes
        "duration_hours": duration // 3600000,  # Convert ms to hours
        "duration_hhmmss": formatted_time,
        "start_time": start_time_obj,
        "start_time_ymdhm": start_time_readable,
        "end_time": end_time_obj,
        "end_time_ymdhm": end_time_readable,
        "efficiency": entry['efficiency'],
        "minutes_asleep": entry['minutesAsleep'],
        "minutes_awake": entry['minutesAwake'],
        "main_sleep": entry['isMainSleep'],
        "deep_sleep_count": entry['levels']['summary']['deep']['count'],
        "deep_sleep_minutes": entry['levels']['summary']['deep']['minutes'],
        "light_sleep_count": entry['levels']['summary']['light']['count'],
        "light_sleep_minutes": entry['levels']['summary']['light']['minutes'],
        "rem_sleep_count": entry['levels']['summary']['rem']['count'],
        "rem_sleep_minutes": entry['levels']['summary']['rem']['minutes'],
        "wake_count": entry['levels']['summary']['wake']['count'],
        "wake_minutes": entry['levels']['summary']['wake']['minutes'],
    })