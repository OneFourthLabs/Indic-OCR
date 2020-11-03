'''
Rule-based method to extract Old PAN Card
using the OCR'ed output string.

Card format:
https://swarajyamag.com/insta/only-half-of-issued-pan-cards-linked-to-aadhaar-despite-31-march-deadline-says-income-tax-department
'''

import re

def parse_names(line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    
    ## -- EXTRACT ENGLISH NAME -- #
    while line_i < n_lines and not 'GOVT' in lines[line_i].upper() and not 'INDIA' in lines[line_i].upper():
        line_i += 1
    line_i += 1
    if line_i >= n_lines:
        result['logs'].append('Failed to find name')
        return backtrack_line_i
    
    result['en']['name'] = lines[line_i]
    line_i += 1
    
    ## -- EXTRACT PARENT NAME -- #
    if line_i >= n_lines:
        result['logs'].append('Failed to find parent name')
        return line_i-1
    
    result['en']['relation'] = lines[line_i]
    line_i += 1
    return line_i

def parse_dob(line_i, lines, n_lines, result):
    ## -- EXTRACT DOB -- #
    if line_i >= n_lines:
        result['logs'].append('Failed to find DOB')
        return line_i
    
    result['en']['dob'] = lines[line_i]
    # Sometimes DOB can be corrupt, also try checking for exact results
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
            return line_i
        
        line_i = tmp_line_i
        result['en']['dob'] = matches[0]

    line_i += 1
    return line_i

def parse_id(line_i, lines, n_lines, result):
    ## -- EXTRACT ID -- #
    if line_i >= n_lines:
        result['logs'].append('Failed to find ID')
        return line_i
    
    backtrack_line_i = line_i
    # Search for parts of 'PERMANENT ACCOUNT NUMBER'
    while line_i < n_lines and not 'COUNT' in lines[line_i].upper() and not 'NUMB' in lines[line_i].upper():
        line_i += 1
    line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to find ID using normal method')
        # Try regex
        line_i = backtrack_line_i
        exact_regex_pattern = r'[A-Z][A-Z][A-Z][A-Z][A-Z]\d\d\d\d[A-Z]' # Fails when bad OCR
        regex_pattern = r'[A-Z][A-Z][A-Z][A-Z]\w\d\d\d\d\w'
        noisy_regex_pattern = r'\w{10}'
        matches = re.findall(regex_pattern, lines[line_i])
        while not matches:
            line_i += 1
            if line_i >= n_lines: break
            matches = re.findall(regex_pattern, lines[line_i])
        
        if line_i >= n_lines or not matches:
            result['logs'].append('Unable to parse ID using regex')
        else:
            result['en']['id'] = matches[0]
    else:
        result['en']['id'] = lines[line_i]
    
    line_i += 1
    return line_i

def get_values(full_str, lang='hi'):
    lines = full_str.split('\n')
    line_i, n_lines = 0, len(lines)

    result = {'en': {}, 'logs': []}
    
    line_i = parse_names(line_i, lines, n_lines, result)
    line_i = parse_dob(line_i, lines, n_lines, result)
    line_i = parse_id(line_i, lines, n_lines, result)
    
    return result
