import re

key_map = {
    'ta': {
        'name': 'வாக்காளரின் பெயர்',
        'relation': 'உறவினரின் பெயர்'
    },
    'hi': {
        'name': 'नाम',
        'relation': 'पिता नाम'
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
    regional_key_b = key_map[lang]['name'].split()[1]
    while line_i < n_lines and not regional_key in lines[line_i]:
        line_i += 1
    
    if line_i >= n_lines:
        print('Failed to find regional name')
        return result
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result[lang]['name'] = name
    line_i += 1

    if not name:
        # What if it's in the next line?
        if line_i < n_lines:
            #if regional_key_b in lines[line_i]:
            name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
        if name:
            result[lang]['name'] = name
            line_i += 1
        else:
            print('Corrupt Regional name')
            # return result
    
    if name.startswith(regional_key) or name.startswith(regional_key_b):
        name = ' '.join(name.split()[1:])
        result[lang]['name'] = name

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

    if not name:
        # What if it's in the next line?
        if line_i < n_lines:
            #if 'name' in lines[line_i].lower():
            name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
        if name:
            result['en']['name'] = name
            line_i += 1
        else:
            print('Corrupt English name')
            # return result
    
    if name.lower().startswith('name') or name.lower().startswith('elect'):
        name = ' '.join(name.split()[1:])
        result['en']['name'] = name
    
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

    if not name:
        # What if it's in the next line?
        if line_i < n_lines:
            #if regional_key_b in lines[line_i]:
            name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
        if name:
            result[lang]['relation'] = name
            line_i += 1
        else:
            print('Corrupt Relation regional name')
            # return result
    
    if name.startswith(regional_key) or name.startswith(regional_key_b):
        name = ' '.join(name.split()[1:])
        result[lang]['relation'] = name
    
    ## -- RELATION'S ENGLISH NAME -- #
    while line_i < n_lines and not 'relation' in lines[line_i].lower() and not 'father' in lines[line_i].lower() and not 'parent' in lines[line_i].lower():
        line_i += 1
    
    if line_i >= n_lines:
        print('Failed to find English relation name')
        return result
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result['en']['relation'] = name
    line_i += 1

    if not name:
        # What if it's in the next line?
        if line_i < n_lines:
            #if 'name' in lines[line_i].lower():
            name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
        if name:
            result['en']['relation'] = name
            line_i += 1
        else:
            print('Corrupt Relation English name')
            # return result
    
    if name.lower().startswith('name') or name.lower().startswith('relation') or name.lower().startswith('father') or name.lower().startswith('parent'):
        name = ' '.join(name.split()[1:])
        result['en']['relation'] = name
    
    return result
