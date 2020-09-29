def extract_pan(text):
    result = {'en': {}}
    lines = text.split('\n')
    if len(lines) < 4:
        return None
    
    # Line 1 format:
    # नाम / Name : <NAME>
    if 'Name' not in lines[0]:
        return None
    
    result['en']['name'] = lines[0].split(':')[1].strip()
    
    # Line 2 format:
    # पिता का नाम / Father's Name : <NAME>
    # Note: Can also be father or mother or parent
    
    result['en']['relation'] = lines[1].split(':')[1].strip()
    
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

import xml.etree.ElementTree as ET
def extract_aadhar(xml_string):
    try:
        data_node = ET.fromstring(xml_string)
    except:
        return None
    
    return {
        'en': {
            'name': data_node.attrib['name'],
            # If DOB is present, convert YYYY-MM-DD to DD/MM/YYYY
            'dob': '/'.join(data_node.attrib['dob'].split('-')[::-1]) if 'dob' in data_node.attrib else None,
            'yob': data_node.attrib['yob'],
            'gender': 'Female' if data_node.attrib['gender'] == 'F' else 'Male',
            'relation': data_node.attrib['co'] if 'co' in data_node.attrib else None,

            'address': {
                'house': data_node.attrib['house'],
                'street': data_node.attrib['street'],
                'landmark': data_node.attrib['lm'],

                # Village/Town/City
                'city': data_node.attrib['vtc'],
                'post_office': data_node.attrib['po'],

                'district': data_node.attrib['dist'],
                'sub_district': data_node.attrib['subdist'],

                'state': data_node.attrib['state'],
                'pin_code': data_node.attrib['pc'],
            }
        }
    }

DOC_MAP = {
    'pan': extract_pan,
    'pan_new': extract_pan,
    'aadhar': extract_aadhar,
    'aadhar_front': extract_aadhar
}

def extract_from_qr(doc_type, bboxes):
    if doc_type not in DOC_MAP:
        return None
    
    qr_bboxes = [bbox for bbox in bboxes if bbox['type']=='qr']
    if not qr_bboxes:
        return None
    
    qr_message = qr_bboxes[0]['text']
    return DOC_MAP[doc_type](qr_message)
