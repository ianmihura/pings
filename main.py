import argparse
import sys,os
import curses
from curses.textpad import Textbox, rectangle
import time
from threading import Thread, Event

import ip
import i18n

has_curses = False
ips = ip.IPs()
TOP_SPACING = 3
    
def init_curses(stdscr):

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()
    stdscr.nodelay(1)

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # Status bar

    k = 0
    line = TOP_SPACING
    selected_ip = ''
    is_drawing_help = False
    while True:

        # Init
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        line = max(0, line)
        line = min(height-1, line)
        
        # Handle input
        if (k == ord('q')):
            break
        elif k == curses.KEY_DOWN:
            line += 1
        elif k == curses.KEY_UP:
            line -= 1
        elif (k == ord('x')) and (selected_ip in ips.ips):
            del ips.ips[selected_ip]
        elif k == ord('a'):
            new_ip = request_input(stdscr, i18n.ADD_IP_TITLE)
            ips.add_ip(new_ip)
        elif k == ord('e'):
            new_ip = request_input(stdscr, i18n.EDIT_IP_TITLE.format(selected_ip))
            ips.ips[selected_ip].edit_ip(new_ip)
        elif k == ord('h'):
            is_drawing_help = not is_drawing_help

        # Draw title
        stdscr.addstr(0, 0, i18n.DRAW_TITLE)
        
        # Draw status bar & help status bar
        stdscr.attron(curses.color_pair(3))

        status_bar = i18n.STATUS_BAR_INFO.format(line, selected_ip)
        stdscr.addstr(height-1, 0, status_bar)
        stdscr.addstr(height-1, len(status_bar), " " * (width - len(status_bar) - 1))

        if (is_drawing_help):
            help_status_bar = i18n.STATUS_BAR_HELP
            stdscr.addstr(height-2, 0, help_status_bar)
            stdscr.addstr(height-2, len(help_status_bar), " " * (width - len(help_status_bar) - 1))

        stdscr.attroff(curses.color_pair(3))

        # Ping loop
        loop_index = TOP_SPACING
        for ip_id in ips.ips:
            if (loop_index == line):
                selected_ip = ip_id

            ip = ips.ips[ip_id]

            t = Thread(target=exe_ping, args=(ip, stdscr, loop_index))
            t.start()

            loop_index += 1

        # Closing loop
        stdscr.move(line, 0)
        stdscr.refresh()
        time.sleep(0.1)
        k = stdscr.getch()
    
def exe_ping(ip, stdscr, line):
    stdscr.addstr(line, 0, ip.get_result())
    ip.ping()
    stdscr.addstr(line, 0, ip.get_result())

def request_input(stdscr, title):
    stdscr.addstr(0, 0, title)
    add_stdscr = curses.newwin(1, 60, 2, 1)
    
    rectangle(stdscr, 1,0, 3, 62)
    stdscr.refresh()

    box = Textbox(add_stdscr)
    box.stripspaces = True
    box.edit()

    return box.gather()[:-1]

def main():
    # Get parsed arguements
    parser = argparse.ArgumentParser()
    parser.add_argument('ips', type=str, help=i18n.ARGS_HELP)
    args = parser.parse_args()

    # Init all ips
    for ip in args.ips.split(','):
        ip = ips.add_ip(ip)
    
    # Start main curses loop
    curses.wrapper(init_curses)

if __name__ == '__main__':
    main()