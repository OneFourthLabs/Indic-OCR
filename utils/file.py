import os, io
from datetime import datetime

def dump_file_from_bytes(bytes: io.BytesIO, extension, output_folder=None):
    out_file = datetime.now().strftime("%Y-%m-%d__%H-%M-%S") + extension
    if output_folder:
        out_file = os.path.join(output_folder, out_file)
    with open(out_file, 'wb') as f:
        f.write(bytes.getbuffer())
    return out_file

def dump_uploaded_file(base_filename, file, output_folder=None):
    extension = os.path.splitext(base_filename)[1]
    out_file = datetime.now().strftime("%Y-%m-%d__%H-%M-%S") + extension
    if output_folder:
        out_file = os.path.join(output_folder, out_file)
    with open(out_file, 'wb') as f:
        f.write(file.read())
    return out_file
