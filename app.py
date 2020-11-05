from flask import Flask, request
import Recap.api as recap
import Shotgun.api as shotgun
import Email.api as email
import uuid
import threading

app = Flask(__name__)

# Use a dict to store our jobs in the demo. Recommend to store it in a database in a real environment.
localCache = {}


# Post uri from shotgun to website.
def do_shotgun_post_job(scene, file_ids):
    for file_id in file_ids:
        file_info = shotgun.GetFileDownloadUri(file_id)
        filename = str(file_info[0]).lower()
        uri = file_info[1]
        response = None
        while response is None or 'fault' in response:
            if filename.endswith('.xml'):
                response = recap.PostUriToScene(scene, [uri], 'survey')
            if filename.endswith('.jpg') or filename.endswith('.png'):
                response = recap.PostUriToScene(scene, [uri])
            print(response)
    print(recap.PostScene(scene))
    email.SendEmail(body=f'Scene {scene} has been created.')


# Accept job call from shotgun
@app.route('/shotgun/dorecap', methods=['POST', 'GET'])
def shotgun_post_job():
    global localCache
    data = request.form
    callback_id = uuid.uuid4()
    scene = recap.CreatePhotoScene('testscene', callback=callback_id)
    localCache[str(callback_id)] = [scene, 'testscene']
    file_ids = str(data['ids']).split(',')
    thread = threading.Thread(target=do_shotgun_post_job, args=(scene, file_ids))
    thread.start()
    return scene


# Query scene status manually
@app.route('/recap/<scene_name>', methods=['POST', 'GET'])
def query_scene(scene_name):
    return recap.QueryScene(scene_name)


# Download the scene manually.
@app.route('/recap/download/<scene_name>', methods=['GET'])
def download_scene(scene_name):
    return recap.DownloadPhotoScene(scene_name)


# Receive callback from Recap
@app.route('/recap/callback/<uuid>', methods=['GET'])
def recap_callback(uuid):
    global localCache
    print(request.args)
    scene = localCache[uuid][0]
    name = localCache[uuid][1]
    email.SendEmail(body=f'Scene {scene} has completed.')
    recap.DownloadPhotoScene(scene, filename=name)
    email.SendEmail(body=f'Scene {scene}, {name} download complete.')
    return ""
