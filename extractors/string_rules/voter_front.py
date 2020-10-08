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

import string
ALLOWED_ENGLISH_CHARS = string.digits + ' ' + string.ascii_letters + '.,?/_-:;' #string.punctuation
DISALLOWED_REGIONAL_CHARS = string.ascii_letters + ''.join([c for c in string.punctuation if c not in '.,?/_-:;'])

def parse_id(line_i, lines, n_lines, result):
    # Search for header: "Elector Photo Identity Card"
    backtrack_line_i = line_i
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
            result['logs'].append('Failed to find the voter header')
            line_i = backtrack_line_i
    
    # -- EXTRACT ID -- #
    backtrack_line_i = line_i
    exact_regex_pattern = r'[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d' # Fails when bad OCR
    regex_pattern = r'\w{10}'
    matches = re.findall(regex_pattern, lines[line_i])
    while not matches:
        line_i += 1
        if line_i >= n_lines: break
        matches = re.findall(exact_regex_pattern, lines[line_i])
    
    if not matches:
        result['logs'].append('Corrupt ID')
        line_i = backtrack_line_i
    elif line_i >= n_lines:
        result['logs'].append('Unable to parse ID')
        line_i = backtrack_line_i
    else:
        # Success
        result['en']['id'] = matches[0]
        line_i += 1
    
    return line_i

def parse_regional_name(lang, line_i, lines, n_lines, result):
    ## -- EXTRACT REGIONAL NAME -- #
    backtrack_line_i = line_i
    regional_key_parts = key_map[lang]['name'].split()
    regional_key = regional_key_parts[0]
    regional_key_b = regional_key_parts[1] if len(regional_key_parts) > 1 else None
    # Search till we encounter the regional key, or stop when we encounter the next field 'name'
    while line_i < n_lines and not regional_key in lines[line_i] and not 'name' in lines[line_i].lower():
        line_i += 1
    
    if line_i >= n_lines or 'name' in lines[line_i].lower():
        result['logs'].append('Failed to find regional name')
        return backtrack_line_i
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result[lang]['name'] = name
    line_i += 1

    if not name:
        # What if it's in the next line?
        if line_i < n_lines:
            if regional_key_b in lines[line_i]:
                name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
        if name:
            result[lang]['name'] = name
            line_i += 1
    
    if name.startswith(regional_key) or (regional_key_b and name.startswith(regional_key_b)):
        name = ' '.join(name.split()[1:])
        result[lang]['name'] = name
    
    # Remove English chars
    result[lang]['name'] = ''.join([c for c in result[lang]['name'] if c not in DISALLOWED_REGIONAL_CHARS]).strip()

    if not result[lang]['name']:
        result['logs'].append('Corrupt Regional name')

    return line_i

def parse_english_name(line_i, lines, n_lines, result):
    ## -- EXTRACT ENGLISH NAME -- #
    # Note: Tamil Voter has the key 'Elector Name', but Hindi has 'Name'
    # TODO: 'Name' can accidentally match with 'Parent Name' too. How to fix?
    backtrack_line_i = line_i
    while line_i < n_lines and not 'elector' in lines[line_i].lower() and not 'name' in lines[line_i].lower():
        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to find English name')
        return backtrack_line_i
    
    # Remove first word
    name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
    
    result['en']['name'] = name
    line_i += 1

    if not name:
        # What if it's in the next line?
        if line_i < n_lines:
            if 'name' in lines[line_i].lower():
                name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
        if name:
            result['en']['name'] = name
            line_i += 1
    
    if name.lower().startswith('name') or name.lower().startswith('elect'):
        name = ' '.join(name.split()[1:])
        result['en']['name'] = name
    
    # Allow only ASCII chars
    result['en']['name'] = ''.join([c for c in result['en']['name'] if c in ALLOWED_ENGLISH_CHARS]).strip()

    if not result['en']['name']:
        result['logs'].append('Corrupt English name')

    return line_i

def parse_relation_regional_name(lang, line_i, lines, n_lines, result):
    ## -- RELATION'S REGIONAL NAME -- #
    backtrack_line_i = line_i
    regional_key_parts = key_map[lang]['relation'].split()
    regional_key = regional_key_parts[0]
    regional_key_b = regional_key_parts[-1]
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
            result['logs'].append('Failed to find regional relation name')
            return backtrack_line_i
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
    
    for regional_key_part in regional_key_parts:
        if name.startswith(regional_key_part + ' '):
            name = ' '.join(name.split()[1:])
            result[lang]['relation'] = name
    
    # Remove English chars
    result[lang]['relation'] = ''.join([c for c in result[lang]['relation'] if c not in DISALLOWED_REGIONAL_CHARS]).strip()

    if not result[lang]['relation']:
        result['logs'].append('Corrupt Relation regional name')
    
    return line_i

def parse_relation_english_name(line_i, lines, n_lines, result):
    ## -- RELATION'S ENGLISH NAME -- #
    backtrack_line_i = line_i
    while line_i < n_lines and not 'relation' in lines[line_i].lower() and not 'father' in lines[line_i].lower() and not 'husband' in lines[line_i].lower() and not 'parent' in lines[line_i].lower() and not 'mother' in lines[line_i].lower():
        line_i += 1
    
    if line_i >= n_lines:
        result['logs'].append('Failed to find English relation name')
        return backtrack_line_i
    
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
    
    if name.lower().startswith('name') or name.lower().startswith('relation') or name.lower().startswith('father') or name.lower().startswith('parent'):
        name = ' '.join(name.split()[1:])
        result['en']['relation'] = name
    
    # Incase the name is broken into 2 lines: 
    # "Father's: Narendra
    # Name Modi Ji"
    if line_i < n_lines:
        if lines[line_i].lower().startswith('name'):
            last_name = ' '.join(lines[line_i].split()[1:]).replace(':', '').strip()
            result['en']['relation'] += ' ' + last_name
            line_i += 1

    # Allow only ASCII chars
    result['en']['relation'] = ''.join([c for c in result['en']['relation'] if c in ALLOWED_ENGLISH_CHARS]).strip()

    # Sometimes, we will have to clear out the 's' from "Father s <NAME>"
    if result['en']['relation'].startswith('s '):
        result['en']['relation'] = result['en']['relation'][2:]

    if not result['en']['relation']:
        result['logs'].append('Corrupt Relation English name')

    return line_i

def get_values(full_str, lang):
    lines = full_str.replace('$', 'S').split('\n')
    line_i, n_lines = 0, len(lines)

    result = {'en': {}, lang: {}}
    result['logs'] = []
    
    line_i = parse_id(line_i, lines, n_lines, result)

    line_i = parse_regional_name(lang, line_i, lines, n_lines, result)
    line_i = parse_english_name(line_i, lines, n_lines, result)

    line_i = parse_relation_regional_name(lang, line_i, lines, n_lines, result)
    line_i = parse_relation_english_name(line_i, lines, n_lines, result)
    
    return result
