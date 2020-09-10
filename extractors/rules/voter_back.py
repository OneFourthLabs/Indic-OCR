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

def get_values(full_str, lang='ta'):
    lines = full_str.split('\n')
    line_i, n_lines = 0, len(lines)
    result = {'en': {}, lang: {}}
    
    ## -- EXTRACT GENDER -- ##
    regional_key = key_map[lang]['gender']
    while line_i < n_lines and not 'sex' in lines[line_i].lower() and not 'male' in lines[line_i].lower() and not regional_key in lines[line_i]:
        line_i += 1
    if line_i >= n_lines:
        print('Failed to discern the gender')
        return result
    
    # Assume only 2 genders
    result['en']['gender'] = 'Female' if 'female' in lines[line_i].lower() else 'Male'
    result[lang]['gender'] = value_map[lang][result['en']['gender']]
    line_i += 1
    
    ## -- EXTRACT DOB -- ##
    while line_i < n_lines and not 'dob' in lines[line_i].lower() and not 'age' in lines[line_i].lower() and not 'yr' in lines[line_i].lower():
        line_i += 1
    if line_i >= n_lines:
        print('Failed to find DOB')
        return result
    
    matches = re.findall(r'(\d+/\d+/\d+)', lines[line_i])
    if not matches:
        print('DOB in broken format?')
        return result
    dob_str = matches[0]
    result['en']['dob'] = dob_str
    result[lang]['dob'] = dob_str
    line_i += 1
    
    ## -- EXTRACT ADDRESS IN REGIONAL LANGUAGE -- ##
    regional_key = key_map[lang]['address']
    if line_i >= n_lines or not any((
        regional_key in lines[line_i],
        ':' in lines[line_i])): # Weak but ok
        print('Failed to find regional address')
        return result
    
    address = lines[line_i].replace(regional_key, '').replace(':', '').strip()
    line_i += 1
    
    # Copy until we reach the English line
    while line_i < n_lines and 'Address' not in lines[line_i]:
        address += '\n' + lines[line_i].strip()
        line_i += 1
    
    result[lang]['address'] = address
    
    ## -- EXTRACT ENGLISH ADDRESS -- ##
    if line_i >= n_lines or not any((
        'Address' in lines[line_i],
        ':' in lines[line_i])): # Weak but ok
        print('Failed to find English address')
        return result
    
    address = lines[line_i].replace('Address', '').replace(':', '').strip()
    line_i += 1
    if line_i >= n_lines:
        print('Corrupt English Address')
        return result
    
    # Assume 2 line address
    address += '\n' + lines[line_i]
    line_i += 1
    
    result['en']['address'] = address
    
    ## -- EXTRACT DATE OF ISSUE -- ##
    while line_i < n_lines and not 'date' in lines[line_i].lower():
        line_i += 1
    if line_i >= n_lines:
        print('Failed to parse DoI')
        return result
    
    matches = re.findall(r'(\d+-\d+-\d+)', lines[line_i])
    if not matches:
        print('DoI in broken format?')
        return result
    result['en']['doi'] = matches[0]
    
    return result
