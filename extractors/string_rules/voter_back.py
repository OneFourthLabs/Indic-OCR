import re

key_map = {
    'ta': {
        'address': 'முகவரி',
        'gender': 'இனம்',
        'dob': 'பிறந்த தேதி'
    },
    'hi': {
        'address': 'पता',
        'gender': 'लिंग',
        'dob': 'जन्म की तारीख'
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

def parse_gender(lang, line_i, lines, n_lines, result):
    ## -- EXTRACT GENDER -- ##
    backtrack_line_i = line_i
    regional_key = key_map[lang]['gender']
    while line_i < n_lines and not 'sex' in lines[line_i].lower() and not 'male' in lines[line_i].lower() and not regional_key in lines[line_i]:
        line_i += 1
    if line_i >= n_lines:
        result['logs'].append('Failed to discern the gender')
        return backtrack_line_i
    
    # Assume only 2 genders
    result['en']['gender'] = 'Female' if 'female' in lines[line_i].lower() else 'Male'
    result[lang]['gender'] = value_map[lang][result['en']['gender']]
    line_i += 1

    return line_i

def parse_dob(lang, line_i, lines, n_lines, result):
    ## -- EXTRACT DOB -- ##
    backtrack_line_i = line_i
    while line_i < n_lines and not 'dob' in lines[line_i].lower() and not 'age' in lines[line_i].lower() and not 'yrs' in lines[line_i].lower():
        line_i += 1
    if line_i >= n_lines:
        result['logs'].append('Failed to find DOB')
        return backtrack_line_i
    
    matches = re.findall(r'(\d+/\d+/\d+)', lines[line_i])
    if not matches:
        result['logs'].append('DOB in broken format')
        result['en']['dob'] = lines[line_i].lower().replace('age', '').replace('dob', '').strip()
    else:
        dob_str = matches[0]
        result['en']['dob'] = dob_str
    line_i += 1
    return line_i

def parse_regional_address(lang, line_i, lines, n_lines, result):
    ## -- EXTRACT ADDRESS IN REGIONAL LANGUAGE -- ##
    backtrack_line_i = line_i
    regional_key = key_map[lang]['address']
    if line_i >= n_lines or not any((
        regional_key in lines[line_i],
        ':' in lines[line_i])): # Weak but ok
        result['logs'].append('Failed to find regional address')
        return backtrack_line_i
    
    address = lines[line_i].replace(regional_key, '').replace(':', '').strip()
    line_i += 1
    
    # Copy until we reach the English line
    while line_i < n_lines and 'address' not in lines[line_i].lower():
        address += '\n' + lines[line_i].strip()
        line_i += 1
    
    result[lang]['address'] = address
    return line_i

def parse_english_address(line_i, lines, n_lines, result):
    ## -- EXTRACT ENGLISH ADDRESS -- ##
    backtrack_line_i = line_i
    if line_i >= n_lines or not any((
        'address' in lines[line_i].lower(),
        ':' in lines[line_i])): # Weak but ok
        result['logs'].append('Failed to find English address')
        return backtrack_line_i
    
    address = lines[line_i].replace('Address', '').replace(':', '').strip()
    result['en']['address'] = address
    line_i += 1
    if line_i >= n_lines:
        result['logs'].append('Corrupt English Address')
        return line_i
    
    # Assume 2 line address
    address += '\n' + lines[line_i]
    result['en']['address'] = address
    line_i += 1

    return line_i

def parse_doi(line_i, lines, n_lines, result):
    ## -- EXTRACT DATE OF ISSUE -- ##
    backtrack_line_i = line_i
    while line_i < n_lines and not 'dat' in lines[line_i].lower():
        line_i += 1
    if line_i >= n_lines:
        result['logs'].append('Failed to parse DoI')
        return backtrack_line_i
    
    matches = re.findall(r'(\d+[-/ ]\d+[-/ ]\d+)', lines[line_i])
    if not matches:
        result['logs'].append('DoI in broken format')
        result['en']['doi'] = lines[line_i].lower().replace('date', '')
    else:
        result['en']['doi'] = matches[0]
    
    line_i += 1
    return line_i

def get_values(full_str, lang):
    lines = full_str.split('\n')
    line_i, n_lines = 0, len(lines)

    result = {'en': {}, lang: {}}
    result['logs'] = []
    
    line_i = parse_gender(lang, line_i, lines, n_lines, result)
    line_i = parse_dob(lang, line_i, lines, n_lines, result)
    
    line_i = parse_regional_address(lang, line_i, lines, n_lines, result)
    line_i = parse_english_address(line_i, lines, n_lines, result)
    
    line_i = parse_doi(line_i, lines, n_lines, result)
    
    return result
