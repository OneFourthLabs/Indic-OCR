import io, os
from datetime import datetime

def dump_jpeg(img: io.BytesIO, output_folder):
    out_file = datetime.now().strftime("%Y-%m-%d__%H-%M-%S") + '.jpg'
    out_file = os.path.join(output_folder, out_file)
    with open(out_file, 'wb') as f:
        f.write(img.getbuffer())
    return out_file
