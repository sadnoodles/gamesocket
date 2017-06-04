#!/usr/bin/env python
# -*- coding: utf-8 -*-


def compatible_read(sock, size):
    return_value = ''
    while True:
        try:
            r = sock.recv(size)
        except:
            return None
        # print repr(r)
        if r == '' or r == '\x03' or r == '\x1a' or r == '\xff\xf4\xff\xfd\x06':  # Ctrl+C or Ctrl+Z or linxu Ctrl+c
            return None

        return_value += r

        if return_value.endswith('\n') or len(return_value) >= size:
            break

    return return_value


class GameBase(object):
    def __init__(self, sock, ip, need_login=False, line_sep='\r\n', allow_login_retry=False):
        self.sock = sock
        self.ip = ip
        self.sock_closed = False
        self.need_login = need_login
        self.allow_login_retry = allow_login_retry
        self.line_sep = line_sep

    def read(self, size=1024):
        return compatible_read(self.sock, size)

    def send(self, msg):
        try:
            self.sock.send(msg.encode('utf-8'))
        except:
            return

    def sendline(self, msg):
        self.send(msg + self.line_sep)

    write = send

    def login(self):
        # TODO: login
        # return True, "Welcome."
        raise NotImplementedError

    def get_input(self, hint):
        r = ''
        if not self.sock_closed:
            self.send(self.line_sep + hint)
            r = self.read(1024)
            if r is None:
                self.exit()
                return ''
        return r.rstrip('\r\n')

    def exit(self, word=''):
        if word:
            self.send(word)
        self.sock_closed = True
        self.sock.close()

    def game_begin(self, extra_data=None):
        # Todo
        raise NotImplementedError

    def start(self,):
        login_state, extra_data = False, ''
        if self.need_login:
            c = 0
            while c < 3:
                login_state, extra_data = self.login()
                c += 1
                if login_state:
                    break
                if not self.allow_login_retry:
                    break
                self.sendline("Login error: %s" % extra_data)
            if login_state:
                self.send(
                    self.line_sep +
                    'Login succeed!' +
                    self.line_sep)
            else:
                self.exit("Login Failed.")
        try:
            self.game_begin(extra_data)
        except Exception, e:
            print "Exception:", self.ip, e
        finally:
            self.exit(self.line_sep + "The End.")
        print "%s Closed." % self.ip
