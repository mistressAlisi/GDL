import base64
import gzip
import json

import pybase64


def encode_json_for_html(obj):
    json_bytes = json.dumps(obj).encode('utf-8')  # minified JSON
    compressed = gzip.compress(json_bytes)
    encoded = pybase64.urlsafe_b64encode(compressed).decode('ascii')
    # print(encoded,type(encoded))
    return encoded

def decode_json_from_html(encoded):
    compressed = pybase64.urlsafe_b64decode(encoded)
    json_bytes = gzip.decompress(compressed)
    return json.loads(json_bytes.decode('utf-8'))