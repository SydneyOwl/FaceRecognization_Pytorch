from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

socketio = SocketIO()

UPLOAD_FOLDER = "video_cache/original"
PROCESSED_FOLDER = "video_cache/processed"
ALLOWED_EXTENSIONS = ['mp4', 'avi']
emoLabel = ['amaze', 'fear', 'disgust', 'happy', 'sad', 'anger', "neutral"]
MONITOR_STREAM = "rtmp://YOUR_IP/live/test"
PROCESSED_STREAM = "rtmp://YOUR_IP/live/ferStream"
def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = "rfDhi3948/"
    app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 限制大小64mb
    from .monitor import monitor as monitor_blueprint
    from .offline_video import offline_video as offline_video_blueprint
    from .auth import auth
    app.register_blueprint(monitor_blueprint)
    app.register_blueprint(offline_video_blueprint)
    app.register_blueprint(auth)
    CORS(app, resources=r'/*',supports_credentials=True)
    socketio.init_app(app,cors_allowed_origins='*', async_mode='threading')
    return app