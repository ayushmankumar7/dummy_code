import cv2 

from client import Client

client=Client("cc1",server_ip="192.168.0.113")
vid=cv2.VideoCapture(0)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

while True:
    r,frame=vid.read()
    if r:
        r, image = cv2.imencode('.jpg', frame, encode_param)
        client.send(image)
    else:
        break