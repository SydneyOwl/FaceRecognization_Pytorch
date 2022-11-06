from crypt import methods
import time
from typing import List
import uuid
from flask import request, jsonify, send_from_directory

from utils.jwtutil import jwtDecodeDefault
from utils.picupload import upload_byte_to_cos
from . import offline_video
import os
from werkzeug.utils import secure_filename
from app import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, PROCESSED_FOLDER
from database.tool.video_sqltool import *
import cv2
# video_keys = shared_val.video_keys
upload_dir = os.path.join(os.getcwd(), UPLOAD_FOLDER)
done_dir = os.path.join(os.getcwd(), PROCESSED_FOLDER)
@offline_video.route("/getMyVideo",methods=['POST'])
def getMyVideo():
    userid = jwtDecodeDefault(request).get("data")["id"]
    videoLsts= getVideoListByUID(userid)
    owl = []
    for v in videoLsts:
        owl.append({
                "thumb":v.thumb,
                "original_name":v.original_name,
                "is_processed":v.processed,
                "id":v.id,
                "time":v.time
            })
    return jsonify({
        "status":200,
        "data":owl
    })
@offline_video.route("/downloadVideo", methods=['GET'])
def getVideo():
    try:
        vkey = request.args.get("videoKey")
        # print("vk"+request.args.get("videoKey"))
        viInfo = getVideoInfo(vkey)
        if viInfo == None:
            return jsonify({
                "status": 404,
                "info": "ERR_FILE_NOT_FOUND"
            })
        if not viInfo.processed:
            return jsonify({
                "status": 403,
                "info": "ERR_FILE_NOT_PROCESSED"
            })
        _, filename = os.path.split(viInfo.dir)
        return send_from_directory(path='processed-'+filename, directory=done_dir, as_attachment=True)
    except Exception as e:
        print(repr(e))
        return jsonify({
            "status": 500
        })


@offline_video.route("/sendVideo", methods=['POST'])
def saveVideo():
    video = request.files['file']
    userid = jwtDecodeDefault(request).get("data")["id"]
    if not video:
        return jsonify({
            "status": 400,
            "info": "ERR_VIDEO_IS_NIL"
        })
    """Video streaming route. Put this in the src attribute of an img tag."""
    ran_key = str(uuid.uuid4())
    fileName = ran_key + secure_filename(video.filename)
    if '.' in fileName and fileName.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS:
        targetDirectory = os.path.join(upload_dir, fileName)
        video.save(targetDirectory)
    else:
        return jsonify({
            "status": 401,
            "info": "ERR_INVALID_VIDEO_FORMAT"
        })
    cap = cv2.VideoCapture(targetDirectory)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            break
    # path = os.path.join(os.getcwd(),"video_cache/tmp.jpg")
    # cv2.imwrite(path,frame)
    res,frame = cv2.imencode(".jpg",frame)
    url = ""
    if res:
        url = upload_byte_to_cos(frame.tobytes(),str(uuid.uuid4()),"frame_thumb")
    storageVideo(ran_key, userid, secure_filename(video.filename), targetDirectory,url)
    # shared_val.video_keys[ran_key] = {
    #     "dir": targetDirectory,
    #     "originalFilename": fileName,
    #     "isProcessed": False
    # }
    return jsonify({
        "status": 200,
        "key": ran_key,
        "timestamp": int(time.time())
    })
