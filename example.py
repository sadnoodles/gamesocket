#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This is a example of using gamesocket to write a game that you can play it on socket.
Start this script and run:

`telnet 127.0.0.1 52700` 
or 
`nc 127.0.0.1 52700`

Or some other socket tools you like.

All you need to do is write a game_begin function  like the ExampleGame.
You can interact with players by using 'get_input' and 'send' or 'sendline'.
Easy like using a command line.
Multi-threading is already handled by the GameServer.
Focus on a single player!
'''
import random
from game import GameBase


class ExampleGame(GameBase):
    def game_begin(self, extra_data=None):
        n = random.randint(0, 10000)
        c = 0
        self.sendline("Guess a number under 10000.")
        while 1:
            number = self.get_input("Input a number:")
            try:
                number = int(number)
            except:
                self.sendline("Not a number!")
                continue
            if number == n:
                self.send("Yes, it's %s. You Win! You guessed %s times" % (n, c))
                break
            if number > n:
                self.sendline("Not it. A little less.")

            if number < n:
                self.sendline("Not it. A bit more.")
            c += 1


def main():
    from server import GameServer
    GameServer.run_server(
        "127.0.0.1", 52700,
        ExampleGame,
        banner='=== Guess Number Game ===')


if __name__ == '__main__':
    main()
