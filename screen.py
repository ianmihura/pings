import sys,os
import time
import curses

from curses.textpad import Textbox, rectangle
from threading import Thread, active_count

import ip
import i18n

TOP_SPACING = 0
PING_LOOP_TIMEOUT = 0.1

class Screen:

    UP = -1
    DOWN = 1

    def __init__(self):
        # Keyboard stroke
        self.k = 0

        # Scroll & screen
        self.line = TOP_SPACING
        self.top = 0
        self.bottom = 0
        self.height = 0
        self.width = 0
        self.max_lines = 0
        self.page = 0

        self.selected_ip = ''
        self.is_drawing_help = False
    
    def init_meassures(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.max_lines = self.height -1
        self.bottom = len(self.ips.get_ips())
        self.line = max(0, self.line)
        self.line = min(self.height-1, self.line)
        self.page = self.bottom // self.max_lines
    
    def set_stdscr(self, stdscr):
        self.stdscr = stdscr
    
    def toggle_drawing_help(self):
        self.is_drawing_help = not self.is_drawing_help
    
    def scroll(self, direction):
        """Scrolling the window when pressing up/down arrow keys"""
        # next cursor position after scrolling
        next_line = self.line + direction

        # Up direction scroll overflow
        # current cursor position is 0, but top position is greater than 0
        if (direction == self.UP) and (self.top > 0 and self.line == 0):
            self.top += direction
            return
        # Down direction scroll overflow
        # next cursor position touch the max lines, but absolute position of max lines could not touch the bottom
        if (direction == self.DOWN) and (next_line == self.max_lines -1) and (self.top + self.max_lines < self.bottom):
            self.top += direction
            return
        # Scroll up
        # current cursor position or top position is greater than 0
        if (direction == self.UP) and (self.top > 0 or self.line > 0):
            self.line = next_line
            return
        # Scroll down
        # next cursor position is above max lines, and absolute position of next cursor could not touch the bottom
        if (direction == self.DOWN) and (next_line < self.max_lines) and (self.top + next_line < self.bottom):
            self.line = next_line
            return
    
    def paging(self, direction):
        current_page = (self.top + self.line) // self.max_lines
        next_page = current_page + direction
        # The last page may have fewer items than max lines,
        # so we should adjust the current cursor position as maximum item count on last page
        if next_page == self.page:
            self.line = min(self.line, self.bottom % self.max_lines - 1)

        # Page up
        # if current page is not a first page, page up is possible
        # top position can not be negative, so if top position is going to be negative, we should set it as 0
        if (direction == self.UP) and (current_page > 0):
            self.top = max(0, self.top - self.max_lines)
            return

        # Page down
        # if current page is not a last page, page down is possible
        if (direction == self.DOWN) and (current_page < self.page):
            self.top += self.max_lines
            return

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
    curses.start_color() # Neutral, not selected
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK) # Online, not selected
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK) # Timeout, not selected
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_WHITE) # Online, selected
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE) # Timeout, selected
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE) # Status bar, neutral, selected

    draw_loop()

def draw_loop():
    while (screen.k is not ord('q')):
        # Init
        screen.stdscr.clear()
        screen.init_meassures()

        # Handle input
        handle_input()
            
        # Draw title and status bar
        draw_bar()

        # Ping loop
        draw_ping()

        # Closing loop
        screen.stdscr.refresh()
        time.sleep(PING_LOOP_TIMEOUT)

        # Next input
        screen.k = screen.stdscr.getch()

def handle_input():
    if screen.k == curses.KEY_DOWN:
        screen.scroll(screen.DOWN)

    elif screen.k == curses.KEY_UP:
        screen.scroll(screen.UP)

    elif screen.k == curses.KEY_RIGHT:
        screen.paging(screen.DOWN)

    elif screen.k == curses.KEY_LEFT:
        screen.paging(screen.UP)

    elif (screen.k == ord('x')) and (screen.selected_ip in screen.ips.get_ips()):
        screen.ips.del_ip(screen.selected_ip)
        screen.scroll(screen.UP)

    elif screen.k == ord('a'):
        new_ip = request_input(i18n.ADD_IP_TITLE)
        screen.ips.add_ip(new_ip)

    elif screen.k == ord('e'):
        new_ip = request_input(i18n.EDIT_IP_TITLE.format(screen.selected_ip))
        screen.ips.get_ip(screen.selected_ip).edit_ip(new_ip)
        
    elif screen.k == ord('h'):
        screen.toggle_drawing_help()

def draw_bar():
    range_top, range_bottom = screen.ips.get_range()
    status_bar = i18n.STATUS_BAR_INFO.format(screen.selected_ip, range_top, range_bottom, len(screen.ips.get_ips()), active_count())
    status_bar += " " * (screen.width - len(status_bar) - 1) 
    screen.stdscr.addstr(screen.height-1, 0, status_bar, curses.color_pair(5))

    if (screen.is_drawing_help):
        help_status_bar = i18n.STATUS_BAR_HELP 
        help_status_bar += (" " * (screen.width - len(help_status_bar) - 1))
        screen.stdscr.addstr(screen.height-2, 0, help_status_bar, curses.color_pair(5))

def draw_ping():
    for idx, ip in enumerate(screen.ips.get_ips_range(screen.top, screen.top + screen.max_lines)):
        is_selected = False
        if (idx == screen.line):
            screen.selected_ip = ip
            is_selected = True

        t = Thread(target=exe_ping, args=(screen.ips.get_ip(ip), idx, is_selected))
        t.daemon = True
        t.start()

def exe_ping(oip, current_line, is_selected):
    ip, ping_last, is_timeout = oip.get_result()

    if is_timeout and is_selected:
        screen.stdscr.addstr(current_line, 0, i18n.PING_TIMEOUT.format(ip), curses.color_pair(4))
    elif is_timeout and not is_selected:
        screen.stdscr.addstr(current_line, 0, i18n.PING_TIMEOUT.format(ip), curses.color_pair(2))
    elif ping_last == 0 and is_selected:
        screen.stdscr.addstr(current_line, 0, i18n.PING_WAITING.format(ip), curses.color_pair(5))
    elif ping_last == 0 and not is_selected:
        screen.stdscr.addstr(current_line, 0, i18n.PING_WAITING.format(ip))
    elif is_selected:
        screen.stdscr.addstr(current_line, 0, i18n.PING_RESULT.format(ip, ping_last), curses.color_pair(3))
    elif not is_selected:
        screen.stdscr.addstr(current_line, 0, i18n.PING_RESULT.format(ip, ping_last), curses.color_pair(1))
    
    oip.ping()
    sys.exit()

def display():
    screen.stdscr.erase()
    for idx, item in screen.ips.get_ips_range(screen.top, screen.top + screen.max_lines):

        if idx == screen.line:
            screen.stdscr.addstr(idx, 0, item, curses.color_pair(2))
        else:
            screen.stdscr.addstr(idx, 0, item, curses.color_pair(1))
        
    screen.stdscr.refresh()

def request_input(title):
    screen.stdscr.addstr(0, 0, title)
    add_stdscr = curses.newwin(1, 60, 2, 1)
    
    rectangle(screen.stdscr, 1, 0, 3, 62)
    screen.stdscr.refresh()

    box = Textbox(add_stdscr)
    box.stripspaces = True
    box.edit()

    return box.gather()[:-1]