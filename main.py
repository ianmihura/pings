import argparse
import sys,os
import curses
import time

import ip

has_curses = False
ips = ip.IPs()
futures = []

# Initialize curses screen
# stdscr = curses.initscr()
    
def init_curses(stdscr):

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # # Disable default echo function
    # curses.noecho()
    # # Disable buffering input : no ENTER key needed for input
    # curses.cbreak()
    # # Enable keypad mode
    # stdscr.keypad(True)

    # Init drawing loop
    k = 0
    stdscr.clear()

    while True:
        
        # Rendering some text
        stdscr.addstr(0, 0, 'Pinging your ips:')

        # print(str(len(ips.ips)))

        # Refresh the screen
        stdscr.refresh()

        i = 2
        for ip_id in ips.ips:
            i += 1
            ip = ips.ips[ip_id]
            ip.ping()
            stdscr.addstr(i, 0, ip.get_result())

        time.sleep(1)

        # Wait for next input
        # k = stdscr.getch()

def main():
    # Get parsed arguements
    parser = argparse.ArgumentParser()
    parser.add_argument('ips', type=str, help='List of IP addresses to ping, separated by a comma. Example 8.8.8.8,4.4.4.4')
    args = parser.parse_args()

    processes = []

    # Init all ips
    for ip in args.ips.split(','):
        ip = ips.add_ip(ip)
    
    # Start main curses loop
    curses.wrapper(init_curses)

if __name__ == '__main__':
    main()