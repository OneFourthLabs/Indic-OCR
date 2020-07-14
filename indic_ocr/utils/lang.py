
# Refer: www.loc.gov/standards/iso639-2/php/code_list.php
## 2-letter code to 3-letter code
ISO639_v1_TO_v2 = {
    'en': 'eng',
    'ta': 'tam',
    'hi': 'hin'
}

ISO639_v2_TO_v1 = {
    v2:v1 for v1,v2 in ISO639_v1_TO_v2.items()
}

ISO639_v2_TO_SCRIPT = {
    'eng': 'latin',
    'tam': 'tamil',
    'hin': 'devanagari'
}

# A mixture of ISO639 v1 and v2's as in real world
# 2 letters for majorities and 3 letters for minorities
def standardize_langcode(lang):
    if lang in ISO639_v2_TO_SCRIPT:
        if lang in ISO639_v2_TO_v1:
            return ISO639_v2_TO_v1[lang]
        return lang
    if lang in ISO639_v1_TO_v2:
        return lang
    return None

from langdetect import detect_langs, detect
def get_lang_from_text(text):
    try:
        return detect_langs(text)[0].lang
    except:
        return 'unknown'
