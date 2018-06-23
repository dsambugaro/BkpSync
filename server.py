#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading
import os
from time import sleep

class Server(threading.Thread):
    _conn = None
    _syncs = []
    def __init__(self, host, port, path, queue):
        threading.Thread.__init__(self)
        self._running = True
        self._stop_event = threading.Event()
        self._queue = queue
        self._host = host
        self._port = int(port)
        self._path = path
        self._sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self._sckt.bind((self._host, self._port))
        self._sckt.listen(5)
        while self._running:
            print('Server listening...')
            conn, addr = self._sckt.accept()
            print('Connected by client ', addr)
            print('Creating Thread to receive modifications')
            sync = threading.Thread(target=self.update, args=(conn, self._path, self._queue, addr))
            sync.daemon = True
            sync.start()
            sync._stop_event = threading.Event()
            sync.join(1)
            self._syncs.append(sync)

    def update(self, conn, path, queue, addr):
        file_name = ''
        aux = b''
        while True:
            aux = conn.recv(1)
            if aux.decode('utf-8') == '?':
                break
            if aux.decode('utf-8') == '*':
                break
            file_name += aux.decode('utf-8')
        file_path = (path + file_name)
        if aux.decode('utf-8') != '*':
            print("Updating file {}. Command from client {}".format(file_path, addr))
            queue.put(file_path)
            with open(file_path, 'wb') as f:
                while True:
                    file_body = conn.recv(4096)
                    if not file_body:
                        break
                    queue.put(file_path)
                    sleep(0.5)
                    f.write(file_body)
            print('File ' + file_path + ' updated')
        else:
            queue.put(file_path)
            print("Deleting file {}. Command from client {}".format(file_path, addr))
            try:
                os.remove(file_path)
            except Exception:
                print('File ' + file_path + ' deleted')
        exit(0)

    def stop(self):
        for sync in self._syncs:
            sync._stop_event.set()
        self._stop_event.set()
