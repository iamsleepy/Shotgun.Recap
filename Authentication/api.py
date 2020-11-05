import requests
import os
import sys
from datetime import datetime, timedelta
import threading
import time


class ForgeToken:
    access_code = None
    expire_time = None
    lock = threading.Lock()


# Get our forge application token
def GetAppToken() -> ForgeToken:
    # We only wants one working thread on token at the same time.
    token = os.getenv('FORGE_CLIENT_TOKEN')
    secret = os.getenv('FORGE_CLIENT_SECRET')
    if token is None or secret is None:
        print("Error: Missing FORGE_CLIENT_TOKEN or FORGE_CLIENT_SECRET in system environment. Terminate now.")
        sys.exit(0)

    ForgeToken.lock.acquire()

    # Do we need to refresh or initialize token?
    if ForgeToken.expire_time is None or ForgeToken.expire_time <= datetime.now():
        uri = 'https://developer.api.autodesk.com/authentication/v1/authenticate'
        # We need data:read,data:write for recap
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'client_id': token,
            'client_secret': secret,
            'grant_type': 'client_credentials',
            'scope': 'data:read data:write code:all'
        }

        # Get token! We'll try 5 times
        retry = 0
        retry_limit = 5
        retry_interval = 1
        response = None
        refresh_time = datetime.now()
        while retry < retry_limit:
            response = requests.post(uri, headers)
            if response.status_code == 200:
                break
            retry = retry + 1
            print(f'Status code:{response.status_code}. \nFailed to get item for {retry} times. Retry in {retry_interval} seconds.')
            if retry >= retry_limit:
                print(f"Failed to get authcode after {retry} attempts.")
                return None
            time.sleep(retry_interval)
            refresh_time = datetime.now()
        payload = response.json()
        ForgeToken.access_code = payload['access_token']
        ForgeToken.expire_time = refresh_time + timedelta(seconds=int(payload['expires_in']))
    ForgeToken.lock.release()
    return ForgeToken
