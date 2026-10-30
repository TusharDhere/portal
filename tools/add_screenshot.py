"""Add a screenshot to an SOP.

Usage:
  python tools/add_screenshot.py <sop-id> <image-url-or-path> "<alt text>" <learn-article-url> "<article title>"

The image can be a local file or a raw.githubusercontent.com URL from Microsoft's public docs
repositories (CC BY 4.0). It is resized to max 1000px, converted to WebP and stored in shots/shots.json.
Then run: python build.py
"""
import sys, io, json, base64, os, urllib.request
from PIL import Image
sid, src, alt, learn, title = sys.argv[1:6]
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(BASE, 'shots', 'shots.json')
data = json.load(open(path, encoding='utf8'))
raw = urllib.request.urlopen(src).read() if src.startswith('http') else open(src, 'rb').read()
im = Image.open(io.BytesIO(raw)).convert('RGB')
if im.width > 1000:
    im = im.resize((1000, int(im.height * 1000 / im.width)))
buf = io.BytesIO(); im.save(buf, 'WEBP', quality=82)
data['img'].setdefault(sid, []).append(dict(uri='data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode(), alt=alt, w=im.width, h=im.height))
data['src'][sid] = [learn, title]
json.dump(data, open(path, 'w', encoding='utf8'))
print('added to', sid, im.size)
