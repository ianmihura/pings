import sys,os
import argparse
import curses

import screen
import i18n

def main():
    # Get parsed arguements
    parser = argparse.ArgumentParser()
    parser.add_argument('-ips', type=str, help=i18n.ARGS_HELP_IPS)
    parser.add_argument('-f', '--file', type=str, help=i18n.ARGS_HELP_FILE)

    args = parser.parse_args()
    raw_ips = []
    
    if (args.ips):
        raw_ips += args.ips.split(',')

    if (args.file):
        raw_ips += parse_file(args.file)

    # Start main curses loop
    curses.wrapper(screen.init_curses, raw_ips)

def parse_file(file):
    if not os.path.isfile(file):
       print("File path {} does not exist. Exiting...".format(file))
       sys.exit()

    try:
        f = open(file, 'r')
        raw_ips = f.readline().split(',')
        f.close()
        return raw_ips

    except:
        print('Unable to access file {}'.format(file))

if __name__ == '__main__':
    main()