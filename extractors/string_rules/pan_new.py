'''
Rule-based method to extract information from
latest PAN card using full output string from OCR.

Card format:
https://www.pancardapp.com/blog/what-is-pan-card/
'''

import re

def parse_id(line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    # Search for a word in "Permanent Account Number Card",
    # belown which we can find the ID
    while line_i < n_lines \
        and 'permanent' not in lines[line_i].lower() \
        and 'account' not in lines[line_i].lower() \
        and 'number' not in lines[line_i].lower():

        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Unable to find PAN header')
        return backtrack_line_i

    # Hoping the ID will be in the next line
    line_i += 1
    result['en']['id'] = lines[line_i]
    backtrack_line_i = line_i

    # Parse out the ID pattern
    exact_regex_pattern = r'[A-Z][A-Z][A-Z][A-Z][A-Z]\d\d\d\d[A-Z]' # Fails when bad OCR
    regex_pattern = r'[A-Z][A-Z][A-Z][A-Z]\w\d\d\d\d\w'
    noisy_regex_pattern = r'\w{10}'

    matches = re.findall(regex_pattern, lines[line_i])
    while not matches:
        line_i += 1
        if line_i >= n_lines: break
        matches = re.findall(regex_pattern, lines[line_i])
    
    if line_i >= n_lines or not matches:
        result['logs'].append('Unable to parse exact ID using regex')
        return backtrack_line_i
    else:
        result['en']['id'] = matches[0]
    
    return line_i

def parse_name(line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    # Search for a word in "नाम / Name",
    # belown which we can find the name

    # Also stop searching when you reach the next line (parent's name)
    disallowed_words = 'parent|father|mother|husband|पिता|माता|पति'
    
    while line_i < n_lines \
        and 'name' not in lines[line_i].lower() \
        and 'नाम' not in lines[line_i].lower() \
        and not re.findall(disallowed_words, lines[line_i].lower()):
        
        line_i += 1
    
    if line_i >= n_lines or re.findall(disallowed_words, lines[line_i].lower()):
        result['logs'].append('Unable to find PAN holder name')
        return backtrack_line_i
    
    # Hoping the name will be in the next line
    line_i += 1
    result['en']['name'] = lines[line_i]
    return line_i

def parse_relation_name(line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    keys = 'parent|father|mother|husband|पिता|माता|पति'

    while line_i < n_lines \
        and not re.findall(keys, lines[line_i].lower()):

        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Unable to find relation name')
        return backtrack_line_i
    
    # Hoping the name will be in the next line
    line_i += 1
    result['en']['relation'] = lines[line_i]
    return line_i

def parse_dob(line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    # Search for "जन्म की तारीख / Date of Birth"
    # But the DoB key can be in next line, so better search for that alone
    
    while line_i < n_lines \
        and 'date' not in lines[line_i].lower() \
        and 'birth' not in lines[line_i].lower():

        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Unable to find DoB key')
        line_i = backtrack_line_i
    else:
        # Hoping it will be there in next line
        line_i += 1
        result['en']['dob'] = lines[line_i]
    
    # Parse using pattern
    dob_regex = r'(\d+/\d+/\d+)'
    matches = re.findall(dob_regex, result['en']['dob'])
    if matches:
        result['en']['dob'] = matches[0]
    else:
        # Search till we find the exact date pattern
        tmp_line_i = line_i
        while not matches:
            tmp_line_i += 1
            if tmp_line_i >= n_lines: break
            matches = re.findall(dob_regex, lines[tmp_line_i])
        
        if tmp_line_i >= n_lines or not matches:
            result['logs'].append('Exact DOB not matched')
        else:
            result['en']['dob'] = matches[0]
            line_i = tmp_line_i + 1
    
    return line_i

def get_values(full_str, lang='hi'):
    lines = full_str.split('\n')
    line_i, n_lines = 0, len(lines)

    result = {'en': {}, 'logs': []}

    line_i = parse_id(line_i, lines, n_lines, result)
    line_i = parse_name(line_i, lines, n_lines, result)
    line_i = parse_relation_name(line_i, lines, n_lines, result)
    line_i = parse_dob(line_i, lines, n_lines, result)

    return result
