import sys,os
import argparse
import curses

import screen
import i18n
import profile

def main():
    # Get parsed arguements
    parser = argparse.ArgumentParser()
    parser.add_argument('-ips', type=str, help=i18n.ARGS_HELP_IPS)
    parser.add_argument('-p', '--profile', type=str, help=i18n.ARGS_HELP_PROFILE)

    profile.check_profiles()
    args = parser.parse_args()
    raw_ips = []
    raw_ips_names = []
    
    # Enter via args
    if args.ips:
        raw_ips = args.ips.split(',')
        raw_ips_names = [''] * len(raw_ips)

    # Enter via profile
    elif args.profile:
        (raw_ips, raw_ips_names) = profile.get_ips_from_profile(args.profile)
        screen.screen.set_current_profile(args.profile)

    # Start main curses loop
    curses.wrapper(screen.init_curses, raw_ips, raw_ips_names)

if __name__ == '__main__':
    main()