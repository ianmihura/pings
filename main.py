import sys,os
import argparse
import curses

import screen
import i18n

def main():
    # Get parsed arguements
    parser = argparse.ArgumentParser()
    parser.add_argument('-ips', type=str, help=i18n.ARGS_HELP_IPS)
    # parser.add_argument('-f', '--file', type=str, help=i18n.ARGS_HELP_FILE)
    # parser.add_argument('-s', '--separator', type=str, help=i18n.ARGS_HELP_FILE_SEPARATOR)

    args = parser.parse_args()
    raw_ips = []
    
    if (args.ips):
        raw_ips = args.ips.split(',')

    # File parser
    # if (args.file):
    #     print(args.file)

    #     if (args.separator):
    #         print(args.separator)

    # Start main curses loop
    curses.wrapper(screen.init_curses, raw_ips)

if __name__ == '__main__':
    main()