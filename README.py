# pings

Is a python program that helps you ping a list of IP addresses, or a subnet.

You can add aliases to the IPs to identify them easily, make lists and saved your preferences to profiles in %appdata% (originally developed for Windows environment).

Flags
    [null]
        Start pings with no IPs loaded
    -ips x.x.x.x/x
        Start pings with an IP or a range of IPs [/x]
        You can also separate different IPs with commas
        x.x.x.x/x,x.x.x.x/x
    -p profile_name
        Start pings with a saved profile
        Default saves to %appdata%
    -s
        Shows profiles available
        Default to %appdata%
    -r
        Shows README file
    -h
        Get help for flags
    
Keyboard shortcuts
    Navigation
        UP/DOWN arrows
            Select next IP
        LEFT/RIGHT arrows
            Next page (scrolls one full screen length)
    Profile
        s
            Save current config as profile
            Will suggest to overwrite
    IPs
        a
            Add IP or range of IPs
        x
            Delete selected IP
        n
            Add/change name of selected IP
        t
            Hide/show timeout IPs
            Paging & scrolling may feel awkward
    General config
        r
            Sleeps for 3 seconds - Refresh
        h
            Show help
        p
            Change ping frecuency
        q
            Peacefully quits
            Will ask if you want to save changes if its working with a profile
            Will save changes ONLY IF you type in y or yes [Y or YES]"""
