import sys,os

import i18n

def parse_file(file):
    if not os.path.isfile(file):
       print("File path {} does not exist. Exiting...".format(file))
       sys.exit()
    
    try:
        f = open(file, 'r')
        raw_ips = f.readline().split(',')
        raw_ips_names = f.readline().split(',')
        f.close()
        return (raw_ips, raw_ips_names)

    except:
        print('Unable to access file {}'.format(file))

def save_file(file_path, current_file_path, ips):
    result = ''
    if file_path: result = _save_file(file_path, ips, False)
    else:
        if current_file_path: result = _save_file(current_file_path, ips, True)
        else: result = i18n.SAVE_FILE_PATH_NOT_PRESENT
    return result

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

        if is_overwrite: result = i18n.SAVE_FILE_SUCCESS_OVERWRITE.format(file_path)
        else: result = i18n.SAVE_FILE_SUCCESS_NEW.format(file_path)

    except:
        result = i18n.SAVE_FILE_UNABLE_ACCESS.format(file_path)

    return result

def _parse_ips(ips):
    parsed_ips = ''
    parsed_names = ''
    for ip in ips:
        parsed_ips += ip + ','
        parsed_names += ips[ip].get_name() + ','
    return (parsed_ips[:-1], parsed_names[:-1])