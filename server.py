import queue 
import threading 

import zmq 

class Server():
    qu = queue.Queue()
    def __init__(self,server_ip,  port=5555, listener=10):
        self.server_ip = server_ip
        self.port = port
        self.listener = listener
        self.qu = queue.Queue()
        thread = threading.Thread(target=self.start)
        thread.start()

    def __del__(self):
        print('Destructor called.')

    def worker_routine(self, worker_url, context: zmq.Context = None):
        context = context or zmq.Context.instance()
        socket = context.socket(zmq.REP)
        socket.connect(worker_url)

        while True:
            message = socket.recv_pyobj()
            socket.send_string("ok")
            self.qu.put(message)

    def receive(self):
        while True:
            message = self.qu.get()
            return message

    def start(self):
        url_worker = "inproc://workers"
        url_client = f"tcp://{self.server_ip}:"+str(self.port)

        # Prepare our context and sockets
        context = zmq.Context.instance()

        # Socket to talk to clients
        clients = context.socket(zmq.ROUTER)
        clients.bind(url_client)

        # Socket to talk to workers
        workers = context.socket(zmq.DEALER)
        workers.bind(url_worker)

        # Launch pool of worker threads
        for i in range(self.listener):
            thread = threading.Thread(
                target=self.worker_routine, args=(url_worker,))
            thread.start()

        zmq.proxy(clients, workers)