#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pycchess - just another chinese chess UI
# Copyright (C) 2011 - 2015 timebug

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from common import *
from chessboard import Chessboard
from chessnet import Chessnet

import pygame
from pygame.locals import *

import sys
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

ON_POSIX = 'posix' in sys.builtin_module_names


init = True
waiting = False
moved = False
chessboard = None
screen = None
ai_proc = None
queue = Queue()


def enqueue_output(out, queue):
    for line in out:
        queue.put(line)
    out.close()


def init_game():
    global chessboard
    global screen
    global queue
    global ai_proc

    pygame.init()
    screen = pygame.display.set_mode(size, 0, 32)
    chessboard = Chessboard()

    if len(sys.argv) == 2 and sys.argv[1][:2] == '-n':
        chessboard.net = Chessnet()

        if sys.argv[1][2:] == 'r':
            pygame.display.set_caption("red")
            chessboard.side = RED
        elif sys.argv[1][2:] == 'b':
            pygame.display.set_caption("black")
            chessboard.side = BLACK
        else:
            print('>> quit game')
            sys.exit()

        chessboard.net.NET_HOST = sys.argv[2]

    elif len(sys.argv) == 1:
        # text = True: set text mode
        # bufsize = 1: set line buffer mode
        ai_proc = Popen("./harmless", stdin=PIPE, stdout=PIPE, close_fds=ON_POSIX, text=True, bufsize=1)
        chessboard.fin, chessboard.fout = ai_proc.stdin, ai_proc.stdout
        response = Thread(target=enqueue_output, args=(chessboard.fout, queue))
        response.daemon = True
        response.start()

        chessboard.fin.write("ucci\n")

        while True:
            try:
                output = queue.get_nowait()
            except Empty:
                continue
            else:
                print(output)
                if 'ucciok' in output:
                    break

        chessboard.mode = AI
        pygame.display.set_caption("harmless")
        chessboard.side = RED
    else:
        print('>> quit game')
        sys.exit()

    chessboard.fen_parse(fen_str)


def new_game():
    global init
    global waiting
    global moved

    chessboard.fin.write("setoption newgame\n")
    chessboard.fin.flush()
    print('>> new game')

    chessboard.fen_parse(fen_str)
    init = True
    waiting = False
    moved = False


def quit_game():
    global ai_proc

    if chessboard.mode is NETWORK:
        net = Chessnet()
        net.send_move('quit')
    if chessboard.mode is AI:
        chessboard.fin.write("quit\n")
        chessboard.fin.flush()
        ai_proc.terminate()

    print('>> quit game')
    sys.exit()


def run_game():
    global init
    global waiting
    global moved

    for event in pygame.event.get():
        if event.type == QUIT:
            quit_game()
        elif event.type == KEYDOWN:
            if event.key == K_r:
                if chessboard.mode == AI:
                    if not waiting or chessboard.over:
                        new_game()
                        return
            elif event.key == K_q:
                quit_game()
                return

        elif event.type == MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if x < BORDER or x > (WIDTH - BORDER):
                continue
            if y < BORDER or y > (HEIGHT - BORDER):
                continue
            x = (x - BORDER) // SPACE
            y = (y - BORDER) // SPACE
            if not waiting and not chessboard.over:
                moved = chessboard.move_chessman(x, y)
                if chessboard.mode == NETWORK and moved:
                    chessboard.over = chessboard.game_over(1-chessboard.side)
                    if chessboard.over:
                        chessboard.over_side = 1-chessboard.side

    chessboard.draw(screen)
    pygame.display.update()

    if moved:
        if chessboard.mode is NETWORK:
            move_str = chessboard.net.get_move()
            if move_str == 'quit':
                quit_game()
            else:
                move_arr = str_to_move(move_str)

        if chessboard.mode is AI:
            try:
                output = queue.get_nowait()
            except Empty:
                waiting = True
                return
            else:
                waiting = False
                sys.stdout.write(output)

            if output[0:10] == 'nobestmove':
                chessboard.over = True
                chessboard.over_side = 1 - chessboard.side

                if chessboard.over_side == RED:
                    win_side = 'BLACK'
                else:
                    win_side = 'RED'
                print('>>', win_side, 'win')

                return
            elif output[0:8] == 'bestmove':
                move_str = output[9:13]
                move_arr = str_to_move(move_str)
            else:
                return

        chessboard.side = 1 - chessboard.side
        chessboard.move_from = OTHER
        chessboard.move_chessman(move_arr[0], move_arr[1])
        chessboard.move_chessman(move_arr[2], move_arr[3])
        chessboard.move_from = LOCAL
        chessboard.side = 1 - chessboard.side

        # if chessboard.check(chessboard.side):
        chessboard.over = chessboard.game_over(chessboard.side)
        if chessboard.over:
            chessboard.over_side = chessboard.side

            if chessboard.over_side == RED:
                win_side = 'BLACK'
            else:
                win_side = 'RED'
            print('>>', win_side, 'win')

        moved = False

    if len(sys.argv) == 2 and sys.argv[1][:2] == '-n' and init:
        move_str = chessboard.net.get_move()
        if move_str is not None:
            move_arr = str_to_move(move_str)

            chessboard.side = 1 - chessboard.side
            chessboard.move_from = OTHER
            chessboard.move_chessman(move_arr[0], move_arr[1])
            chessboard.move_chessman(move_arr[2], move_arr[3])
            chessboard.move_from = LOCAL
            chessboard.side = 1 - chessboard.side
            init = False
        else:
            chessboard.over = True


def main():
    init_game()
    try:
        while True:
            run_game()
    except KeyboardInterrupt:
        quit_game()


if __name__ == '__main__':
    main()
