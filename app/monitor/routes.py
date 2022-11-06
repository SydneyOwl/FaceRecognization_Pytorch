from flask import jsonify
from . import monitor
import shared_val


@monitor.route('/startPush', methods=["POST"])
def goStream():
    shared_val._is_cam_available = True
    return jsonify({"status": "200"})


@monitor.route('/endPush', methods=["POST"])
def noStream():  # clear
    shared_val._is_cam_available = False
    print("Cam disconnected!")
    return jsonify({"status": "200"})


@monitor.route("/getAllFace", methods=["POST"])
def getStoragedFace():
    return jsonify({
        "status": 200, "face": shared_val.tmp_face
    })
