import jwt
from config import jwt_cfg
def jwtdecode(token,key):
    headers = dict(typ="jwt", alg="HS256")
    jwt_decode = jwt.decode(
        token, key=key, algorithms=['HS256'], headers=headers)
    return jwt_decode
def jwtDecodeDefault(request):
    raw = request.headers.get(
        'auth-token')
    headers = dict(typ="jwt", alg="HS256")
    jwt_decode = jwt.decode(
        raw, key=jwt_cfg["key"], algorithms=['HS256'], headers=headers)
    return jwt_decode  