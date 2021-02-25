import sys,os
import time
import curses

from curses.textpad import Textbox, rectangle
from threading import Thread, Event

import ip
import i18n

TOP_SPACING = 3
PING_LOOP_TIMEOUT = 0.1

class Screen:
    def __init__(self):
        self.k = 0
        self.line = TOP_SPACING
        self.selected_ip = ''
        self.is_drawing_help = False
        self.height = 0
        self.width = 0
    
    def init_meassures(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.line = max(0, self.line)
        self.line = min(self.height-1, self.line)
    
    def set_stdscr(self, stdscr):
        self.stdscr = stdscr
    
    def toggle_drawing_help(self):
        self.is_drawing_help = not self.is_drawing_help
    
    def next_line(self):
        if (self.line >= len(screen.ips.get_ips()) + TOP_SPACING - 1):
            return
        
        self.line += 1
        self.stdscr.move(self.line, 0)
        
    def prev_line(self):
        if (self.line <= TOP_SPACING):
            return
        
        self.line -= 1
        self.stdscr.move(self.line, 0)

screen = Screen()

def init_curses(stdscr, raw_ips):

    # Init ips
    screen.ips = ip.IPs()
    screen.ips.add_ips(raw_ips)

    # Clear and refresh the screen for a blank canvas
    screen.set_stdscr(stdscr)
    screen.stdscr.clear()
    screen.stdscr.refresh()
    screen.stdscr.nodelay(1)

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK) # Pinging
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK) # Timeout
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # Status bar

    draw_loop()

def draw_loop():
    while (screen.k is not ord('q')):
        # Init
        screen.stdscr.clear()
        screen.init_meassures()

        # Handle input
        handle_input()
            
        # Draw title and status bar
        draw_meta()

        # Ping loop
        draw_ping()

        # Closing loop
        screen.stdscr.refresh()
        time.sleep(PING_LOOP_TIMEOUT)

        # Next input
        screen.k = screen.stdscr.getch()

def handle_input():
    # Switch handles input over k
    if screen.k == curses.KEY_DOWN:
        screen.next_line()

    elif screen.k == curses.KEY_UP:
        screen.prev_line()

    elif (screen.k == ord('x')) and (screen.selected_ip in screen.ips.get_ips()):
        screen.ips.del_ip(screen.selected_ip)
        screen.prev_line()

    elif screen.k == ord('a'):
        new_ip = request_input(i18n.ADD_IP_TITLE)
        screen.ips.add_ip(new_ip)

    elif screen.k == ord('e'):
        new_ip = request_input(i18n.EDIT_IP_TITLE.format(screen.selected_ip))
        screen.ips.get_ip(screen.selected_ip).edit_ip(new_ip)
        
    elif screen.k == ord('h'):
        screen.toggle_drawing_help()

def draw_meta():
    # Draw title
    screen.stdscr.addstr(0, 0, i18n.DRAW_TITLE)
    
    # Draw status bar & help status bar
    screen.stdscr.attron(curses.color_pair(3))

    status_bar = i18n.STATUS_BAR_INFO.format(screen.selected_ip, screen.line)
    screen.stdscr.addstr(screen.height-1, 0, status_bar)
    screen.stdscr.addstr(screen.height-1, len(status_bar), " " * (screen.width - len(status_bar) - 1))

    if (screen.is_drawing_help):
        help_status_bar = i18n.STATUS_BAR_HELP
        screen.stdscr.addstr(screen.height-2, 0, help_status_bar)
        screen.stdscr.addstr(screen.height-2, len(help_status_bar), " " * (screen.width - len(help_status_bar) - 1))

    screen.stdscr.attroff(curses.color_pair(3))

def draw_ping():
    loop_index = TOP_SPACING
    for ip in screen.ips.get_ips():
        # Update selected_ip for deletion
        if (loop_index == screen.line):
            screen.selected_ip = ip

        t = Thread(target=exe_ping, args=(screen.ips.get_ip(ip), loop_index))
        t.start()

        loop_index += 1

def exe_ping(oip, current_line):
    ip, ping_last, is_timeout = oip.get_result()

    if is_timeout:
        screen.stdscr.attron(curses.color_pair(2))
        screen.stdscr.addstr(current_line, 0, i18n.PING_TIMEOUT.format(ip))
        screen.stdscr.attroff(curses.color_pair(2))

    elif ping_last == 0:
        screen.stdscr.addstr(current_line, 0, i18n.PING_WAITING.format(ip))

    else:
        screen.stdscr.attron(curses.color_pair(1))
        screen.stdscr.addstr(current_line, 0, i18n.PING_RESULT.format(ip, ping_last))
        screen.stdscr.attroff(curses.color_pair(1))
    
    oip.ping()

def request_input(title):
    screen.stdscr.addstr(0, 0, title)
    add_stdscr = curses.newwin(1, 60, 2, 1)
    
    rectangle(screen.stdscr, 1, 0, 3, 62)
    screen.stdscr.refresh()

    box = Textbox(add_stdscr)
    box.stripspaces = True
    box.edit()

    return box.gather()[:-1]