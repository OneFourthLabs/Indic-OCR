import re
import string
string.alphanumerics = string.ascii_letters + string.digits

ALLOWED_ENGLISH_CHARS = string.digits + ' ' + string.ascii_letters + '.,?/_-:;' #string.punctuation
DISALLOWED_REGIONAL_CHARS = string.ascii_letters + ''.join([c for c in string.punctuation if c not in '.,?/_-:;'])

EN_NUMERALS = '0123456789'

NUMERAL_MAP = {
    'hi': str.maketrans({en: l for en, l in zip('०१२३४५६७८९', EN_NUMERALS)}),
    'ta': str.maketrans({en: l for en, l in zip('௦௧௨௩௪௫௬௭௮௯', EN_NUMERALS)})
}

def remove_non_ascii(s):
    # Allow only ASCII chars
    return ''.join([c for c in s if c in ALLOWED_ENGLISH_CHARS]).strip()

def remove_english_chars(s):
    # Remove English chars
    return ''.join([c for c in s if c not in DISALLOWED_REGIONAL_CHARS]).strip()

def remove_non_letters(s):
    # Remove characters that are not ASCII letters
    return ''.join([c for c in s if c in string.ascii_letters])

def remove_non_letters_except_space(s):
    # Remove characters that are neither ASCII letters nor space
    return ''.join([c for c in s if c in string.ascii_letters+' ']).strip()

def remove_non_alphanumerics(s):
    # Remove characters that are neither ASCII letters nor numbers
    return ''.join([c for c in s if c in string.alphanumerics])

def fix_date(date_str):
    date_str = date_str.replace('|', '/').replace('!', '/')
    if not re.findall(r'(\d\d/\d\d/\d\d\d\d)', date_str):
        # If 8 or more digits are there, probably fix it
        raw_digits = remove_non_numerals(date_str)
        if len(raw_digits) == 8:
            return raw_digits[:2] + '/' + raw_digits[2:4] + '/' + raw_digits[4:]
        elif len(raw_digits) > 8:
            half_broken_dob_regex = r'(\d\d/\d\d.+\d\d\d\d)'
            if re.findall(half_broken_dob_regex, date_str):
                # If half broken (without slash in between), fix it.
                date_str = re.findall(half_broken_dob_regex, date_str)[0]
                date_str = date_str[:5] + '/' + date_str[-4:]
            else:
                # Assume first 8 digits as DoB and proceed
                date_str = raw_digits[:2] + '/' + raw_digits[2:4] + '/'
                if len(raw_digits) == 9:
                    date_str += raw_digits[-4:]
                else:
                    date_str += raw_digits[4:8]
    return remove_non_ascii(date_str.replace(' ', ''))

def remove_non_numerals(s):
    # Remove characters that are not numbers
    return ''.join([c for c in s if c in string.digits]).strip()

def standardize_numerals(s, lang):
    # Convert language numerals to Hindu-Arabic
    if lang == 'en':
        return s
    return s.translate(NUMERAL_MAP[lang])
