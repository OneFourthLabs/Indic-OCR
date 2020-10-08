import string
ALLOWED_ENGLISH_CHARS = string.digits + ' ' + string.ascii_letters + '.,?/_-:;' #string.punctuation
DISALLOWED_REGIONAL_CHARS = string.ascii_letters + ''.join([c for c in string.punctuation if c not in '.,?/_-:;'])

def remove_non_ascii(s):
    # Allow only ASCII chars
    return ''.join([c for c in s if c in ALLOWED_ENGLISH_CHARS]).strip()

def remove_english_chars(s):
    # Remove English chars
    return ''.join([c for c in s if c not in DISALLOWED_REGIONAL_CHARS]).strip()
