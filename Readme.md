# Using Forge Reality Capture with asset files in Shotgun

This sample will use the attachment files of an asset in Shotgun with Forge Reality Capture service.

Forge Reality Capture API leverages our latest desktop and cloud solution built for UAV and drone processes, ReCap Photo. You can add geo-based metadata by setting Ground Control Points (GCPs), selecting specific geographic coordinate systems, and tagging images with GPS information. The integration of this geo data results in accurate textured meshes, point clouds, and orthophotos. A reconstruction report details the level of accuracy. It also could use digital photos from hand-held cameras to produce photorealistic 3D models. Example use cases include the capture of objects, building facades, and interiors.

The sample is written with Python 3 with Flask. I also used requests, you'll need to install these libraries manually if you haven't installed them yet.

You'll need both Forge account and Shotgun account to run the sample.

Before running the sample, you'll need setup following system enivironment variables:

	FLASK_APP=app.py
	FLASK_ENV=development
	FLASK_RUN_HOST 

These are settings for running flask. The flask run host should be your wan/lan ip address, e.g. 10.0.0.4.


	EMAIL_SERVER
	EMAIL_PASSWORD
	EMAIL_USER
	EMAIL_RECEIVER

The user/password is the login/password for the email server. Email server could be any smtp server, I've tested with outlook server and it is working fine. The default port for smtp server is 587, if your smtp server uses a different port, please modify it in the source code (email/api.py). Email receiver is the default receiver for the notification email.

	FORGE_CLIENT_SECRET
	FORGE_CLIENT_TOKEN

You'll need to put your forge app token/secret here.

	RECAP_CALLBACK_URL
	RECAP_FILE_STORAGE

These are Reality Capture settings. The first is url for receving the callback, it should be your public domain name or ip address with **/recap/callback** in the end (e.g. http://myhost/recap/callback). The recap file storage setting is a local path for downloading generated recap files (e.g. f:\recapstorage).

	SHOTGUN_ACTION_SECRET
	SHOTGUN_APPLICATION_KEY
	SHOTGUN_APPLICATION_NAME
	SHOTGUN_HOST

These are shotgun settings, the secret, key and name are the one you've created in shotgun. Please notice that, the application name must match the name you've created in shotgun, otherwise shotgun will return a 400 bad reqeust. The host should be your shotgun server address (e.g. https://mystudio.shotgunstudio.com)
