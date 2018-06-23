#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading
import pyinotify
from time import sleep

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, queue, folder, host, port):
        pyinotify.ProcessEvent.__init__(self)
        self._queue = queue
        self.folder = folder
        self.host = host
        self.port = port

    def process_IN_CREATE(self, event):
        last_file = ''
        try:
            last_file = self._queue.get(False)
        except Exception:
            print('Empty queue, you may have updates to send')

        if(last_file != event.pathname):
            print('LAST: ', last_file)
            print('Create detected!')
            sync = threading.Thread(target=Client.sendFile, args=(self.folder, event.pathname, 'create', self.host, self.port, self._queue))
            sync.daemon = True
            sync.start()
            sync._stop_event = threading.Event()
            sync.join(1)
            # Client.sendFile(self.folder, event.pathname, 'create', self.host, self.port, self._queue)

    def process_IN_DELETE(self, event):
        print('Delete detected! ', event.pathname)
        sync = threading.Thread(target=Client.sendFile, args=(self.folder, event.pathname, 'delete', self.host, self.port, self._queue))
        sync.daemon = True
        sync.start()
        sync._stop_event = threading.Event()
        sync.join(1)

    def process_IN_MODIFY(self, event):
        last_file = ''
        try:
            last_file = self._queue.get(False)
        except Exception:
            print('Empty queue, you may have updates to send')

        if(last_file != event.pathname):
            print('LAST: ', last_file)
            print('Modify detected! ', event.pathname)
            sync = threading.Thread(target=Client.sendFile, args=(self.folder, event.pathname, 'modify', self.host, self.port, self._queue))
            sync.daemon = True
            sync.start()
            sync._stop_event = threading.Event()
            sync.join(1)
            # Client.sendFile(self.folder, event.pathname, 'modify', self.host, self.port, self._queue)

class Client(threading.Thread):
    def __init__(self, host, port, path, queue):
        threading.Thread.__init__(self)
        self._running = True
        self._stop_event = threading.Event()
        self._queue = queue
        self._host = host
        self._port = int(port)
        self._path = path


    def run(self):
        print('Client ready')
        wm = pyinotify.WatchManager()
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
        handler = EventHandler(self._queue, self._path, self._host, self._port)
        notifier = pyinotify.Notifier(wm, handler)
        wd = wm.add_watch(self._path, mask)
        if wd.get(self._path) >= 0:
            print('Init watcher directory...')
            notifier.loop()
        else:
            raise Exception("Error adding watch directory")
            exit(1)

    def stop(self):
        self._stop_event.set()

    @staticmethod
    def sendFile(folder, path, action, host, port, queue):
        if action == 'create':
            queue.put(path)
        sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sckt.connect((host, port))
        file_name = path.replace(folder, '')
        if action != 'delete':
            file_name += '?'
        else:
            file_name += '*'
        print('Sending file name')
        sckt.send(bytes(file_name, 'utf-8'))
        if action != 'delete':
            print('Sending file body')
            with open(path, 'rb') as f:
                file_body = f.read(4096)
                while file_body:
                    sckt.send(file_body)
                    sleep(1)
                    file_body = f.read(4096)
        print('Closing connection')
        sckt.close()
        exit(0)
