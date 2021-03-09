import sys,os

import i18n

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

def save_file(file_path, current_file_path, ips):
    result = ''
    if file_path:
        result = _save_file(file_path, ips)
    else:
        if current_file_path:
            result = _save_file(current_file_path, ips)
        else:
            result = i18n.SAVE_FILE_PATH_NOT_PRESENT
    return result

def _save_file(file_path, ips):
    result = ''
    w_ips = _parse_ips(ips)

    try:
        f = open(file_path, 'w')
        f.truncate(0)
        f.write(w_ips)
        f.close()
        result = i18n.SAVE_FILE_SUCCESS
        
    except:
        result = i18n.SAVE_FILE_UNABLE_ACCESS.format(file_path)

    return result

def _parse_ips(ips):
    parsed_ips = ''
    for ip in ips:
        parsed_ips += ip + ','
    return parsed_ips[:-1]