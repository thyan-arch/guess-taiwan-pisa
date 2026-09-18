# -*- coding: utf-8 -*-
"""把 _style.css / _body.html / _app.js / data/questions.json 組成 web/index.html"""
import base64, json, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
W = os.path.join(ROOT, 'web')

def data_uri(p):
    return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()

def build():
    css  = open(os.path.join(W, '_style.css'), encoding='utf-8').read()
    body = open(os.path.join(W, '_body.html'), encoding='utf-8').read()
    js   = open(os.path.join(W, '_app.js'), encoding='utf-8').read()
    qs   = open(os.path.join(ROOT, 'data', 'questions.json'), encoding='utf-8').read()
    body = (body.replace('__LOGO_WHITE__', data_uri(os.path.join(W, 'assets/logo-white.png')))
                .replace('__LOGO_COLOR__', data_uri(os.path.join(W, 'assets/logo-color.png'))))
    head = ('<title>猜猜臺灣排第幾</title>\n'
      '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
      '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
      '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
      'family=Noto+Sans+TC:wght@400;500;700&family=Ubuntu:wght@500;700&'
      'family=Fira+Sans:wght@400;500&display=swap">\n')
    html = (head + '<style>\n' + css + '\n</style>\n\n' + body +
            '\n<script id="pisa-data" type="application/json">' + qs + '</script>\n'
            '<script>\n' + js + '\n</script>\n')
    for out in (os.path.join(W, 'index.html'), os.path.join(ROOT, 'docs', 'index.html')):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8').write(html)
        print(os.path.relpath(out, ROOT), round(os.path.getsize(out)/1024), 'KB')
    # GitHub Pages：關閉 Jekyll 處理
    open(os.path.join(ROOT, 'docs', '.nojekyll'), 'w').close()

if __name__ == '__main__':
    build()
