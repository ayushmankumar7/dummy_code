import cv2

from server import Server 

server = Server("192.168.0.113")
while True:
    message = server.receive() 
    frame = cv2.imdecode(message.image, cv2.IMREAD_COLOR)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()