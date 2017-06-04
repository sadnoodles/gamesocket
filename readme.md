# Game Socket

A socket interface game server. Build your own socket games! Learn from the `example.py`!

## Example:

See [example.py](./example.py)

Start it use `python example.py` and play it use :

`telnet 127.0.0.1 52700` 

or 

`nc 127.0.0.1 52700`

Or some other socket tools you like.


## Install

Download or clone this repo, put it together with your scripts, then import.

## Describe:

The `server.py` contains a GameServer which is the server. Most time you don't need to rewrite it, just use it.

The `game.py` contains a GameBase which is the game logic. Basicly you can copy a `example.py` and rewrite the `game_begin` function with you own game. And a new socket game done!

## More

### Login

Rewrite the login function, ask players for username or password or anything, then validate them. And return `True, extra_data` or `False, error_info`.
