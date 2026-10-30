import json as _j
_SH=_j.load(open(os.path.join(BASE,'shots','shots.json'),encoding='utf8'))
_o=sop_html
def sop_html(s):
    h=_o(s);k=s['id']
    if k in _SH['img']:
        u,t=_SH['src'][k]
        figs=''.join(f'<figure class="shot"><img loading="lazy" src="{x["uri"]}" width="{x["w"]}" height="{x["h"]}" alt="{E(x["alt"])}"><figcaption>{E(x["alt"])}</figcaption></figure>' for x in _SH['img'][k])
        note=f'<p class="src">Screenshots from <a href="{u}" target="_blank" rel="noopener">Microsoft Learn: {E(t)}</a>, © Microsoft, licensed under <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>.</p>'
        h=h.replace('</ol>','</ol><h3>Portal screenshots</h3><div class="shots">'+figs+'</div>'+note,1)
    return h
