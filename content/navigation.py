ORD=['Compute','Networking','Storage','Identity','Security','Monitoring','Backup & DR','Governance','Cost']
assert all(s['cat'] in ORD for s in SOPS)
SOPS.sort(key=lambda s:ORD.index(s['cat']))
_g={}
for s in SOPS:_g.setdefault(s['cat'],[]).append(s)
_slug=lambda c:c.replace(' & ','-').lower()
_n=sop_html
def sop_html(s):
    """One SOP = one page: <section class="view" id="v-sop-ID"> ... previous/next at the bottom."""
    h=_n(s);i=SOPS.index(s);sid=s['id']
    h=h.replace('<article class="sop"','<article class="sop" data-cat="%s"'%s['cat'],1);t=[]
    def rep(m):t.append(m.group(1));return f'<h3 id="sop-{sid}-{len(t)}">{m.group(1)}</h3>'
    h=re.sub(r'<h3>(.*?)</h3>',rep,h)
    toc='<nav class="toc">'+''.join(f'<a href="#sop-{sid}" data-t="sop-{sid}-{k+1}">{x}</a>' for k,x in enumerate(t))+'</nav>'
    h=h.replace(f'<h3 id="sop-{sid}-1"',toc+f'<h3 id="sop-{sid}-1"',1)
    h=h.replace('<div class="ck">','<div class="ck">'+''.join(f'<label><input type="checkbox"> {x}</label>' for x in s['v']),1)
    if s.get('cmd'):
        nt='<p class="src">Required permission: '+E((s.get('pre') or ['the role named in Prerequisites'])[0])+'.</p>'
        h=re.sub(r'(<h3 id="sop-%s-\d+">Commands</h3>)'%sid,lambda m:m.group(1)+nt,h,1)
    a=SOPS[i-1] if i else None;b=SOPS[i+1] if i+1<len(SOPS) else None
    lk=lambda x,arrow:f'<a href="#sop-{x["id"]}"'+(' style="text-align:right"' if arrow=='n' else '')+'><small>'+('Previous' if arrow=='p' else 'Next')+f' · {x["cat"]}</small><br>'+(('← ' if arrow=='p' else '')+E(x['t'])+(' →' if arrow=='n' else ''))+'</a>'
    pg='<div class="pager">'+(lk(a,'p') if a else '<span></span>')+(lk(b,'n') if b else '')+'</div>'
    h=h.replace('</article>',pg+'</article>')
    m=re.match(r'(<article[^>]*>)(.*?)(<nav class="toc">.*?</nav>)(.*?)(<div class="pager">.*</div>)</article>$',h,re.S)
    if m:
        parts=re.split(r'(?=<h3 id="sop-%s-\d+")'%re.escape(sid),m.group(4))
        secs=''
        for p in parts:
            if not p.strip():continue
            mm=re.match(r'(<h3 [^>]*>.*?</h3>)(.*)$',p,re.S)
            secs+='<section class="sec">'+mm.group(1)+'<div class="sb">'+mm.group(2)+'</div></section>' if mm else '<div class="sb">'+p+'</div>'
        h=m.group(1)+'<header class="sop-hero"><p class="src backl"><a href="#sops">← All Azure Portal SOPs</a> · '+s['cat']+'</p>'+m.group(2)+m.group(3)+'</header><div class="secs">'+secs+'</div>'+m.group(5)+'</article>'
    return f'<section class="view" id="v-sop-{sid}" data-sop="{sid}" data-cat="{s["cat"]}">'+h+'</section>'
