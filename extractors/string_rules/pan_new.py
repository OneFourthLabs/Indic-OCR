'''
Rule-based method to extract information from
latest PAN card using full output string from OCR.

Card format:
https://www.pancardapp.com/blog/what-is-pan-card/

TODO: Support Business e-PAN format:
https://ibb.co/TbYWSnD
'''

import re
from .str_utils import remove_non_ascii, remove_non_letters, remove_non_numerals, remove_non_alphanumerics

RELATION_KEYS = '[fpr]ath[eo]r|mother|husband|पिता|माता|पति'
GOV_HEADER_KEYS = 'income|tax|department|govt|india'
NAME_KEYS = 'name|नाम'
PAN_KEYS = 'permanent|account|number|card'
PAN_HINDI_KEYS = 'स्थायी|लेखा|संख्या|कार्ड'
DOB_KEYS = 'date|birth|जन्म|तारीख'
DOB_REGEX = r'(\d{1,2}[|1!/-]\d+.?\d\d\d+)'

def parse_id(line_i, lines, n_lines, result):
    backtrack_line_i = line_i
    # Search for a word in "Permanent Account Number Card",
    # belown which we can find the ID
    while line_i < n_lines and not re.findall(PAN_KEYS, lines[line_i].lower()):
        line_i += 1
    
    if line_i < n_lines:
        # Hoping the ID will be in the next line
        line_i += 1
        if line_i >= n_lines:
            result['logs'].append('Unable to find ID after PAN key')
            return backtrack_line_i
    else:
        result['logs'].append('Unable to find PAN header')

        # Try to find 'INCOME TAX DEPARTMENT' / 'GOVT. OF INDIA'
        line_i = backtrack_line_i

        while line_i < n_lines and not re.findall(GOV_HEADER_KEYS, lines[line_i].lower()):
            line_i += 1
        
        if line_i >= n_lines:
            # Try to find Hindi PAN header
            line_i = backtrack_line_i
            while line_i < n_lines and not re.findall(PAN_HINDI_KEYS, lines[line_i].lower()):
                line_i += 1
            
            if line_i >= n_lines:
                return backtrack_line_i
            else:
                # Hoping the ID will be 2 lines below the "Sthayi Lekha" line
                line_i += 2
                if line_i >= n_lines:
                    return backtrack_line_i
                result['logs'].append('WARN: ID MAYbe wrong')
        else:
            # Hoping the ID will be 3 lines below the "ITD GoI" line
            line_i += 3
            if line_i >= n_lines:
                return backtrack_line_i
            result['logs'].append('WARN: ID MAYbe wrong')
    
    result['en']['id'] = lines[line_i].replace(' ', '')
    if len(remove_non_alphanumerics(result['en']['id'])) < 5 and line_i+1 < n_lines:
        # Sometimes the 'Bharat Sarkar' watermark gets detected. Skip that if any
        result['en']['id'] = lines[line_i+1].replace(' ', '')
        
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
    # Search for a word in "नाम / Name", belown which we can find the name
    # Also stop searching when you reach the next line (parent's name)
    
    while line_i < n_lines \
        and not re.findall(NAME_KEYS, lines[line_i].lower()) \
        and not re.findall(RELATION_KEYS, lines[line_i].lower()):
        
        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Unable to find PAN holder name')
        return backtrack_line_i
    elif re.findall(RELATION_KEYS, lines[line_i].lower()):
        # It means that though we have failed to find the key 'name',
        # we have found the next key. So hope name is present in prev. line
        result['logs'].append('Warning: Name MAYbe wrong')
        line_i -= 1
        while line_i >= 0 and not remove_non_ascii(lines[line_i]):
            line_i -= 1
        
        if line_i < 0:
            return backtrack_line_i
    else:
        # Hoping the name will be in the next line
        line_i += 1
    
    result['en']['name'] = lines[line_i]
    return line_i+1

def parse_relation_name(line_i, lines, n_lines, result):
    if line_i >= n_lines:
        result['logs'].append('Error in processing relation name')
        return line_i
    backtrack_line_i = line_i

    while line_i < n_lines \
        and not re.findall(RELATION_KEYS, lines[line_i].lower()):

        line_i += 1
    
    if line_i >= n_lines:
        # Try to find based on 'name'
        if 'name' in result['en'] and re.findall(NAME_KEYS, lines[backtrack_line_i].lower()):
            # Hoping something like 'father' is corrupt, but 'name' is not
            line_i = backtrack_line_i
            result['logs'].append('Warning: Relation name MAYbe wrong')
        else:
            result['logs'].append('Unable to find relation name')
            return backtrack_line_i
    
    # Hoping the name will be in the next line
    line_i += 1
    result['en']['relation'] = lines[line_i]
    return line_i

def parse_dob(line_i, lines, n_lines, result):
    if line_i >= n_lines:
        result['logs'].append('Error in processing DoB')
        return line_i
    backtrack_line_i = line_i
    # Search for "जन्म की तारीख / Date of Birth"
    while line_i < n_lines and not re.findall(DOB_KEYS, lines[line_i].lower()):
        line_i += 1
    line_i += 1
    
    # Sometimes, the multilingual DoB can be in 2 lines.
    # So ensure that's skipped if any
    while line_i < n_lines and re.findall(DOB_KEYS, lines[line_i].lower()):
        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Unable to find DoB key')
        line_i = backtrack_line_i
    else:
        # Hoping it will be there in this line
        result['en']['dob'] = lines[line_i]
    
    # Parse using pattern
    matches = re.findall(DOB_REGEX, lines[line_i])
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
        else:
            result['en']['dob'] = matches[0]
            line_i = tmp_line_i
    
    # Patch: If we had failed to parent's name, try now
    if 'dob' in result['en'] and 'relation' not in result['en']:
        name = remove_non_ascii(lines[line_i-2]).strip()
        if not re.findall(DOB_KEYS, name.lower()) and len(remove_non_letters(name)) > 4:
            result['en']['relation'] = name
            result['logs'].append('Relation name MAYbe wrong')
            if 'name' not in result['en'] or name == result['en']['name'].strip():
                # In-case we wrongly or didn't parse name, try to fix that too
                if 'name' in result['en']:
                    del result['en']['name']
                
                if line_i-4 > 0:
                    name = remove_non_ascii(lines[line_i-4]).strip()
                    if len(remove_non_letters(name)) > 4:
                        result['en']['name'] = name
                        if 'id' in result['en'] and name == result['en']['id'].strip():
                            # If in case we went too far
                            del result['en']['name']
                        else:
                            result['logs'].append('Name MAYbe wrong')
    
    # Fix DoB
    if 'dob' in result['en'] and len(remove_non_numerals(result['en']['dob'])) < 6:
        del result['en']['dob']
        # Find if it's broken but present in next line
        if line_i+1 < n_lines and len(remove_non_numerals(lines[line_i+1])) > 5:
            result['en']['dob'] = lines[line_i+1]
    
    return line_i+1

def get_values(full_str, lang='hi'):
    lines = full_str.split('\n')
    line_i, n_lines = 0, len(lines)

    result = {'en': {}, 'logs': []}

    line_i = parse_id(line_i, lines, n_lines, result)
    line_i = parse_name(line_i, lines, n_lines, result)
    line_i = parse_relation_name(line_i, lines, n_lines, result)
    line_i = parse_dob(line_i, lines, n_lines, result)

    return result
