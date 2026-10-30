"""Read EXIF only when Pillow is available; GPS stays opt-in and local."""
def _decimal(values, ref):
    result = float(values[0]) + float(values[1]) / 60 + float(values[2]) / 3600
    if isinstance(ref, bytes):
        ref = ref.decode('ascii')
    if ref not in ('N', 'S', 'E', 'W'):
        raise ValueError('Invalid GPS reference')
    return -result if ref in ('S', 'W') else result

def extract_metadata(path, allow_gps=False):
    try:
        from PIL import Image
    except ImportError:
        return {'status': 'unavailable', 'limitations': ['Pillow is not installed'], 'gps': None}
    try:
        with Image.open(path) as image:
            if image.width * image.height > 50_000_000:
                raise ValueError('Image exceeds 50 megapixel analysis limit')
            exif = image.getexif()
            result = {'status': 'ok', 'format': image.format, 'width': image.width,
                      'height': image.height, 'gps': None, 'exif_present': bool(exif),
                      'limitations': ['EXIF may be edited; it is not independent location verification.']}
            for tag, name in ((271, 'make'), (272, 'model'), (306, 'datetime')):
                if tag in exif:
                    result[name] = str(exif[tag])[:500]
            if allow_gps and 34853 in exif:
                gps = exif.get_ifd(34853)
                if all(k in gps for k in (1, 2, 3, 4)):
                    lat, lon = _decimal(gps[2], gps[1]), _decimal(gps[4], gps[3])
                    if abs(lat) > 90 or abs(lon) > 180:
                        raise ValueError('GPS out of range')
                    result['gps'] = {'latitude': lat, 'longitude': lon, 'role': 'exif_claim'}
            elif not allow_gps:
                result['limitations'].append('GPS extraction disabled pending public-location privacy review.')
            return result
    except (OSError, ValueError, SyntaxError, ZeroDivisionError) as exc:
        return {'status': 'error', 'gps': None, 'limitations': [type(exc).__name__ + ': metadata could not be decoded']}
