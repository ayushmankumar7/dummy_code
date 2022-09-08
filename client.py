import zmq 
import datetime 

class message():
    image: None
    client_name: None
    image_id = 0

    def __init__(self, image, client_name, generate_image_id=True):
        self.image = image
        self.client_name = client_name
        if generate_image_id:
            self.image_id = int(
                datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))
                
class Client():
    server_ip = ""
    server_port = 0
    request_timeout = 0
    request_retries = 0
    client_name = ""
    context = None
    client = None
    server_endpoint = ""
    poll = None
    generate_image_id = False

    def __init__(self, client_name="", server_ip="localhost", server_port=5555, request_timeout=3000, request_retries=3, generate_image_id=True):
        self.server_ip = server_ip
        self.server_port = server_port
        self.request_retries = request_retries
        self.request_timeout = request_timeout
        self.client_name = client_name
        self.server_endpoint = "tcp://%s:%d" % (server_ip, server_port)
        self.context = zmq.Context(1)
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(self.server_endpoint)
        self.poll = zmq.Poller()
        self.poll.register(self.client, zmq.POLLIN)
        self.generate_image_id = generate_image_id

    def __del__(self):
        self.poll.unregister(self.client)
        self.context.term()

    def send(self, image):
        retries_left = self.request_retries
        new_message = message(image, self.client_name, self.generate_image_id)
        self.client.send_pyobj(new_message)
        expect_reply = True
        while expect_reply:
            socks = dict(self.poll.poll(self.request_timeout))
            if socks.get(self.client) == zmq.POLLIN:
                reply = self.client.recv()
                if not reply:
                    break
                else:
                    retries_left = self.request_retries
                    expect_reply = False

            else:

                print("W: No response from server, retrying…", flush=True)
                # Socket is confused. Close and remove it.
                self.client.setsockopt(zmq.LINGER, 0)
                self.client.close()
                self.poll.unregister(self.client)
                retries_left -= 1
                if retries_left == 0:
                    print("E: Server seems to be offline, abandoning", flush=True)
                    raise "Server seems to be offline, abandoning"
                print("I: Reconnecting and resending ", flush=True)
                # Create new connection
                self.client = self.context.socket(zmq.REQ)
                self.client.connect(self.server_endpoint)
                self.poll.register(self.client, zmq.POLLIN)
                self.client.send_pyobj(new_message)