import re

key_map = {
    'ta': {
        'name': 'வாக்காளரின் பெயர்',
        'relation': 'உறவினரின் பெயர்'
    },
    'hi': {
        'name': 'नाम',
        'relation': 'पिता का नाम'
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
    
    exact_regex_pattern = r'[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d' # Fails when bad OCR
    regex_pattern = r'\w{10}'
    matches = re.findall(regex_pattern, lines[line_i])
    while not matches:
        line_i += 1
        if line_i >= n_lines: break
        matches = re.findall(exact_regex_pattern, lines[line_i])
    
    if line_i >= n_lines or not matches:
        print('Unable to parse ID')
        return result
    
    result['en']['id'] = matches[0]
    line_i += 1
    
    ## -- EXTRACT REGIONAL NAME -- #
    regional_key = key_map[lang]['name'].split()[0]
    while line_i < n_lines and not regional_key in lines[line_i]:
        line_i += 1
    
    if line_i >= n_lines:
        print('Failed to find regional name')
        return result
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result[lang]['name'] = name
    line_i += 1
    
    ## -- EXTRACT ENGLISH NAME -- #
    # Note: Tamil Voter has the key 'Elector Name', but Hindi has 'Name'
    # TODO: 'Name' can accidentally match with 'Parent Name' too. How to fix?
    while line_i < n_lines and not 'Elector' in lines[line_i] and not 'Name' in lines[line_i]:
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
    while line_i < n_lines and not regional_key in lines[line_i]:
        line_i += 1
    
    if line_i >= n_lines:
        print('Failed to find regional relation name')
        return result
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result[lang]['relation'] = name
    line_i += 1
    
    ## -- RELATION'S ENGLISH NAME -- #
    while line_i < n_lines and not 'Relation' in lines[line_i]:
        line_i += 1
    
    if line_i >= n_lines:
        print('Failed to find English relation name')
        return result
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result['en']['relation'] = name
    line_i += 1
    
    return result
