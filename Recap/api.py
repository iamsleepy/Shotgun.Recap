from typing import Dict

import Authentication.api as auth
import requests
import os

RecapPhotoSceneLocation = 'https://developer.api.autodesk.com/photo-to-3d/v1/photoscene'
RecapFileLocation = 'https://developer.api.autodesk.com/photo-to-3d/v1/file'

def getUrlFormHeader():
    token = auth.GetAppToken()
    return {
        'Authorization': f'Bearer {token.access_code}',
        'Content-type': 'application/x-www-form-urlencoded'
    }


# For uploading scene directly
def getMultiFormHeader():
    token = auth.GetAppToken()
    return {
        'Authorization': f'Bearer {token.access_code}',
        'Content-type': 'multipart/form-data'
    }


# Create a photo scene on recap
def CreatePhotoScene(name, scene_type='aerial', gps_type='regular', callback=''):
    global RecapPhotoSceneLocation
    callback_base = os.getenv('RECAP_CALLBACK_URL')
    if callback_base is None:
        print("Error: Missing RECAP_CALLBACK_URL in your environment")
        return None
    data = {
        'scenename': name,
        'format': 'rcm,fbx',
        'scenetype': scene_type,
        'gpstype': gps_type,
        'callback': f'{callback_base}/{callback}'
    }
    response = requests.post(RecapPhotoSceneLocation, data=data, headers=getUrlFormHeader())
    if response.status_code != 200:
        print(response)
        return None
    data = response.json()
    return data['Photoscene']['photosceneid']


# Download the photo scene after the finished callback
def DownloadPhotoScene(name, filename, format='fbx'):
    storage_location = os.getenv('RECAP_FILE_STORAGE')
    if storage_location is None:
        print("Error: Missing RECAP_FILE_STORAGE in your environment, can't save file.")
        return None
    local_filename = f'{storage_location}\\{filename}.{name}.{format}.zip'
    url = f'{RecapPhotoSceneLocation}/{name}?format={format}'
    response = requests.get(url, headers=getUrlFormHeader())
    data = response.json()
    with requests.get(data['Photoscene']['scenelink'], stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return local_filename


# Post local file to recap directly
def PostImageFileToScene(scene_name, files):
    global RecapFileLocation
    headers = getUrlFormHeader()
    data = {
        'photosceneid': scene_name,
        'type': 'image',
        'file[]': files
    }


# Post uri to recap directly
def PostUriToScene(scene_name, uris, uri_type='image') -> Dict[str, str]:
    global RecapFileLocation
    headers = getUrlFormHeader()
    data = {
        'photosceneid': scene_name,
        'type': uri_type,
    }
    i = 0
    for uri in uris:
        data[f'file[{i}]'] = uri
        i += 1
    r = requests.post(RecapFileLocation, headers=headers, data=data)
    return r.json()


def PostScene(scene_name):
    global RecapPhotoSceneLocation
    uri = f'{RecapPhotoSceneLocation}/{scene_name}'
    headers = getUrlFormHeader()
    r = requests.post(uri, headers=headers)
    return r.content


def QueryScene(scene_name):
    global RecapPhotoSceneLocation
    uri = f'{RecapPhotoSceneLocation}/{scene_name}/progress'
    headers = getUrlFormHeader()
    r = requests.get(uri, headers=headers)
    return r.content
