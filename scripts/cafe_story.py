"""Editorial landing for independent cafes and hospitality buyers."""
from datetime import datetime
import re
import editorial as e


def photo(src, alt, caption, stem=None, hero=False):
    if stem is None:
        stem = src.removesuffix('.webp')
    srcset = f'{stem}-640.webp 640w, {stem}-1280.webp 1280w, {src} 2000w'
    return ('<figure class="photo cafe-photo'+(' cafe-photo-hero' if hero else '')+'"><img src="'+e.esc(src)+'" srcset="'+e.esc(srcset)+'" sizes="'+('100vw' if hero else '(max-width: 700px) 100vw, 50vw')+'" alt="'+e.esc(alt)+'" '+('fetchpriority="high"' if hero else 'loading="lazy"')+' decoding="async"><figcaption>'+caption+'</figcaption></figure>')


def render(post):
    intro, remaining = post['body'].split('\n## ', 1)
    story, faq_text = ('## ' + remaining).split('## Häufige Fragen', 1)
    chapters = re.findall(r'## (\d{2}) · (.+?)\n(.*?)(?=\n## |\Z)', story, re.S)
    pairs = [(q.strip(), a.strip()) for q, a in re.findall(r'### (.+?)\n(.*?)(?=\n### |\Z)', faq_text, re.S)]
    if len(chapters) != 6 or len(pairs) != 6:
        raise ValueError('Cafe story requires six chapters and six FAQ answers')
    date = datetime.fromisoformat(post['published']).strftime('%d.%m.%Y')
    body = '<nav class="breadcrumbs" aria-label="Brotkrümelnavigation"><a href="/">Startseite</a><span>/</span><a href="/aktuelles/">Journal</a><span>/</span><span>Für Cafés</span></nav><article class="editorial cafe-story"><header class="story-heading"><span class="eyebrow">Für Cafés · Ideen für deine Getränkekarte</span><h1>'+e.inline(post['heading'])+'</h1><div class="standfirst">'+e.blocks(intro)+'</div><p class="byline">'+e.esc(post['author'])+' · <time datetime="'+e.esc(post['published'])+'">'+date+'</time> · 6 Minuten Lesezeit</p></header>'
    base = '/images/magazin/pine-nut-latte-gastronomie/barista-beim-espresso'
    body += photo(base+'.webp', 'Barista bereitet Espresso an einer professionellen Kaffeemaschine zu. Stimmungsbild.', 'Stimmungsbild · Pew Nguyen / Pexels. Keine Aufnahme eines M97-Factory-Getränks. <a href="https://www.pexels.com/photo/barrista-preparing-coffee-10439807/" target="_blank" rel="noopener noreferrer">Fotoquelle ↗</a>', base, True)
    body += '<section class="cafe-quick" aria-label="Der Test in vier Schritten"><div><span>01</span><strong>Ein Klassiker</strong><small>aus deiner Karte wählen</small></div><div><span>02</span><strong>Klein probieren</strong><small>Geschmack und Ablauf prüfen</small></div><div><span>03</span><strong>Eigene Zahlen</strong><small>Portion und Kosten rechnen</small></div><div><span>04</span><strong>Dann entscheiden</strong><small>Gästefeedback einbeziehen</small></div></section>'
    body += '<nav class="cafe-route" aria-label="Artikelübersicht"><span class="eyebrow">Vom Bar-Test zur Karte</span><ol>'+''.join('<li><a href="#cafe-'+n+'"><span>'+n+'</span>'+e.esc(title)+'</a></li>' for n, title, _ in chapters)+'</ol></nav>'
    for n, title, copy in chapters:
        body += '<section class="cafe-chapter" id="cafe-'+n+'"><div class="cafe-chapter-heading"><span class="recipe-number">'+n+'</span><h2>'+e.esc(title)+'</h2></div><div class="prose cafe-copy">'+e.blocks(copy)+'</div>'
        if n == '02':
            cup='/images/magazin/pine-nut-latte/recipe-01-cappuccino.webp'
            body += photo(cup, 'Cappuccino mit Latte Art als mögliches Ausgangsgetränk für einen eigenen Geschmackstest. Stimmungsbild.', 'Cappuccino-Stimmungsbild · Busenur Demirkan / Pexels. Kein getestetes PINE-NUT-LATTE-Rezept. <a href="https://www.pexels.com/photo/elegant-latte-art-on-ceramic-cup-34030761/" target="_blank" rel="noopener noreferrer">Fotoquelle ↗</a>', '/images/magazin/pine-nut-latte/recipe-01-cappuccino')
        if n == '04':
            body += '<aside class="cafe-equation"><span class="eyebrow">Deine Rechnung</span><div><strong>Preis netto</strong><span aria-hidden="true">−</span><strong>Zusatzkosten</strong><span aria-hidden="true">=</span><strong>Deckungsbeitrag</strong></div><p>Berechne mit deinem tatsächlichen Einkaufspreis, der getesteten Portion, deiner Arbeitszeit und den verkauften Testgetränken.</p></aside>'
        body += '</section>'
    body += e.faq(pairs)
    body += '<aside class="cafe-contact"><span class="eyebrow">Nächster Schritt</span><h2>Welche Variante passt hinter deine Bar?</h2><p>Frag nach Händlerkonditionen und teile uns mit, welche Getränke du servierst.</p><a class="button" href="/#kontakt">Händleranfrage stellen <span aria-hidden="true">→</span></a><a href="'+e.RECIPES+'">Experimentelle Ideen für die Bar ansehen →</a></aside>'
    body += '<aside class="production-reading"><span class="eyebrow">Weiter im Journal</span><h2>Ein paar Ideen zum Ausprobieren.</h2><div><a href="'+e.RECIPES+'">7 experimentelle Getränkekombinationen →</a><a href="/magazin/pine-nut-latte-herstellung/">Wie PINE NUT LATTE entsteht →</a><a href="/aktuelles/">Alle Geschichten im Journal →</a></div></aside><a class="back-link" href="/aktuelles/">← Alle Geschichten</a></article>'
    url=e.BASE+post['path']; publisher={'@type':'Organization','name':'M97 Factory','url':e.BASE}
    graph=[{'@type':'WebPage','@id':url,'url':url,'name':post['title'],'inLanguage':'de-DE'},
           {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Startseite','item':e.BASE+'/'},{'@type':'ListItem','position':2,'name':'Journal','item':e.BASE+'/aktuelles/'},{'@type':'ListItem','position':3,'name':post['title'],'item':url}]},
           {'@type':'BlogPosting','@id':url+'#article','url':url,'headline':post['heading'],'description':post['description'],'image':[e.BASE+post['image']],'mainEntityOfPage':{'@id':url},'inLanguage':'de-DE','articleSection':'Für Cafés','author':publisher,'publisher':publisher,'keywords':['Getränke für Cafés','Kaffee Menü erweitern','Getränkekarte Café Ideen','Barista neue Getränke','PINE NUT LATTE Gastronomie'],'datePublished':post['published'],'dateModified':post['modified']},
           {'@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':re.sub(r'[*]','',a)}} for q,a in pairs]}]
    return e.shell(post['title']+' | M97 Factory',post['description'],post['path'],body,graph,post['image'],False)

