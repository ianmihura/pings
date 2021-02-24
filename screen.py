import sys,os
import time
import curses

from curses.textpad import Textbox, rectangle
from threading import Thread, Event

import ip
import i18n

class Screen(object):

    TOP_SPACING = 3
    PING_LOOP_TIMEOUT = 0.1

    def __init__(self, raw_ips):
        
        # Init ips
        self.ips = ip.IPs()
        self.ips.add_ips(raw_ips)

        # Clear and refresh the screen for a blank canvas
        self.stdscr = curses.initscr()
        self.stdscr.clear()
        self.stdscr.refresh()
        self.stdscr.nodelay(1)

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK) # Pinging
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK) # Timeout
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # Status bar

        self.draw_loop()

    def draw_loop(self):
        self.k = 0
        self.line = self.TOP_SPACING
        self.selected_ip = ''
        self.is_drawing_help = False

        while (self.k is not ord('q')):
            # Init
            self.stdscr.clear()
            self.height, self.width = self.stdscr.getmaxyx()
            self.line = max(0, self.line)
            self.line = min(self.height-1, self.line)
    
            # Handle input
            self._handle_input()
                
            # Draw title and status bar
            self._draw_meta()

            # Ping loop
            self._draw_ping()

            # Closing loop
            self.stdscr.move(self.line, 0)
            self.stdscr.refresh()
            time.sleep(self.PING_LOOP_TIMEOUT)

            # Next input
            self.k = self.stdscr.getch()
    
    def _handle_input(self):
        # Switch handles input over self.k
        if self.k == curses.KEY_DOWN and (self.line < len(self.ips.get_ips()) + self.TOP_SPACING - 1):
            self.line += 1

        elif self.k == curses.KEY_UP and self.line > self.TOP_SPACING:
            self.line -= 1

        elif (self.k == ord('x')) and (self.selected_ip in self.ips.get_ips()):
            self.ips.del_ip(self.selected_ip)
            self.selected_ip = ''
            self.line -= 1

        elif self.k == ord('a'):
            new_ip = self.request_input(i18n.ADD_IP_TITLE)
            self.ips.add_ip(new_ip)

        elif self.k == ord('e'):
            new_ip = self.request_input(i18n.EDIT_IP_TITLE.format(self.selected_ip))
            self.ips.get_ip(self.selected_ip).edit_ip(new_ip)
            
        elif self.k == ord('h'):
            self.is_drawing_help = not self.is_drawing_help
    
    def _draw_meta(self):
        # Draw title
        self.stdscr.addstr(0, 0, i18n.DRAW_TITLE)
        
        # Draw status bar & help status bar
        self.stdscr.attron(curses.color_pair(3))

        status_bar = i18n.STATUS_BAR_INFO.format(self.selected_ip)
        self.stdscr.addstr(self.height-1, 0, status_bar)
        self.stdscr.addstr(self.height-1, len(status_bar), " " * (self.width - len(status_bar) - 1))

        if (self.is_drawing_help):
            help_status_bar = i18n.STATUS_BAR_HELP
            self.stdscr.addstr(self.height-2, 0, help_status_bar)
            self.stdscr.addstr(self.height-2, len(help_status_bar), " " * (self.width - len(help_status_bar) - 1))

        self.stdscr.attroff(curses.color_pair(3))
    
    def _draw_ping(self):
        loop_index = self.TOP_SPACING
        for ip in self.ips.get_ips():
            if (loop_index == self.line):
                self.selected_ip = ip

            t = Thread(target=self.exe_ping, args=(self.ips.get_ip(ip), loop_index))
            t.start()

            loop_index += 1

    
    def exe_ping(self, oip, current_line):
        ip, ping_last, is_timeout = oip.get_result()

        if is_timeout:
            self.stdscr.attron(curses.color_pair(2))
            self.stdscr.addstr(current_line, 0, i18n.PING_TIMEOUT.format(ip))
            self.stdscr.attroff(curses.color_pair(2))

        elif ping_last == 0:
            self.stdscr.addstr(current_line, 0, i18n.PING_WAITING.format(ip))

        else:
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(current_line, 0, i18n.PING_RESULT.format(ip, ping_last))
            self.stdscr.attroff(curses.color_pair(1))
        
        oip.ping()

    def request_input(self, title):
        self.stdscr.addstr(0, 0, title)
        add_stdscr = curses.newwin(1, 60, 2, 1)
        
        rectangle(self.stdscr, 1, 0, 3, 62)
        self.stdscr.refresh()

        box = Textbox(add_stdscr)
        box.stripspaces = True
        box.edit()

        return box.gather()[:-1]