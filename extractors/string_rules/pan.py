'''
Rule-based parser for most PAN card formats

Should also work for this very old format, which is similar to new PAN:
https://www.tribuneindia.com/1999/99jun12/10ct1.jpg
'''

from . import pan_old, pan_new
import re

def get_values(full_str, lang='hi'):
    test_str = full_str.lower()
    if re.findall(pan_new.RELATION_KEYS, test_str) or re.findall(pan_new.PAN_HINDI_KEYS, test_str) or re.findall(pan_new.DOB_KEYS, test_str) \
        or 'name' in test_str or re.findall(r' card\s+', test_str) or 'हस्ताक्षर' in test_str \
        or re.findall('\d\d-\d\d-\d\d\d\d', test_str) or 'commissioner' in test_str: # Very old format
        
        return pan_new.get_values(full_str, lang)
    else:
        return pan_old.get_values(full_str, lang)
