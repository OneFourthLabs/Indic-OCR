DOC_MAP = {
    'pan': extract_pan,
    'pan_new': extract_pan
}

def extract_from_qr(doc_type, bboxes):
    if doc_type not in DOC_MAP:
        return None
    
    qr_bboxes = [bbox for bbox in bboxes if bbox['type']=='qr']
    if not qr_bboxes:
        return None
    
    qr_message = qr_bboxes[0]['text']
    return DOC_MAP[doc_type](qr_message)

def extract_pan(text):
    result = {'en': {}}
    lines = text.split('\n')
    
    # Line 1 format:
    # नाम / Name : <NAME>
    if 'Name' not in lines[0]:
        return None
    
    result['en']['name'] = lines[0].split(':')[1].strip()
    
    # Line 2 format:
    # पिता का नाम / Father's Name : <NAME>
    # Note: Can also be father or mother or parent
    
    result['en']['parent'] = lines[1].split(':')[1].strip()
    
    # Line 3 format:
    # जन्म की तारीख / Date of Birth : <DOB>
    
    if 'Date of Birth' not in lines[2]:
        return None
    
    result['en']['dob'] = lines[2].split(':')[1].strip()
    
    # Line 4 format:
    # पैन / PAN : <ID>
    
    if 'PAN' not in lines[3]:
        return None
    
    result['en']['id'] = lines[3].split(':')[1].strip()
    
    return result
