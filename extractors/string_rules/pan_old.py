'''
Rule-based method to extract Old PAN Card
using the OCR'ed output string.

Card format:
https://swarajyamag.com/insta/only-half-of-issued-pan-cards-linked-to-aadhaar-despite-31-march-deadline-says-income-tax-department
'''

import re
from .str_utils import fix_date, remove_non_ascii, remove_non_numerals, remove_non_letters

HEADER_WORDS = 'INCOME|TAX|DEPART|GOVT|INDIA'
HINDI_HEADER_WORDS = 'आयकर|विभाग|भारत|सरकार'
PAN_WORDS_EXACT = 'PERMANENT|ACCOUNT|NUMBER' # OCR is not always perfect, hence approx it by:
PAN_WORDS = 'PERM|COUNT|NUMB'
DOB_REGEX = r'(\d+[|/!)]\d+.?\d\d\d+)'

def parse_lossy_from_hindi_header(line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    
    while line_i < n_lines and not re.findall(HINDI_HEADER_WORDS, lines[line_i]):
        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to find hindi header')
        return backtrack_line_i
    
    # Assume it might be a line or two after Hindi header
    line_i += 2
    if line_i >= n_lines:
        return backtrack_line_i
    
    result['en']['name'] = remove_non_ascii(lines[line_i])
    line_i += 1
    if line_i >= n_lines:
        return backtrack_line_i
    
    result['en']['relation'] = remove_non_ascii(lines[line_i])
    return line_i+1

def parse_names_lossy(line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    
    # Try to find PAN row. If successful, backing up by 3 lines should give name hopefully
    while line_i < n_lines and not re.findall(PAN_WORDS, lines[line_i].upper()):
        line_i += 1
    
    if line_i >= n_lines:
        # Try to find DoB. If successful, backing up by 2 lines should give name hopefully
        line_i = backtrack_line_i
        while line_i < n_lines and not re.findall(DOB_REGEX, lines[line_i].upper()):
            line_i += 1
        if line_i >= n_lines:
            return parse_lossy_from_hindi_header(backtrack_line_i, lines, n_lines, result)
        else:
            line_i -= 2
    else:
        line_i -= 3
    
    if line_i < 0:
        return parse_lossy_from_hindi_header(backtrack_line_i, lines, n_lines, result)
    
    name = remove_non_ascii(lines[line_i])
    if len(remove_non_letters(name)) < 4:
        return backtrack_line_i
    result['en']['name'] = name
    result['en']['relation'] = remove_non_ascii(lines[line_i+1])
    result['logs'].append('The person names MAYbe wrong')
    return line_i+2

def parse_names(line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    
    ## -- EXTRACT ENGLISH NAME -- #
    while line_i < n_lines and not re.findall(HEADER_WORDS, lines[line_i].upper()):
        line_i += 1
    line_i += 1
    
    # The Header Words can be split across multiple lines.
    # So skip them all (including 'Satymeva Jayate' if present)
    while line_i < n_lines and (re.findall(HEADER_WORDS, lines[line_i].upper()) or len(remove_non_letters(lines[line_i].replace(' ', ''))) < 4):
        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to find header')
        return parse_names_lossy(backtrack_line_i, lines, n_lines, result)
    
    # Patch: Sometimes, New PAN is wrongly classified as old
    if re.findall(PAN_WORDS_EXACT, lines[line_i].upper()):
        result['logs'].append('Probably PAN was wrongly classified as old')
        return backtrack_line_i
    
    result['en']['name'] = remove_non_ascii(lines[line_i])
    line_i += 1
    
    # Sometimes it also detects the 'Bharat Sarkar' watermark in the right
    # So try to skip that
    while line_i < n_lines and len(remove_non_letters(lines[line_i].replace(' ', ''))) < 3:
        line_i += 1
    
    ## -- EXTRACT PARENT NAME -- #
    if line_i >= n_lines:
        result['logs'].append('Failed to find parent name')
        return line_i-1
    
    result['en']['relation'] = remove_non_ascii(lines[line_i])
    line_i += 1
    
    # Sometimes it also detects the 'Bharat Sarkar' watermark in the right
    # So try to skip that
    while line_i < n_lines and not remove_non_ascii(lines[line_i].replace(' ', '')):
        line_i += 1
    
    return line_i

def parse_dob(line_i, lines, n_lines, result):
    ## -- EXTRACT DOB -- #
    if line_i >= n_lines:
        result['logs'].append('Failed to find DOB')
        return line_i
    
    # Sometimes DOB is not detected, hence reaches next line.
    if re.findall(PAN_WORDS, lines[line_i].upper()):
        result['logs'].append('Detector probably failed to detect DoB')
        return line_i
    
    result['en']['dob'] = lines[line_i]
    # Sometimes DOB can be corrupt, also try checking for exact results
    matches = re.findall(DOB_REGEX, result['en']['dob'])
    if matches:
        result['en']['dob'] = matches[0]
    else:
        # Search till we find the exact date pattern
        tmp_line_i = line_i
        while not matches:
            tmp_line_i += 1
            if tmp_line_i >= n_lines: break
            matches = re.findall(DOB_REGEX, lines[tmp_line_i])
        
        if tmp_line_i >= n_lines or not matches:
            result['logs'].append('Exact DOB not matched')
            if len(remove_non_numerals(result['en']['dob'])) > 4:
                # Ensure atleast 4 numbers are there
                return line_i+1
            else:
                del result['en']['dob']
                return line_i
        
        line_i = tmp_line_i
        result['en']['dob'] = matches[0]
    line_i += 1
    return line_i

def parse_id_lossy(line_i, lines, n_lines, result):
    if 'dob' not in result['en']:
        return line_i
    
    if re.findall(DOB_REGEX, fix_date(result['en']['dob'])):
        # If DoB was properly extracted properly,
        # we may assume we are in the PAN line,
        # and hope that next line contains the ID
        if line_i+1 < n_lines:
            pan_id = remove_non_ascii(lines[line_i+1].replace(' ', ''))
            if len(pan_id) < 7 and line_i+2 < n_lines:
                # Worst case, get next line
                pan_id = remove_non_ascii(lines[line_i+2].replace(' ', ''))
            if len(pan_id) > 7:
                result['en']['id'] = pan_id
                result['logs'].append('Approximately extracted ID')
                return line_i+2
    
    return line_i

def parse_id(line_i, lines, n_lines, result):
    ## -- EXTRACT ID -- #
    if line_i >= n_lines:
        result['logs'].append('Failed to find ID')
        return line_i
    
    backtrack_line_i = line_i
    # Search for parts of 'PERMANENT ACCOUNT NUMBER'
    while line_i < n_lines and not re.findall(PAN_WORDS, lines[line_i].upper()):
        line_i += 1
    line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to find ID using normal method')
        # Try regex
        line_i = backtrack_line_i
        exact_regex_pattern = r'[A-Z][A-Z][A-Z][A-Z][A-Z]\d\d\d\d[A-Z]' # Fails when bad OCR
        regex_pattern = r'[A-Z][A-Z][A-Z][A-Z]\w\d\d\d\d\w?'
        noisy_regex_pattern = r'\w{10}'
        matches = re.findall(regex_pattern, lines[line_i].replace(' ', ''))
        while not matches:
            line_i += 1
            if line_i >= n_lines: break
            matches = re.findall(regex_pattern, lines[line_i].replace(' ', ''))
        
        if line_i >= n_lines or not matches:
            result['logs'].append('Unable to parse ID using regex')
            return parse_id_lossy(backtrack_line_i, lines, n_lines, result)
        else:
            result['en']['id'] = matches[0]
    else:
        result['en']['id'] = lines[line_i]
        
        # Patch: Find DoB if we failed to find it eariler
        if 'dob' not in result['en'] and line_i-2 >= 0 and len(remove_non_numerals(lines[line_i-2])) >= 6:
            result['en']['dob'] = lines[line_i-2]
    
    line_i += 1
    return line_i

def get_values(full_str, lang='hi'):
    lines = full_str.split('\n')
    line_i, n_lines = 0, len(lines)

    result = {'en': {}, 'logs': []}
    
    line_i = parse_names(line_i, lines, n_lines, result)
    
    # Note: Company PAN cards don't have parent's name
    # So if there is date in that field, make it as DoB
    if 'relation' in result['en'] and re.findall(DOB_REGEX, result['en']['relation']):
        result['en']['dob'] = result['en']['relation']
        del result['en']['relation']
    else:
        line_i = parse_dob(line_i, lines, n_lines, result)
    line_i = parse_id(line_i, lines, n_lines, result)
    
    return result
