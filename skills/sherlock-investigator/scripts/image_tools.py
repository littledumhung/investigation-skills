"""Optional local crops and average hash. Similarity is never identity proof."""
def crop(path, destination, box):
    from PIL import Image
    with Image.open(path) as image:
        if image.width * image.height > 50_000_000:
            raise ValueError('Image too large')
        left, top, right, bottom = map(int, box)
        if not 0 <= left < right <= image.width or not 0 <= top < bottom <= image.height:
            raise ValueError('Crop outside source')
        image.crop((left, top, right, bottom)).save(destination)
    return str(destination)

def average_hash(path):
    from PIL import Image
    with Image.open(path) as image:
        if image.width * image.height > 50_000_000:
            raise ValueError('Image too large')
        values = list(image.convert('L').resize((8, 8)).getdata())
    mean = sum(values) / 64
    return f'{sum((v >= mean) << i for i, v in enumerate(values)):016x}'

def distance(first, second):
    return (int(first, 16) ^ int(second, 16)).bit_count()
