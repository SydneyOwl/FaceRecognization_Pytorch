import cv2 
if __name__ == "__main__":
  ## 读取rtsp视频流并显示
  cap = cv2.VideoCapture("rtmp://IP/live/test")
  ## 读取usb-came 0（/dev/video0） 
  #cap = cv2.VideoCapture(0)
  while cap.isOpened():
    (ret,frame)=cap.read()
    if ret:
        # print (frame.shape[0], frame.shape[1], frame.shape[2])
        cv2.imshow("frame",frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
  cv2.destroyWindow("frame")
  cap.release()
