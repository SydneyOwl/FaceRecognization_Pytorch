import datetime
from flask import request, jsonify
from . import auth
import jwt
from utils.jwtutil import jwtdecode
from database.db.dbconn import session
from database.orm.Operator import Operator
from config import jwt_cfg
key1 = jwt_cfg["key"]


@auth.before_request  # 执行所有装饰器都要执行当前装饰器(简洁版实现同样功能)
def login_required():
    if request.path in ['/login',"/startPush","/endPush"]:  # 如果登录的路由是注册和登录就返会none
        return None
    raw = request.headers.get(
        'auth-token')
    if raw == None:  # 没有登录就自动跳转到登录页面去
        return jsonify({
            "status": 300,
            "info": "Unauthorized"
        })
    try:
        jwtdecode(raw,key1)
    except jwt.ExpiredSignatureError:
        return jsonify({
            "status": 405,
            "info": "expired"
        })
    except Exception as e:
        print(repr(e))
        return jsonify({
            "status": 500,
            "info": "InternalServerErrorr"
        })
    # return jsonify({
    #     "raw": jwt_decode
    # })
    return None


@auth.route("/login", methods=['POST'])
def login():
    raw = request.get_json()
    user = session.query(Operator).filter_by(
        name=raw['username'], password=raw['password']).first()
    if user is None:
        return jsonify({
            "status": 405,
            "info": "ERR_USERNAME_OR_PASSWORD_ERROR"
        })
    else:
        headers = dict(typ="jwt", alg="HS256")
        payload = {'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                   'iat': datetime.datetime.utcnow(),
                   'iss': "owl",
                   "data": {'id': user.id}}
        encoding_jwt = jwt.encode(
            payload=payload, key=key1, algorithm='HS256', headers=headers)
        return jsonify({
            "status": 200,
            "token": encoding_jwt.decode()
        })


@auth.route("/isAuthorized", methods=['POST'])
def owl():
    try:
        headers = dict(typ="jwt", alg="HS256")
        # for i,j in request.headers.items():
        #     print(i,j)
        # print(tk)
        jwt_decode = jwt.decode(
            request.headers.get(
                'auth-token'), key=key1, algorithms=['HS256'], headers=headers)
    except jwt.ExpiredSignatureError:
        return jsonify({
            "status": 405,
            "info": "expired"
        })
    except Exception as e:
        print(repr(e))
        return jsonify({
            "status": 500,
            "info": "InternalServerErrorr"
        })
    return jsonify({
        "status": 200
    })
