'''
Rule-based method to extract details from Aadhar card Front side
using the full output string from OCR

Card formats:

Hindi:
With DOB: https://blog.pixlab.io/2020/03/full-scan-support-for-india-aadhar-id-card
With YoB: https://in.pinterest.com/pin/455919162248327710


Tamil: http://puthiyakuralgal.blogspot.com/2015/04/plastic-aadhaar-cards-at-rs30.html
Bangla: http://www.ekhansangbad.com/archives/21857
'''

import re

key_map = {
    'ta': {
        'dob': 'பிறந்த நாள்',
        'yob': 'பிறந்த வருடம்'
    },
    'hi': {
        'dob': 'जन्म तिथि',
        'yob': 'जन्म वर्ष'
    }
}

value_map = {
    'ta': {
        'Male': 'ஆண்‌',
        'Female': 'பெண்',
    },
    'hi': {
        'Male': 'पुरुष',
        'Female': 'महिला'
    }
}

def parse_name(lang, line_i, lines, n_lines, result):
    # Search for the string 'GOVERNMENT OF INDIA'
    backtrack_line_i = line_i
    while line_i < n_lines \
        and 'GOVERN' not in lines[line_i].upper() \
        and 'INDIA' not in lines[line_i].upper():

        line_i += 1
    
    if line_i < n_lines:
        # Hopefully, the next 2 lines contain English and regional name
        line_i += 1
        if line_i >= n_lines:
            result['logs'].append('Failed to find English name')
            return backtrack_line_i
        result['en']['name'] = lines[line_i].strip()

        line_i += 1
        if line_i >= n_lines:
            result['logs'].append('Failed to find Regional name')
            return line_i
        result[lang]['name'] = lines[line_i].strip()
        return line_i+1
    
    result['logs'].append('Failed to find Aadhar header')

    # Try to find the DOB line and back up by 2 lines
    line_i = backtrack_line_i
    while line_i < n_lines \
        and 'DOB' not in lines[line_i].upper() \
        and 'YEAR' not in lines[line_i].upper() \
        and 'YOB' not in lines[line_i].upper():

        line_i += 1
    
    if line_i < n_lines:
        # Hopefully, the prev 2 lines contain English and regional name
        line_i -= 2
        result['en']['name'] = lines[line_i].strip()
        line_i += 1
        result[lang]['name'] = lines[line_i].strip()
        return line_i+1

    # Try to find the DOB line and back up by 3 lines
    line_i = backtrack_line_i
    while line_i < n_lines \
        and 'MALE' not in lines[line_i].upper():

        line_i += 1
    
    if line_i < n_lines:
        # Hopefully, the prev 3 lines contain English and regional name
        line_i -= 3
        result['en']['name'] = lines[line_i].strip()
        line_i += 1
        result[lang]['name'] = lines[line_i].strip()
        return line_i+1
    
    result['logs'].append('Failed to find name')
    return backtrack_line_i

def parse_dob_using_regex(lang, line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    dob_regex = r'(\d+/\d+/\d+)'
    while line_i < n_lines \
        and not re.findall(dob_regex, lines[line_i]):

        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to get DoB using regex')
        return backtrack_line_i
    
    result['en']['dob'] = re.findall(dob_regex, lines[line_i])[0]
    return line_i+1

def parse_dob_using_key(lang, line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    regional_key = key_map[lang]['dob']

    while line_i < n_lines \
        and 'DOB' not in lines[line_i].upper() \
        and 'DATE' not in lines[line_i].upper() \
        and regional_key not in lines[line_i]:

        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to read DoB')
        return backtrack_line_i
    
    # If parse_dob_using_regex() has failed, it means
    # DOB is corrupted. Extract as much as possible

    dob = lines[line_i]
    if ':' in dob:
        dob = dob.split(':')[1]
    else:
        # What else can we do?
        dob = dob.replace(regional_key, '').replace('DOB', '')
        if dob.startswith('/'):
            dob = dob[1:]
    
    result['en']['dob'] = dob.strip()
    return line_i+1

def parse_yob_using_key(lang, line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    regional_key = key_map[lang]['yob']

    while line_i < n_lines \
        and 'YOB' not in lines[line_i].upper() \
        and 'YEAR' not in lines[line_i].upper() \
        and regional_key not in lines[line_i]:

        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to find YoB')
        return backtrack_line_i
    
    year_regex = '\\d\\d\\d\\d'
    matches = re.findall(year_regex, lines[line_i])
    if matches:
        result['en']['yob'] = matches[0]
    else:
        result['logs'].append('YOB is corrupt')
    
    return line_i+1

def parse_dob(lang, line_i, lines, n_lines, result):

    tmp_line_i = parse_dob_using_regex(lang, line_i, lines, n_lines, result)
    if tmp_line_i > line_i:
        # Success
        return tmp_line_i

    # Find the line which has DOB
    tmp_line_i = parse_dob_using_key(lang, line_i, lines, n_lines, result)
    if tmp_line_i > line_i:
        # Success
        return tmp_line_i
    
    # What if it is Year of Birth?
    tmp_line_i = parse_yob_using_key(lang, line_i, lines, n_lines, result)
    if tmp_line_i > line_i:
        # Success
        return tmp_line_i
    
    return line_i

def parse_gender(lang, line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    # Assumes 2 genders
    while line_i < n_lines \
        and 'MALE' not in lines[line_i].upper():

        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to find gender')
        return backtrack_line_i
    
    gender = 'Female' if 'FEMALE' in lines[line_i].upper() else 'Male'
    result['en']['gender'] = gender
    result[lang]['gender'] = value_map[lang][gender]

    return line_i+1

def parse_id(line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    id_regex = r'(\d+ \d+ \d+)'
    while line_i < n_lines \
        and not re.findall(id_regex, lines[line_i]):

        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to parse ID')
        return backtrack_line_i
    
    result['en']['id'] = re.findall(id_regex, lines[line_i])[0]
    return line_i+1


def get_values(full_str, lang):
    lines = full_str.split('\n')
    line_i, n_lines = 0, len(lines)

    result = {'en': {}, lang: {}, 'logs': []}

    line_i = parse_name(lang, line_i, lines, n_lines, result)
    line_i = parse_dob(lang, line_i, lines, n_lines, result)
    line_i = parse_gender(lang, line_i, lines, n_lines, result)

    line_i = parse_id(line_i, lines, n_lines, result)

    return result
