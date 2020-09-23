'''
Indic Transliterator
'''

from aksharamukha.transliterate import process
from .lang import ISO639_TO_SCRIPT

LANG2SCRIPT = {lang: script.title() for lang, script in ISO639_TO_SCRIPT.items()}
LANG2SCRIPT['en'] = 'ISO'
# TODO: Add all supported languages supported: aksharamukha.appspot.com/documentation

postprocess_options = ['TamilRemoveApostrophe', 'TamilRemoveNumbers']  

def pre_process(src_script, txt):
    if src_script == 'ISO':
        txt = txt.upper().replace('X', 'KS').replace('W', 'V')
    return txt

def transliterate(from_lang, to_lang, phrase):
    src_script = LANG2SCRIPT[from_lang]
    dest_script = LANG2SCRIPT[to_lang]
    phrase = pre_process(src_script, phrase)
    return process(src_script, dest_script, phrase, post_options=postprocess_options)
