import re

def slashify(s):
    s = re.sub(r'^\/+', '', s)
    s = re.sub(r'\/+$', '', s)
    return re.sub(r'\/\/+', '\/', s)
