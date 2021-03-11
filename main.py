import sys,os
import argparse
import curses

import screen
import i18n
import xfile

def main():
    # Get parsed arguements
    parser = argparse.ArgumentParser()
    parser.add_argument('-ips', type=str, help=i18n.ARGS_HELP_IPS)
    parser.add_argument('-f', '--file', type=str, help=i18n.ARGS_HELP_FILE)

    args = parser.parse_args()
    raw_ips = []
    raw_ips_names = []
    
    # Enter via args
    if (args.ips):
        raw_ips = args.ips.split(',')
        raw_ips_names = [''] * len(raw_ips)

    # Enter via file
    elif (args.file): 
        (raw_ips, raw_ips_names) = xfile.parse_file(args.file)
        screen.screen.set_current_file_path(args.file)

    # Start main curses loop
    curses.wrapper(screen.init_curses, raw_ips, raw_ips_names)

if __name__ == '__main__':
    main()