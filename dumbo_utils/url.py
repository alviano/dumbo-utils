import base64
import json
import zlib


def compress_object_for_url(obj: object, *, suffix: str = '%21'):
    json_dump = json.dumps(obj, separators=(',', ':')).encode()
    json_dump = base64.b64encode(json_dump)
    return base64.b64encode(zlib.compress(json_dump)).decode() + suffix
