import re

key_map = {
    'ta': {
        'name': 'வாக்காளரின் பெயர்',
        'relation': 'உறவினரின் பெயர்'
    },
    'hi': {
        'name': 'नाम',
        'relation': 'पिता|माता|पति का नाम'
    }
}

def get_values(full_str, lang):
    full_str = full_str.replace(' EPIC', '')
    lines = full_str.split('\n')
    line_i, n_lines = 0, len(lines)
    result = {'en': {}, lang: {}}
    
    # -- EXTRACT ID -- #
    # Search for header: "Elector Photo Identity Card"
    while line_i < n_lines and not 'PHOTO' in lines[line_i].upper() and not 'IDENTITY' in lines[line_i].upper() and not 'CARD' in lines[line_i].upper():
        line_i += 1
    line_i += 1
    if line_i >= n_lines:
        # Retry by searching for line "Election Commission of India"
        line_i = 0
        while line_i < n_lines and not 'ELECTION' in lines[line_i].upper() and not 'COMMISSION' in lines[line_i].upper() and not 'INDIA' in lines[line_i].upper():
            line_i += 1
        line_i += 2
        if line_i >= n_lines:
            print('Failed to find the voter header')
            return result
    
    exact_regex_pattern = r'[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d' # Fails when bad OCR
    regex_pattern = r'\w{10}'
    matches = re.findall(regex_pattern, lines[line_i])
    while not matches:
        line_i += 1
        if line_i >= n_lines: break
        matches = re.findall(exact_regex_pattern, lines[line_i])
    
    if not matches:
        print('Corrupt ID')
        return result
    elif line_i >= n_lines:
        print('Unable to parse ID')
        return result
    
    result['en']['id'] = matches[0]
    line_i += 1
    
    ## -- EXTRACT REGIONAL NAME -- #
    regional_key_parts = key_map[lang]['name'].split()
    regional_key = regional_key_parts[0]
    regional_key_b = regional_key_parts[1] if len(regional_key_parts) > 1 else None
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
    
    if name.startswith(regional_key) or (regional_key_b and name.startswith(regional_key_b)):
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
    regional_key_parts = key_map[lang]['relation'].split()
    regional_key = regional_key_parts[0]
    regional_key_b = regional_key_parts[-1]
    backtrack_line_i = line_i
    while line_i < n_lines and not re.findall(regional_key, lines[line_i]):
        line_i += 1

    if line_i >= n_lines:
        # What if the first word in "Father Name" is corrupt?
        # Generally, the 'Father Name' will be split in 2 lines.
        # Let's search for the 2nd line and back a line
        line_i = backtrack_line_i
        while line_i < n_lines and not regional_key_b in lines[line_i]:
            line_i += 1
        if line_i >= n_lines:
            print('Failed to find regional relation name')
            return result
        #if len(lines[line_i].split()) == 1:
        line_i -= 1
    
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
    
    for regional_key_part in regional_key_parts:
        if name.startswith(regional_key_part + ' '):
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
