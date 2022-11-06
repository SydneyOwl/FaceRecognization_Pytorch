from sqlalchemy import desc
from database.db.dbconn import session
from database.orm.Video import Video
import datetime
def storageVideo(id,opid,original_name,dir,thumb):
    session.add(Video(
        id,
        opid,
        original_name,
        dir,
        0,
        thumb,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    session.commit()
def updateVideoStatus(id):
    session.query(Video).filter(Video.id==id).update({"processed":1})
    session.commit()
def getVideoStatus(id):
    video = session.query(Video).filter(Video.id==id).first()
    return video.processed
def getVideoInfo(id):
    video = session.query(Video).filter(Video.id==id).first()
    return video
def getVideoListByUID(id):
    return session.query(Video).filter(Video.opid==id).order_by(desc("time")).all()