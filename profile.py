import sys,os
import i18n

IPS_PROFILES_PATH = os.getenv('APPDATA') + '\\ips\\profiles'

def get_profile_path(profile):
    return IPS_PROFILES_PATH + "\\" + profile

def check_profiles():
    if not os.path.isdir(IPS_PROFILES_PATH):
        os.makedirs(IPS_PROFILES_PATH)

def get_ips_from_profile(profile):
    profile_path = get_profile_path(profile)
    
    if not os.path.isfile(profile_path):
        print(i18n.PROFILE_NOT_EXISTS.format(profile))
        sys.exit()

    return _parse_file(profile_path)

def _parse_file(file_path):
    raw_ips = raw_ips_names = []

    try:
        f = open(file_path, 'r')
        raw_ips = f.readline().split(',')
        raw_ips_names = f.readline().split(',')
        f.close()

    except:
        print(i18n.FILE_UNABLE_ACCESS.format(file_path))
    
    return (raw_ips, raw_ips_names)

def save_profile(profile, current_profile, ips):
    file_path = get_profile_path(profile)
    current_file_path = get_profile_path(current_profile)

    if file_path: 
        return (_save_file(file_path, ips, False), profile)
    else:
        if current_file_path: 
            return (_save_file(current_file_path, ips, True), current_file_path)
        else:
            return (i18n.FILE_PATH_NOT_PRESENT, '')

def _save_file(file_path, ips, is_overwrite):
    result = ''
    w_ips, w_ips_names = _parse_ips(ips)

    try:
        f = open(file_path, 'w')
        f.truncate(0)
        f.write(w_ips)
        f.write('\n')
        f.write(w_ips_names)
        f.close()

        if is_overwrite: result = i18n.SAVE_PROFILE_SUCCESS_OVERWRITE.format(file_path)
        else: result = i18n.SAVE_PROFILE_SUCCESS_NEW.format(file_path)

    except:
        result = i18n.FILE_UNABLE_ACCESS.format(file_path)

    return result

def _parse_ips(ips):
    parsed_ips = ''
    parsed_names = ''
    for ip in ips:
        parsed_ips += ip + ','
        parsed_names += ips[ip].get_name() + ','
    return (parsed_ips[:-1], parsed_names[:-1])