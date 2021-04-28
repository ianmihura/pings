import sys,os
import argparse
import curses

import screen
import i18n
import profile
import README

def main():
    # Get parsed arguements
    parser = argparse.ArgumentParser()
    parser.add_argument('-ips', type=str, help=i18n.ARGS_HELP_IPS)
    parser.add_argument('-p', '--profile', type=str, help=i18n.ARGS_HELP_PROFILE)
    parser.add_argument('-r', '--readme', action="store_true", help=i18n.ARGS_HELP_README)
    parser.add_argument('-s', '--show', action="store_true", help=i18n.ARGS_HELP_SHOW_PROFILES)

    profile.check_profiles()
    args = parser.parse_args()
    raw_ips = []
    raw_ips_names = []
    
    if args.readme:
        print(README.text)

    elif args.show:
        (profile_names, profile_content) = profile.get_all_profiles()
        print(i18n.SHOW_PROFILES_TITLE.format(profile.IPS_PROFILES_PATH))
        for i, p in enumerate(profile_names):
            print(i18n.SHOW_PROFILE.format(profile_names[i], profile_content[i]))
    
    else:
        # Enter via ips
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