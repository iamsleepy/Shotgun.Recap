import requests
import os
from datetime import datetime, timedelta
import threading
import time


class ShotgunToken:
    access_code = None
    expire_time = None
    refresh_code = None
    lock = threading.Lock()


def GetFullUri(access_entry):
    host = os.getenv('SHOTGUN_HOST')
    if host is None:
        print("Missing SHOTGUN_HOST in your environment")
    return f'{host}/{access_entry}'


def GetShotgunToken():
    key = os.getenv('SHOTGUN_APPLICATION_KEY')
    script_name = os.getenv('SHOTGUN_APPLICATION_NAME')
    if key is None:
        print("Missing SHOTGUN_APPLICATION_KEY or SHOTGUN_APPLICATION_NAME in your environment!")
        return None
    ShotgunToken.lock.acquire()
    if ShotgunToken.expire_time is None or ShotgunToken.expire_time <= datetime.now():
        uri = GetFullUri('api/v1/auth/access_token')
        headers = {}
        body = {}
        if ShotgunToken.refresh_code is None:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'}
            body = {
                'client_id': script_name,
                'client_secret': key,
                'grant_type': 'client_credentials',
            }
        else:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'}
            body = {
                'refresh_token': ShotgunToken.refresh_code,
                'grant_type': 'refresh_token'
            }
        # Get token! We'll try 5 times
        retry = 0
        retry_limit = 5
        retry_interval = 1
        response = None
        refresh_time = datetime.now()
        while retry < retry_limit:
            response = requests.post(uri, headers=headers, data=body)
            if response.status_code == 200:
                break
            retry = retry + 1
            print(
                f'Status code:{response.status_code}. \nFailed to get item for {retry} times. Retry in {retry_interval} seconds.')
            if retry >= retry_limit:
                print(f"Failed to get authcode after {retry} attempts.")
                return None
            time.sleep(retry_interval)
            refresh_time = datetime.now()
        payload = response.json()
        ShotgunToken.access_code = payload['access_token']
        ShotgunToken.expire_time = refresh_time + timedelta(seconds=int(payload['expires_in']))
        ShotgunToken.refresh_code = payload['refresh_token']
    ShotgunToken.lock.release()
    return ShotgunToken


def GetFileDownloadUri(file_id, entity_type='Attachment'):
    uri = GetFullUri(f'api/v1/entity/{entity_type}/{file_id}')
    headers = {
                'Authorization': f'Bearer {GetShotgunToken().access_code}',
                'Range': '"<string>"'}
    response = requests.get(uri, headers=headers)
    json = response.json()
    this_file = json['data']['attributes']['this_file']
    return [this_file['name'], this_file['url']]
