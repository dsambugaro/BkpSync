#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
from time import sleep
from sys import argv, exit
from queue import Queue

import server
import client

class MainController(threading.Thread):
    def __init__(self, host, port, port_client, path):
        threading.Thread.__init__(self)
        self._running = True
        self._stop_event = threading.Event()
        self._queue = Queue()
        self.server = server.Server('localhost', port, path, self._queue)
        self.client = client.Client(host, port_client, path, self._queue)

    def run(self):
        self.printName()
        try:
            self.server.daemon = True
            self.server.start()
            self.server.join(1)
            self.client.daemon = True
            self.client.start()
            self.client.join(1)
        except Exception as e:
            print('\n\n')
            print('An error has happened in main.py: ' + e)
            print('\n\n')

    def stop(self):
        self.server.stop();
        self.client.stop();
        self._stop_event.set()

    def printName(self):

        # 88888888ba  88                     ad88888ba
        # 88      "8b 88                    d8"     "8b
        # 88      ,8P 88                    Y8,
        # 88aaaaaa8P' 88   ,d8  8b,dPPYba,  `Y8aaaaa,   8b       d8 8b,dPPYba,   ,adPPYba,
        # 88""""""8b, 88 ,a8"   88P'    "8a   `"""""8b, `8b     d8' 88P'   `"8a a8"     ""
        # 88      `8b 8888[     88       d8         `8b  `8b   d8'  88       88 8b
        # 88      a8P 88`"Yba,  88b,   ,a8" Y8a     a8P   `8b,d8'   88       88 "8a,   ,aa
        # 88888888P"  88   `Y8a 88`YbbdP"'   "Y88888P"      Y88'    88       88  `"Ybbd8"'
        #                       88                          d8'
        #                       88                         d8'

        os.system('clear')
        print('\n\n')
        print('===================================================================================')
        print('88888888ba  88                     ad88888ba                                      ')
        print('88      "8b 88                    d8"     "8b                                     ')
        print('88      ,8P 88                    Y8,                                             ')
        print('88aaaaaa8P\' 88   ,d8  8b,dPPYba,  `Y8aaaaa,   8b       d8 8b,dPPYba,   ,adPPYba,  ')
        print('88""""""8b, 88 ,a8"   88P\'    "8a   `"""""8b, `8b     d8\' 88P\'   `"8a a8"     ""  ')
        print('88      `8b 8888[     88       d8         `8b  `8b   d8\'  88       88 8b          ')
        print('88      a8P 88`"Yba,  88b,   ,a8" Y8a     a8P   `8b,d8\'   88       88 "8a,   ,aa  ')
        print('88888888P"  88   `Y8a 88`YbbdP"\'   "Y88888P"      Y88\'    88       88  `"Ybbd8"\'  ')
        print('                      88                          d8\'                             ')
        print('                      88                         d8\'                              ')
        print('===================================================================================')
        print('\n\n')

def main():
    try:
        host = argv[1]
        port = argv[2]
        port_client = argv[3]
        path = argv[4]
        mc = MainController(host, port, port_client, path)
        mc.daemon = True
        mc.start()
        mc.join()
    except Exception:
        print('Usage:\n\t %s <host> <host port> <client port> <path>' % argv[0])
        exit(1)
    while True:
        try:
            sleep(1)
        except (KeyboardInterrupt, SystemExit):
            stop = input('Do you really want end synchronization? (y/N)')
            if stop == 'y' or stop == 'Y':
                mc.stop()
                while mc.is_alive():
                    pass
                print('\n\n')
                print('Ending Synchronization...')
                print('\n\n')
                exit(0)
            continue



if __name__ == "__main__":
    main()
