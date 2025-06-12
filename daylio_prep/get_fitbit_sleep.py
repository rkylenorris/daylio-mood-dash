import fitbit
import datetime
from datetime import timedelta
import pandas as pd
from dotenv import load_dotenv
from fitbit import gather_keys_oauth2 as Oauth2
import os
import json


def get_fitbit_auth():
    load_dotenv()
    fitbit_tokens_path = "data\\fitbit_tokens.json"
    client_id = os.getenv('FITBIT_CLIENT_ID', 'your_client_id')
    client_secret = os.getenv('FITBIT_CLIENT_SECRET', 'your_client_secret')
    
    with open(fitbit_tokens_path) as f:
        token_data = json.load(f)
    
    authd_client = fitbit.Fitbit(
        client_id,
        client_secret,
        access_token=token_data['access_token'],
        refresh_token=token_data['refresh_token'],
        expires_at=token_data['expires_at'],
        refresh_cb=lambda t: json.dump(t, open(fitbit_tokens_path, "w"), indent=2)
    )
    
    return authd_client


def get_fitbit_sleep_data(authd_client = get_fitbit_auth(), days: int = 90):
    """
    Fetches Fitbit sleep data for the last 'days' days.
    
    :param authd_client: Authenticated Fitbit client
    :param days: Number of days to fetch sleep data for
    :return: List of sleep entries
    """
    start = datetime.date.today() - datetime.timedelta(days=days)
    end = datetime.date.today()
    
    response = authd_client.make_request(
        f"https://api.fitbit.com/1.2/user/-/sleep/date/{start}/{end}.json"
    )
    
    if isinstance(response, dict):
        return response.get("sleep", [])
    
    return []


def nap_or_full(duration_hours, start_time, end_time):
    sleep_type = "full"
    nap_hours = 3
    if (start_time.hour in range(8, 19, 1) and duration_hours <= nap_hours):
        sleep_type = "nap"
    elif start_time.date() == end_time.date() and start_time.hour in range(7, 19, 1) and duration_hours <= 6:
        sleep_type = "nap"
    elif start_time.date() == end_time.date() and duration_hours > nap_hours:
        sleep_type = "full"
    elif start_time.date() != end_time.date():
        sleep_type = "full"
    else:
        sleep_type = "nap"
    return sleep_type


def clean_sleep_data(sleep_entries=get_fitbit_sleep_data()):
    """
    Cleans and formats the sleep data entries.
    
    :param sleep_entries: List of sleep entries
    :return: List of cleaned sleep entries
    """
    
    cleaned_entries = []

    for entry in sleep_entries:
        # get duration and format it
        duration = entry.get('duration', 0)
        duration_td = datetime.timedelta(milliseconds=duration)
        formatted_time = str(duration_td)

        # Convert startTime and endTime to datetime objects
        start_time_obj = datetime.datetime.strptime(
            entry['startTime'], "%Y-%m-%dT%H:%M:%S.%f")
        end_time_obj = datetime.datetime.strptime(
            entry['endTime'], "%Y-%m-%dT%H:%M:%S.%f")
        
        # Format start and end times to readable strings
        start_time_readable = start_time_obj.strftime("%Y-%m-%d %H:%M")
        end_time_readable = end_time_obj.strftime("%Y-%m-%d %H:%M")
        
        # Calculate sleep type based on duration and start/end times
        sleep_type = nap_or_full(round(duration / 3600000), start_time_obj, end_time_obj)

        # Convert dateOfSleep to a date object
        sleep_date = datetime.datetime.strptime(
            entry['dateOfSleep'], '%Y-%m-%d').date()

        # Determine sleep log type
        sleep_log_type = entry.get('type', 'unknown')

        # Get summary data
        summary = entry.get('levels', {}).get('summary', {})

        # if log type is classic, get counts for asleep, awake, and restless manually because their count fields are not accurate
        # otherwise, set them to None
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
            
        # Get counts and minutes for different sleep levels    
        asleep_minutes = summary.get('asleep', {}).get('minutes', None)
        awake_minutes = summary.get('awake', {}).get('minutes', None)
        restless_minutes = summary.get('restless', {}).get('minutes', None)
        deep_sleep_count = summary.get('deep', {}).get('count', None)
        light_sleep_count = summary.get('light', {}).get('count', None)
        rem_sleep_count = summary.get('rem', {}).get('count', None)
        wake_count = summary.get('wake', {}).get('count', None)
        deep_sleep_minutes = summary.get('deep', {}).get('minutes', None)
        light_sleep_minutes = summary.get('light', {}).get('minutes', None)
        rem_sleep_minutes = summary.get('rem', {}).get('minutes', None)
        wake_minutes = summary.get('wake', {}).get('minutes', None)

        # Create a cleaned entry dictionary
        cleaned_entries.append({
            "date": sleep_date,
            "duration_milliseconds": duration,
            "duration_seconds": round(duration_td.total_seconds()),
            "duration_minutes": round(duration / 60000),  # Convert ms to minutes
            "duration_hours": round(duration / 3600000),  # Convert ms to hours
            "duration_hhmmss": formatted_time,
            "sleep_type": sleep_type,
            "start_time": start_time_obj,
            "start_time_ymdhm": start_time_readable,
            "end_time": end_time_obj,
            "end_time_ymdhm": end_time_readable,
            "efficiency": entry['efficiency'],
            "minutes_asleep": entry['minutesAsleep'],
            "minutes_awake": entry['minutesAwake'],
            "main_sleep": entry['isMainSleep'],
            "deep_sleep_count": deep_sleep_count,
            "deep_sleep_minutes": deep_sleep_minutes,
            "light_sleep_count": light_sleep_count,
            "light_sleep_minutes": light_sleep_minutes,
            "rem_sleep_count": rem_sleep_count,
            "rem_sleep_minutes": rem_sleep_minutes,
            "wake_count": wake_count,
            "wake_minutes": wake_minutes,
            "asleep_count": asleep_count,
            "asleep_minutes": asleep_minutes,
            "awake_count": awake_count,
            "awake_minutes": awake_minutes,
            "restless_count": restless_count,
            "restless_minutes": restless_minutes,
            "sleep_log_type": sleep_log_type,
        })

    # Convert the list of cleaned entries to a DataFrame and return it
    return pd.DataFrame(cleaned_entries)
