import sys
import time
import curses

from curses.textpad import Textbox, rectangle
from threading import Thread, active_count

import ip
import i18n
import profile

class Screen:

    UP = -1
    DOWN = 1
    STATUS_BAR_SLEEP = 5
    CORE_LOOP_SLEEP = 0.1
    PING_LOOP_SLEEP = 1
    TIMEOUT = 2

    def __init__(self):
        # Keyboard stroke
        self.k = 0

        # Scroll & screen
        self.line = 0
        self.top = 0
        self.bottom = 0
        self.height = 0
        self.width = 0
        self.max_lines = 0
        self.page = 0

        # Other screen settings
        self.current_profile = ''
        self.status = ''
        self.status_history = []
        self.selected_ip = ''
        self.is_drawing_help = False
        self.is_drawing_status = False
        self.is_drawing_timeout = True
        self.close = False
    
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
    
    def toggle_drawing_timeout(self):
        self.is_drawing_timeout = not self.is_drawing_timeout

    def set_timeout(self, timeout):
        try:
            timeout = float(timeout)
            self.TIMEOUT = timeout
            for ip in self.ips.get_ips():
                self.ips.get_ip(ip).set_timeout(timeout)
        except:
            return

    def set_ping_loop_sleep(self, ping_loop_sleep):
        try:
            ping_loop_sleep = float(ping_loop_sleep)
            self.PING_LOOP_SLEEP = ping_loop_sleep
        except:
            return

    # File path
    def set_current_profile(self, profile):
        self.current_profile = profile

    def get_current_profile(self):
        return self.current_profile

    # Status
    def set_status(self, new_status):
        self.status = new_status
        self.status_history.append(new_status)

        t = Thread(target=self._show_status, args=())
        t.daemon = True
        t.start()

    def _show_status(self):
        self.is_drawing_status = True
        time.sleep(self.STATUS_BAR_SLEEP)
        self.is_drawing_status = False
        sys.exit()

    def get_status(self):
        return self.status
    
    def get_status_history(self):
        return self.status_history
    
    def clean_status_history(self):
        self.status_history = []
    
    # Scrolling & paging
    def scroll(self, direction):
        """Scrolling the window when pressing up/down arrow keys"""
        # next cursor position after scrolling
        next_line = self.line + direction

        # Up direction scroll overflow
        # current cursor position is 0, but top position is greater than 0
        if (direction == self.UP) and (self.top > 0 and self.line == 0):
            self.top += direction
            
        # Down direction scroll overflow
        # next cursor position touch the max lines, but absolute position of max lines could not touch the bottom
        elif (direction == self.DOWN) and (next_line == self.max_lines -1) and (self.top + self.max_lines < self.bottom):
            self.top += direction
            
        # Scroll up
        # current cursor position or top position is greater than 0
        elif (direction == self.UP) and (self.top > 0 or self.line > 0):
            self.line = next_line
            
        # Scroll down
        # next cursor position is above max lines, and absolute position of next cursor could not touch the bottom
        elif (direction == self.DOWN) and (next_line < self.max_lines) and (self.top + next_line < self.bottom):
            self.line = next_line
            
    
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

        # Page down
        # if current page is not a last page, page down is possible
        elif (direction == self.DOWN) and (current_page < self.page):
            self.top += self.max_lines
    
    # Request user input
    def request_input(self, title, content=''):
        self.stdscr.addstr(0, 0, title)
        add_stdscr = curses.newwin(1, 60, 2, 1)
        
        rectangle(self.stdscr, 1, 0, 3, 62)
        self.stdscr.refresh()
        add_stdscr.addstr(0,0,content)

        box = Textbox(add_stdscr)
        box.stripspaces = True
        box.edit()

        return box.gather()[:-1]

screen = Screen()

def init_curses(stdscr, raw_ips, raw_ips_names):

    # Init ips
    screen.ips = ip.IPs()
    screen.ips.add_ips(raw_ips, raw_ips_names)

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

    t = Thread(target=ping_loop, args=())
    t.daemon = True
    t.start()

    draw_loop()

def ping_loop():
    while (True):
        ips = screen.ips.get_ips_range(
            screen.top -1, 
            screen.top + screen.max_lines + screen.ips.timeout_ips, 
            screen.is_drawing_timeout )

        for ip in ips:
            t = Thread(target=screen.ips.get_ip(ip).ping)
            t.daemon = True
            t.start()
        
        time.sleep(screen.PING_LOOP_SLEEP)

        if screen.close:
            sys.exit()

def draw_loop():
    while (True):
        # Init
        screen.stdscr.clear()
        screen.init_meassures()

        # Ping loop
        draw_ping()
        
        # Draw title and status bar
        draw_bar()

        # Handle input
        handle_input()

        # Closing loop
        screen.stdscr.refresh()
        time.sleep(screen.CORE_LOOP_SLEEP)

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
        screen.set_status(i18n.DELETE_IP_SUCCESS.format(screen.selected_ip))

    elif screen.k == ord('a'):
        new_ip = screen.request_input(i18n.ADD_IP_TITLE)
        screen.ips.add_ip(new_ip)
        screen.set_status(i18n.ADD_IP_SUCCESS.format(new_ip))

    elif screen.k == ord('n'):
        old_name = screen.ips.get_ip(screen.selected_ip).get_name()
        new_name = screen.request_input(i18n.EDIT_IP_TITLE.format(screen.selected_ip), old_name)
        screen.ips.get_ip(screen.selected_ip).set_name(new_name)

    elif screen.k == ord('h'):
        screen.toggle_drawing_help()

    elif screen.k == ord('t'):
        screen.toggle_drawing_timeout()

    elif screen.k == ord('r'):
        time.sleep(3)
    
    elif screen.k == ord('p'):
        new_ping_loop_title = i18n.CONFIG_PING_LOOP_SLEEP.format(screen.PING_LOOP_SLEEP)
        new_ping_loop = screen.request_input(new_ping_loop_title, str(screen.PING_LOOP_SLEEP))
        screen.set_ping_loop_sleep(new_ping_loop)

    elif screen.k == ord('s'):
        current_profile = screen.get_current_profile()
        new_profile = screen.request_input(i18n.SAVE_PROFILE.format(
            current_profile if current_profile else '> NO CURRENT PROFILE <'), current_profile)        
        result_status, saved_profile = profile.save_profile(new_profile, current_profile, screen.ips.get_ips())
        screen.set_current_profile(saved_profile)
        screen.set_status(result_status)
        
    elif screen.k == ord('q'):
        current_profile = screen.get_current_profile()
        screen.close = True
        if not current_profile: sys.exit()
        else:
            save_profile_title = i18n.SAVE_PROFILE_EXIT.format(current_profile)
            save_profile = screen.request_input(save_profile_title).upper()
            if save_profile == 'Y' or save_profile == 'YES':
                profile.save_profile(current_profile, current_profile, screen.ips.get_ips())
            sys.exit()

def draw_bar():
    range_top, range_bottom = screen.ips.get_range()
    info_bar = " " + i18n.INFO_BAR.format(
        screen.selected_ip, 
        range_top if range_top >= 0 else 0,
        min(len(screen.ips.get_ips()), range_bottom),
        len(screen.ips.get_ips()),
        active_count())
    info_bar += " " * (screen.width - len(info_bar) - 1) 
    screen.stdscr.addstr(screen.height-1, 0, info_bar, curses.color_pair(5))

    next_available = -2

    if (screen.is_drawing_help):
        help_bar = " " + i18n.HELP_BAR
        help_bar += (" " * (screen.width - len(help_bar) - 1))
        screen.stdscr.addstr(screen.height + next_available, 0, help_bar, curses.color_pair(5))
        next_available -= 1
    
    if (screen.is_drawing_status):
        status_bar = " " + screen.get_status()
        status_bar += (" " * (screen.width - len(status_bar) - 1))
        screen.stdscr.addstr(screen.height + next_available, 0, status_bar, curses.color_pair(5))
    
def draw_ping():
    no_ips = True
    ips = screen.ips.get_ips_range(
        screen.top -1, 
        screen.top + screen.max_lines + screen.ips.timeout_ips, 
        screen.is_drawing_timeout )

    for idx, ip in enumerate(ips):
        no_ips = False
        is_selected = False
        if (idx == screen.line):
            screen.selected_ip = ip
            is_selected = True
        
        _draw_ping(screen.ips.get_ip(ip), idx, is_selected)

    if no_ips: screen.stdscr.addstr(0,0,i18n.DRAW_NO_IP)

def _draw_ping(oip, current_line, is_selected):
    if current_line > screen.max_lines:
        return

    ip, name, ping_last, is_timeout = oip.get_result()
    if name: ip = '{} - {}'.format(name, ip)

    if is_timeout and is_selected: # Timeout, selected
        screen.stdscr.addstr(current_line, 0, i18n.PING_TIMEOUT.format(ip), curses.color_pair(4))
    elif is_timeout and not is_selected: # Timeout, not selected
        screen.stdscr.addstr(current_line, 0, i18n.PING_TIMEOUT.format(ip), curses.color_pair(2))
    elif ping_last == 0 and is_selected: # Status bar, neutral, selected
        screen.stdscr.addstr(current_line, 0, i18n.PING_WAITING.format(ip), curses.color_pair(5))
    elif ping_last == 0 and not is_selected:
        screen.stdscr.addstr(current_line, 0, i18n.PING_WAITING.format(ip))
    elif is_selected: # Online, selected
        screen.stdscr.addstr(current_line, 0, i18n.PING_RESULT.format(ip, ping_last), curses.color_pair(3))
    elif not is_selected: # Online, not selected
        screen.stdscr.addstr(current_line, 0, i18n.PING_RESULT.format(ip, ping_last), curses.color_pair(1))