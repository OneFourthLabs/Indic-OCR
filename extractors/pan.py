import re

def get_values(full_str, lang='hi'):
    lines = full_str.split('\n')
    line_i, n_lines = 0, len(lines)
    result = {'en': {}}
    
    ## -- EXTRACT ENGLISH NAME -- #
    while line_i < n_lines and not 'GOVT' in lines[line_i].upper() and not 'INDIA' in lines[line_i].upper():
        line_i += 1
    line_i += 1
    if line_i >= n_lines:
        print('Failed to find name')
        return result
    
    result['en']['name'] = lines[line_i]
    line_i += 1
    
    ## -- EXTRACT PARENT NAME -- #
    if line_i >= n_lines:
        print('Failed to find parent name')
        return result
    
    result['en']['parent'] = lines[line_i]
    line_i += 1
    
    ## -- EXTRACT DOB -- #
    if line_i >= n_lines:
        print('Failed to find DOB')
        return result
    
    result['en']['dob'] = lines[line_i]
    line_i += 1
    
    ## -- EXTRACT ID -- #
    while line_i < n_lines and not 'ACCOUNT' in lines[line_i].upper() and not 'NUMBER' in lines[line_i].upper():
        line_i += 1
    line_i += 1
    if line_i >= n_lines:
        print('Failed to find ID')
        return result
    
    result['en']['id'] = lines[line_i]
    line_i += 1
    
    return result
