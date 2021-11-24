from execjs import compile


def decrypt():
    with open("myproject/object.js", 'r', encoding='utf-8') as f:
        js = f.read()
        ct = compile(js, cwd=r'node_modules')
        return ct
