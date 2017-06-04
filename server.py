#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
import socket
import json

from game import GameBase


class Settings(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __init__(self, filename='', data=None):
        self.banner = ''
        self.socket_timeout = 30  # seconds
        self.limit_ip = True  # limit connections of each ip
        self.ip_refresh_interval = 15 * 60  # 15 minute
        self.max_connection = 50
        self.line_sep = '\r\n'
        self.need_login = False
        self.allow_login_retry = False
        if filename:
            self.load(filename)
        if isinstance(data, dict):
            self.__dict__.update(data)

    def load(self, filename):
        try:
            d = json.load(open(filename))
            self.__dict__.update(d)
        except Exception, e:
            print e

    def dump(self, filename):
        try:
            json.dump(self, open(filename, 'w'), indent=4)
        except Exception, e:
            print e


class IPCounter(object):
    def __init__(self, IP_REFRESH_SECONDS=15 * 60, MAX_CONNECTION_COUNT=100):
        self.__ip_dict = {}
        self.IP_REFRESH_SECONDS = IP_REFRESH_SECONDS
        self.MAX_CONNECTION_COUNT = MAX_CONNECTION_COUNT
        self.__thread = None

    def reset_ip_dict(self):
        while True:
            time.sleep(self.IP_REFRESH_SECONDS)
            self.__ip_dict.clear()

    def count(self):
        return len(self.__ip_dict)

    def add(self, ip, n=1):
        # 返回是否超出ip最大连接数
        self.__ip_dict[ip] = self.__ip_dict.get(ip, 0) + n
        return self.__ip_dict[ip] > self.MAX_CONNECTION_COUNT

    def start_refresh_thread(self):
        t_ip_reset = threading.Thread(target=self.reset_ip_dict)
        self.__thread = t_ip_reset
        self.__thread.setDaemon(True)
        t_ip_reset.start()


class GameServer(threading.Thread):
    def __init__(self, ip, port, banner='', setting_filename=''):
        super(self.__class__, self).__init__()
        self.settings = Settings(filename=setting_filename)
        if banner:
            self.settings.banner = banner
        self.address = (ip, port)
        self.BUFSIZE = 1024
        self.ip_counter = IPCounter(
            self.settings.ip_refresh_interval,
            self.settings.max_connection)
        self.init_sock()
        self.running = False

    def on_connect(self, sock, ip):
        # TODO : Override this functions to do something before game begin.
        if self.settings.banner:
            sock.send(self.settings.banner + self.settings.line_sep)

    def handle_client(self, sock, ip, game_cls=None):
        game_cls = game_cls or self.game_cls
        if not issubclass(game_cls, GameBase):
            raise TypeError("'game_cls' Must be a subclass of GameBase")
        self.on_connect(sock, ip)
        c = game_cls(sock, ip,
                     self.settings.need_login,
                     self.settings.line_sep,
                     self.settings.allow_login_retry)
        c.start()

    def init_sock(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.address)
        self.timeout = 30
        self.sock.listen(5)  # 0-5 maximum number of queued connections

    def set_game(self, cls):
        if not issubclass(cls, GameBase):
            raise TypeError("Must be a subclass of GameBase")
        self.game_cls = cls

    def run(self):
        self.ip_counter.start_refresh_thread()

        self.running = True
        while self.running:
            client_sock = None
            print 'Threading active count:', threading.activeCount()
            try:
                print 'Waiting for connection...'
                client_sock, addr = self.sock.accept()
                if not self.running:
                    client_sock.close()
                    break
                # ip 连接计数
                print "Got connection from:", addr
                ip = addr[0]
                if self.settings.limit_ip:
                    print 'IP dict length:', self.ip_counter.count()
                    if self.ip_counter.add(ip):
                        print "E:%s Hit The IP Connection Limit." % ip
                        client_sock.send(
                            'Maximum number of connect times. Wait for 1~15 minutes.')
                        raise
                client_sock.settimeout(self.settings.socket_timeout)
                t = threading.Thread(
                    target=self.handle_client, args=(client_sock, ip))
                t.setDaemon(True)
                t.start()
            except KeyboardInterrupt:
                if client_sock:
                    client_sock.close()
                break
            except Exception, e:
                print(str(e))
                if client_sock:
                    client_sock.close()
                continue
        self.sock.close()

    def stop(self):
        self.running = False
        socket.socket(socket.AF_INET,
                      socket.SOCK_STREAM).connect(self.address)

    @classmethod
    def run_server(cls, ip, port, game_cls, banner='', setting_filename=''):
        gs = cls(ip, port, banner=banner, setting_filename=setting_filename)
        gs.set_game(game_cls)
        gs.start()
        while 1:
            try:
                time.sleep(0.2)
            except KeyboardInterrupt:
                gs.stop()
                break
        print "Exit. Bye~"
