from flask import Blueprint

offline_video = Blueprint('offline_video', __name__)

from . import routes,events