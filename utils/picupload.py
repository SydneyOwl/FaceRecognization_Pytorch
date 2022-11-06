from utils import client,bucket,region
from uuid import uuid4
def upload_img_to_cos(path):
    picName = str(uuid4())
    with open(path, 'rb') as fp:
        client.put_object(
            Bucket=bucket,
            Body=fp,
            Key='/frame_thumb/{}.jpg'.format(picName),
            StorageClass='STANDARD',
            EnableMD5=False
        )
    return "https://{}.cos.{}.myqcloud.com/frame_thumb/{}.jpg".format(bucket,region,picName)
def upload_byte_to_cos(bt:bytes,picName,route = "face_thumb"):
    client.put_object(
            Bucket=bucket,
            Body=bt,
            Key='/{}/{}.jpg'.format(route,picName),
            StorageClass='STANDARD',
            EnableMD5=False
        )
    return "https://{}.cos.{}.myqcloud.com/{}/{}.jpg".format(bucket,region,route,picName)