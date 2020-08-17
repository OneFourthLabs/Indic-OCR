import re

key_map = {
    'ta': {
        'name': 'வாக்காளரின் பெயர்',
        'relation': 'உறவினரின் பெயர்'
    }
}

def get_values(full_str, lang='ta'):
    lines = full_str.split('\n')
    line_i, n_lines = 0, len(lines)
    result = {'en': {}, lang: {}}
    
    # -- EXTRACT ID -- #
    while line_i < n_lines and not 'IDENTITY' in lines[line_i].upper() and not 'CARD' in lines[line_i].upper():
        line_i += 1
    line_i += 1
    if line_i >= n_lines:
        print('Failed to find the ID')
        return result
    
    # regex_pattern = r'[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d' # Fails when bad OCR
    regex_pattern = r'\w{10}'
    matches = re.findall(regex_pattern, lines[line_i])
    if not matches:
        print('Unable to parse ID')
        return result
    
    result['en']['id'] = matches[0]
    line_i += 1
    
    ## -- EXTRACT REGIONAL NAME -- #
    regional_key = key_map[lang]['name'].split()[0]
    while line_i < n_lines and not any((
        regional_key in lines[line_i],
        ':' in lines[line_i])): # Weak but ok
        line_i += 1
    
    if line_i >= n_lines:
        print('Failed to find regional name')
        return result
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result[lang]['name'] = name
    line_i += 1
    
    ## -- EXTRACT ENGLISH NAME -- #
    while line_i < n_lines and not any((
        'Elector' in lines[line_i],
        ':' in lines[line_i])): # Weak but ok
        line_i += 1
    
    if line_i >= n_lines:
        print('Failed to find English name')
        return result
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result['en']['name'] = name
    line_i += 1
    
    ## -- RELATION'S REGIONAL NAME -- #
    regional_key = key_map[lang]['relation'].split()[0]
    while line_i < n_lines and not any((
        regional_key in lines[line_i],
        ':' in lines[line_i])): # Weak but ok
        line_i += 1
    
    if line_i >= n_lines:
        print('Failed to find regional relation name')
        return result
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result[lang]['relation'] = name
    line_i += 1
    
    ## -- RELATION'S ENGLISH NAME -- #
    while line_i < n_lines and not any((
        'Relation' in lines[line_i],
        ':' in lines[line_i])): # Weak but ok
        line_i += 1
    
    if line_i >= n_lines:
        print('Failed to find English relation name')
        return result
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result['en']['relation'] = name
    line_i += 1
    
    return result
