from utils.videoutil import processVideo
from .. import socketio,emoLabel
from flask_socketio import emit
import shared_val
from database.tool.video_sqltool import getVideoInfo, updateVideoStatus
@socketio.on('message', namespace='/wss/rtVideoProcess')
def realVP(message):
    vpr_key = message
    try:
        videoInfo = getVideoInfo(vpr_key)
        if videoInfo==None:
            emit('data', {
                'type': 'videoFrame',
                "status": 404,
                "info": "ERR_FILE_NOT_FOUND"
            })
            return
        if videoInfo.processed:
            emit('data', {
                'type': 'videoFrame',
                "status": 402,
                "info": "ERR_FILE_ALREADY_PROCESSED"
            })
            return
        
        targetDirectory = videoInfo.dir
        updateVideoStatus(vpr_key)
        for i in processVideo(targetDirectory):
            emit('data', {
                'type': 'videoFrame',
                'status': 200,
                'img': i[0],
                'processPercent': i[1],
                'faceCountInThisFrame': i[2],
                'emoInfoPerFrame': dict(zip(emoLabel, i[3])),
                "emoInfoTotal": dict(zip(emoLabel, i[4])),
                "width": i[5],
                "height": i[6]
            })
        emit('data', {
            'type': 'videoFrame',
            'status': 201
        })
    except KeyError:
        emit('data', {
            'type': 'videoFrame',
            'status': 404,
            'ErrorMsg': "ERR_NO_SUCH_FILE"
        })
    except Exception as e:
        print(repr(e))
        emit('data', {
            'type': 'videoFrame',
            'status': 500,
            'ErrorMsg': "ERR_ENCOUNTERED_UNKNOWN_STATUS"
        })