"""Render approved Markdown editorial sources. Drafts exist only in isolated previews."""
from datetime import datetime
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://machen97.com'
ASSETS = '/images/magazin/pine-nut-latte/'
RENAME = '/aktuelles/pinienkaffee-wird-pine-nut-latte/'
RECIPES = '/magazin/pine-nut-latte-cappuccino-rezepte/'


def esc(value):
    return escape(str(value), quote=True)


def inline(value):
    # Raw HTML from manuscripts is deliberately escaped.
    result = esc(value)
    result = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', result)
    result = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', result)
    return result


def blocks(markdown):
    lines = markdown.strip().splitlines(); result=[]; i=0
    while i < len(lines):
        line=lines[i].strip()
        if not line or line == '---' or line.startswith('![') or line.startswith('*Bildidee:'):
            i+=1; continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells): rows.append(cells)
                i+=1
            result.append('<div class="table-scroll" role="region" aria-label="Kombinationshilfe" tabindex="0"><table><thead><tr>'+''.join('<th scope="col">'+inline(c)+'</th>' for c in rows[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in row)+'</tr>' for row in rows[1:])+'</tbody></table></div>');continue
        if line.startswith('> '):
            paragraph=[]
            while i<len(lines) and lines[i].strip().startswith('> '): paragraph.append(lines[i].strip()[2:]);i+=1
            result.append('<aside class="editor-note">'+inline(' '.join(paragraph))+'</aside>');continue
        list_match=re.match(r'(- |\d+\. )',line)
        if list_match:
            ordered=line[0].isdigit(); tag='ol' if ordered else 'ul';items=[]
            while i<len(lines) and re.match(r'\d+\. ' if ordered else r'- ',lines[i].strip()):
                items.append(re.sub(r'^(- |\d+\. )','',lines[i].strip()));i+=1
            result.append(f'<{tag}>'+''.join('<li>'+inline(item)+'</li>' for item in items)+f'</{tag}>');continue
        heading=re.match(r'^(#{2,3}) (.+)$',line)
        if heading:
            level=len(heading[1]);result.append(f'<h{level}>'+inline(heading[2])+f'</h{level}>');i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#{2,3} |\d+\. |- |\||> |!\[)',lines[i].strip()):
            paragraph.append(lines[i].strip());i+=1
        result.append('<p>'+inline(' '.join(paragraph))+'</p>')
    return ''.join(result)


def load(include_drafts=False):
    result=[]
    for source in sorted((ROOT/'content/editorial').glob('*.md')):
        raw=source.read_text(encoding='utf-8')
        front,body=raw.split('---',2)[1:]
        metadata={}
        for line in front.strip().splitlines():
            key,value=line.split(':',1);metadata[key]=value.strip().strip('"')
        published=metadata.get('status')=='published'
        if not published and not include_drafts: continue
        recipe=metadata.get('article_type')=='RecipeCollection'
        body=body.split('# REDAKTIONS- UND DESIGNANHANG')[0]
        body=re.sub(r'<!--.*?-->','',body,flags=re.S).strip()
        heading,body=body.split('\n',1); heading=heading.removeprefix('# ')
        slug=metadata['slug']
        path=(slug if slug.startswith('/') else '/aktuelles/'+slug).rstrip('/')+'/'
        if not re.fullmatch(r'/(?:aktuelles|magazin)/[a-z0-9]+(?:-[a-z0-9]+)*/',path):
            raise ValueError(f'{source.name}: invalid editorial URL')
        if published:
            for field in ['published','modified','author']:
                if not metadata.get(field): raise ValueError(f'{source.name}: publication requires verified {field}')
            start=datetime.fromisoformat(metadata['published']);end=datetime.fromisoformat(metadata['modified'])
            if not start.tzinfo or not end.tzinfo or end<start:raise ValueError('Editorial dates must be real timezone-aware dates')
            if start>datetime.now(start.tzinfo):continue
        result.append(dict(slug=path.strip('/').split('/')[-1],path=path,title=metadata['title'],heading=heading,
            description=metadata['description'],category='article' if recipe else 'news',
            image=ASSETS+'hero-pine-nut-cappuccino.webp' if recipe else ASSETS+'label-classic.webp',
            image_alt='Cappuccino – Stimmungsbild, keine Aufnahme des PINE-NUT-LATTE-Rezepts' if recipe else 'Neues Vorderetikett PINE NUT LATTE Classic 250 g',
            published=metadata.get('published',''),modified=metadata.get('modified',''),author=metadata.get('author',''),
            status='published' if published else 'draft',editorial=True,recipe=recipe,body=body,source=source.name))
    return result


def manifest():
    return {Path(x['file']).stem:x for x in json.loads((ROOT/'content/editorial/images.json').read_text())}


def image(name,hero=False,caption=None):
    item=manifest()[name];alt=item['alt']
    if item['kind']=='stock':alt+=' – Stimmungsbild, kein nachgewiesenes PINE-NUT-LATTE-Rezept'
    source=item['file'];stem=source.removesuffix('.webp')
    sizes='(max-width: 700px) 100vw, 50vw' if not hero else '100vw'
    cap=caption if caption is not None else ('Stimmungsbild · '+item.get('author','')+' / Pexels. Keine Aufnahme des beschriebenen PINE-NUT-LATTE-Rezepts.' if item['kind']=='stock' else 'Neues Vorderetikett · '+('Classic' if name=='label-classic' else 'mit Gewürzen')+' · 250 g')
    credit=f' <a href="{esc(item["source"])}" target="_blank" rel="noopener noreferrer">Fotoquelle ↗</a>' if item['kind']=='stock' else ''
    return f'<figure class="photo {"hero-photo" if hero else ""}"><img src="{source}" srcset="{stem}-640.webp 640w, {stem}-1280.webp 1280w, {source} {min(item["width"],1920)}w" sizes="{sizes}" alt="{esc(alt)}" width="{item["width"]}" height="{item["height"]}" {"fetchpriority=high" if hero else "loading=lazy"} decoding="async"><figcaption>{esc(cap)}{credit}</figcaption></figure>'


def shell(title,description,path,body,graph,img,preview=False):
    data=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')
    return f'''<!doctype html>
<!-- Generated editorial from content/editorial/*.md; never edit generated HTML. -->
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="{'noindex, nofollow' if preview else 'index, follow, max-image-preview:large'}">
<link rel="canonical" href="{BASE}{path}"><meta name="theme-color" content="#f5f2eb">
<meta property="og:type" content="{'website' if path=='/aktuelles/' else 'article'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{BASE}{img}"><meta property="og:locale" content="de_DE"><meta property="og:site_name" content="M97 Factory">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{BASE}{img}">
<link rel="icon" href="/favicon.ico"><link rel="alternate" type="application/rss+xml" title="M97 Factory Journal" href="/aktuelles/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/aktuelles/editorial.css"><script src="/aktuelles/editorial.js" defer></script><script type="application/ld+json">{data}</script></head><body>
<a class="skip" href="#content">Zum Inhalt</a>{'<div class="preview-banner">Vorschau · Noch nicht veröffentlicht</div>' if preview else ''}
<header class="journal-header"><a class="wordmark" href="/aktuelles/">M97 FACTORY<span>THE JOURNAL</span></a><nav aria-label="Hauptnavigation"><a href="/aktuelles/">Journal</a><a href="/">Zur Startseite <span aria-hidden="true">↗</span></a></nav></header>
<main id="content">{body}</main><footer class="journal-footer"><a class="wordmark" href="/aktuelles/">M97 FACTORY<span>Geschichten. Geschmack. Neue Ideen.</span></a><nav aria-label="Weitere Informationen"><a href="/impressum.html">Impressum</a><a href="/datenschutz.html">Datenschutz</a><a href="/aktuelles/feed.xml">RSS</a></nav><small>© 2026 Machen97 UG (haftungsbeschränkt)</small></footer></body></html>'''


def faq_pairs(markdown,recipe):
    if recipe:
        part=markdown.split('## Häufige Fragen')[1].split('---')[0]
        return [(q.strip(),a.strip()) for q,a in re.findall(r'### (.+?)\n(.*?)(?=\n### |\Z)',part,re.S)]
    part=markdown.split('### Kurz gefragt')[1].split('---')[0]
    return [(q.strip(),a.strip()) for q,a in re.findall(r'\*\*(.+?\?)\*\*\s*\n(.*?)(?=\n\*\*|\Z)',part,re.S)]


def faq(pairs):
    return '<section class="faq prose" id="faq"><span class="eyebrow">Gut zu wissen</span><h2>Häufige Fragen</h2>'+''.join('<details><summary><h3>'+esc(q)+'</h3><span aria-hidden="true">+</span></summary><div>'+blocks(a)+'</div></details>' for q,a in pairs)+'</section>'


def cta():
    return '<aside class="product-cta"><div><span class="eyebrow">Zwei Varianten. Viele Möglichkeiten.</span><h2>Finde deine Nussnote.</h2><p>Classic oder mit Gewürzen · 250 g</p></div><div class="cta-links"><a href="/#shop">Classic entdecken ↗</a><a href="/#shop">Mit Gewürzen entdecken ↗</a></div></aside>'


def render(post):
    markdown=post['body'];pairs=faq_pairs(markdown,post['recipe']);intro,rest=markdown.strip().split('\n\n',1)
    breadcrumb='<nav class="breadcrumbs" aria-label="Brotkrümelnavigation"><a href="/">Startseite</a><span>/</span><a href="/aktuelles/">Journal</a><span>/</span><span>'+('Rezepte' if post['recipe'] else 'Neuigkeiten')+'</span></nav>'
    byline='<p class="byline">Redaktioneller Entwurf · Noch nicht veröffentlicht</p>' if post['status']=='draft' else '<p class="byline">'+esc(post['author'])+' · <time datetime="'+esc(post['published'])+'">'+datetime.fromisoformat(post['published']).strftime('%d.%m.%Y')+'</time></p>'
    headline=inline(post['heading'])
    body=breadcrumb+'<article class="editorial '+('recipes' if post['recipe'] else 'news-story')+'"><header class="story-heading"><span class="eyebrow">'+('Rezepte &amp; Inspiration' if post['recipe'] else 'Neuigkeiten · M97 Factory')+'</span><h1>'+headline+'</h1><div class="standfirst">'+blocks(intro)+'</div>'+byline+'</header>'
    if post['recipe']:
        body+=image('hero-pine-nut-cappuccino',True)
        # Source image briefs are not article text; real stock alt/captions come from the manifest.
        rest=re.sub(r'!\[.*?\]\([^\n]+\)\n?', '',rest)
        rest=re.sub(r'\*Bildidee:.*?\*','',rest)
        before,remaining=rest.split('## Erst die Grundlage:',1)
        before=before.replace('Die folgenden Mischrezepte sind kreative Serviervorschläge und sollten vor Veröffentlichung von M97 Factory sensorisch getestet werden.','Die folgenden Mischrezepte sind kreative, experimentelle Serviervorschläge. Sie wurden von M97 Factory noch nicht sensorisch getestet und sind keine geprüften Herstellerrezepte.')
        body+='<div class="prose intro-copy">'+blocks(before)+'<aside class="editor-note"><strong>Zutaten &amp; Allergene:</strong> Die hier beschriebene Rezeptur enthält Milcheiweiß. Auch mit Haferdrink ist das Produkt nicht vegan. Bitte die aktuelle Zutatenliste und Allergenkennzeichnung auf der Verpackung beachten. Kakao kann ebenfalls Koffein enthalten; ein Mocha ohne Espresso ist deshalb nicht automatisch koffeinfrei.</aside></div>'
        chunks=re.split(r'\n## (?=\d\. )',remaining)
        base=chunks.pop(0).strip().removesuffix('---').strip()
        recipe_sections=[]
        for chunk in chunks:
            heading,content=chunk.split('\n',1);num=int(heading[0]);name=heading.split(' – ')[0][3:]
            if num==7: content=content.split('\n## Was passt')[0].removesuffix('---').strip()
            recipe_sections.append((num,name,heading,content))
        body+='<nav class="recipe-nav" aria-label="Die sieben Rezeptideen"><span class="eyebrow">Womit möchtest du anfangen?</span><div>'+''.join(f'<a href="#rezept-{num}"><span>0{num}</span>{esc(name.removeprefix("Pine Nut "))}<span aria-hidden="true">↘</span></a>' for num,name,_,_ in recipe_sections)+'</div></nav>'
        body+='<section id="grundrezept" class="foundation"><div class="prose"><span class="eyebrow">Experimentelle Grundlage für diese Mischrezepte</span><h2>Erst die Grundlage: '+esc(base.split('\n',1)[0])+'</h2>'+blocks(base.split('\n',1)[1])+'</div>'+image('ingredient-pine-nuts',caption='Pinienkerne · Zutaten-Stimmungsbild, keine Produktaufnahme.')+'</section>'
        for num,name,heading,content in recipe_sections:
            meta=re.search(r'^\*(Für .+?)\*',content,re.M);metadata=meta[1] if meta else ''
            content=re.sub(r'^\*Für .+?\*\s*','',content,flags=re.M)
            if num==2: content=content.replace('Nespresso.','Nespresso.')
            opening,ing=content.split('**Zutaten',1);ingtitle,ing=ing.split('**',1);ingredients,steps=ing.split('**Zubereitung**',1)
            instructions,tip=re.split(r'\n\n(?=\*\*)',steps,1)
            names=['','recipe-01-cappuccino','recipe-02-honey-latte','recipe-03-mocha','recipe-04-spiced-latte','recipe-05-iced-latte','recipe-06-flat-white','recipe-07-affogato']
            body+=f'<section class="recipe-section" id="rezept-{num}"><div class="recipe-title"><span class="recipe-number">0{num}</span><div><span class="eyebrow">{esc(metadata)}</span><h2>{esc(heading[3:])}</h2></div></div><div class="recipe-layout">'+image(names[num])+'<div class="recipe-copy">'+blocks(opening)+('<p class="source-link">Inspiration: <a href="https://www.nespresso.com/recipes/int/en/36139PIN-pine-nuts-honey-latte.html" target="_blank" rel="noopener noreferrer">Nespresso · Pine Nuts Honey Latte ↗</a></p>' if num==2 else '')+'<div class="recipe-method"><div class="ingredients"><h3>Zutaten'+esc(ingtitle)+'</h3>'+blocks(ingredients)+'</div><div class="steps"><h3>Zubereitung</h3>'+blocks(instructions)+'</div></div><div class="taste-note">'+blocks(tip)+'</div></div></div></section>'
            if num==3:body+=cta()
        table=markdown.split('## Was passt')[1].split('## Häufige Fragen')[0]
        body+='<section class="pairings prose"><span class="eyebrow">Dein kleiner Geschmacks-Kompass</span><h2>Was passt zu PINE NUT LATTE?</h2>'+blocks(table.split('\n',1)[1])+'</section>'+faq(pairs)
        outro=markdown.split('## Vielleicht muss')[1]
        body+='<section class="prose closing"><h2>Vielleicht muss'+esc(outro.split('\n',1)[0])+'</h2>'+blocks(outro.split('\n',1)[1])+'</section>'+cta()
        related=RENAME;related_title='Aus Pinienkaffee wird PINE NUT LATTE';related_image='label-classic'
    else:
        body+='<div class="rename-hero"><div><span class="eyebrow">Neuer Name. Vertrauter Geschmack.</span><p class="name-before">Pinienkaffee</p><span class="name-arrow" aria-hidden="true">↓</span><p class="name-after">PINE<br>NUT LATTE.</p><p>Classic &amp; mit Gewürzen · 250 g</p></div><div class="label-pair">'+image('label-classic',True)+image('label-spiced')+'</div></div>'
        before_faq=rest.split('### Kurz gefragt')[0].removesuffix('---').strip()
        # Preserve the unverified legal description as attributed draft wording, not an approved label quote.
        if post['status']=='draft':
            before_faq=before_faq.replace('Die rechtlich relevante Produktbeschreibung steht weiterhin gesondert auf der Verpackung:','Die rechtlich relevante Produktbeschreibung muss gesondert auf der Verpackung stehen. Im redaktionellen Entwurf lautet sie:')
        body+='<div class="prose news-copy">'+blocks(before_faq)+'</div><figure class="previous-pack"><img src="/images/photo_09.jpg" alt="Pinienkaffee Classic mit Getränk – bisherige Verpackung vor der Umbenennung" width="799" height="1200" loading="lazy"><figcaption>Echtes Produktfoto aus dem bisherigen Sortiment · Verpackung vor der Umbenennung.</figcaption></figure>'+faq(pairs)
        about=rest.split('**Über M97 Factory**',1)[1]
        body+='<aside class="prose about-brand"><h2>Über M97 Factory</h2>'+blocks(about)+'</aside>'+cta()
        related=RECIPES;related_title='Pine Nut Cappuccino & Co.: 7 Ideen';related_image='hero-pine-nut-cappuccino'
    body+='<aside class="related"><div><span class="eyebrow">Weiter im Journal</span><h2>'+esc(related_title)+'</h2><a class="button" href="'+related+'">Geschichte entdecken <span aria-hidden="true">→</span></a></div><img src="'+ASSETS+related_image+'.webp" alt="" width="640" height="480" loading="lazy"></aside><a class="back-link" href="/aktuelles/">← Alle Geschichten</a></article>'
    publisher={'@type':'Organization','name':'M97 Factory','url':BASE+'/#ueber-uns'}
    graph=[{'@type':'WebPage','@id':BASE+post['path'],'url':BASE+post['path'],'name':post['title'],'inLanguage':'de-DE'},
           {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Startseite','item':BASE+'/'},{'@type':'ListItem','position':2,'name':'Journal','item':BASE+'/aktuelles/'},{'@type':'ListItem','position':3,'name':post['title'],'item':BASE+post['path']}]},
           {'@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':re.sub(r'\*','',a)}} for q,a in pairs]}]
    # No Recipe markup: stock photographs and untested suggestions are not verified recipe evidence.
    # NewsArticle is emitted only at publication with verified author and real dates.
    if post['recipe'] or post['status']=='published':
        schema={'@type':'BlogPosting' if post['recipe'] else 'NewsArticle','headline':post['heading'],'description':post['description'],'image':[BASE+post['image']],'mainEntityOfPage':{'@id':BASE+post['path']},'inLanguage':'de-DE','publisher':publisher}
        if post['status']=='published':schema.update(datePublished=post['published'],dateModified=post['modified'],author={'@type':'Organization','name':post['author']})
        graph.append(schema)
    title=post['title']+' | M97 Factory' if post['recipe'] else 'Pinienkaffee heißt jetzt PINE NUT LATTE | M97 Factory'
    description=post['description'] if post['recipe'] else 'Aus Pinienkaffee wird PINE NUT LATTE. Warum wir unser Getränk aus Pinienkernen in Deutschland umbenannt haben – und was gleich bleibt.'
    return shell(title,description,post['path'],body,graph,post['image'],post['status']=='draft')


def archive(posts,preview=False):
    cards=[]
    for post in posts:
        path=post.get('path','/aktuelles/'+post['slug']+'/')
        label='Rezepte & Inspiration' if post.get('recipe') else ('Neuigkeiten' if post['category']=='news' else 'Wissen & Zubereitung')
        date='<span>Entwurf · Vorschau</span>' if not post.get('published') else '<time datetime="'+esc(post['published'])+'">'+datetime.fromisoformat(post['published']).strftime('%d.%m.%Y')+'</time>'
        cards.append('<article class="journal-card"><a class="card-image" href="'+path+'" tabindex="-1" aria-hidden="true"><img src="'+esc(post['image'])+'" alt="" width="900" height="700" loading="lazy"></a><div class="card-copy"><div class="card-meta"><span>'+label+'</span>'+date+'</div><h2><a href="'+path+'">'+esc(post['title'])+'</a></h2><p>'+esc(post['description'])+'</p><a class="read-link" href="'+path+'" aria-label="'+esc('Beitrag lesen: '+post['title'])+'">Geschichte lesen <span aria-hidden="true">→</span></a></div></article>')
    body='<section class="journal-intro"><span class="eyebrow">Das Journal von M97 Factory</span><h1>Geschichten für<br>eine andere <em>Kaffeepause.</em></h1><p>Neue Ideen, vertrauter Geschmack.<br>Neuigkeiten und Inspiration rund um Pinienkerne.</p></section><section class="journal-grid" aria-label="Alle Neuigkeiten und Artikel">'+''.join(cards)+'</section>'
    graph=[{'@type':'CollectionPage','name':'M97 Factory Journal','url':BASE+'/aktuelles/','inLanguage':'de-DE','mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'url':BASE+p.get('path','/aktuelles/'+p['slug']+'/'),'name':p['title']} for i,p in enumerate(posts)]}}]
    return shell('Neuigkeiten & Artikel | M97 Factory', 'Geschichten, Neuigkeiten und Rezeptideen von M97 Factory. Entdecke PINE NUT LATTE und die Welt der Pinienkerne.', '/aktuelles/',body,graph,ASSETS+'hero-pine-nut-cappuccino.webp' if any(p.get('editorial') for p in posts) else '/images/og-preview.jpg',preview)


def home_carousel(posts):
    """Static accessible homepage links; drafts are included only in isolated previews."""
    short_titles = {
        'pinienkaffee-wird-pine-nut-latte': 'Pinienkaffee wird PINE NUT LATTE',
        'pine-nut-latte-cappuccino-rezepte': '7 Ideen mit PINE NUT LATTE',
        'pinienkaffee-zubereiten': 'Pinienkaffee richtig zubereiten',
        'aktuelles-start': 'Neuigkeiten von M97 Factory',
    }
    cards=[]
    for post in posts[:8]:
        path=post.get('path','/aktuelles/'+post['slug']+'/')
        category='Rezepte & Inspiration' if post.get('recipe') else ('Neuigkeiten' if post['category']=='news' else 'Wissen & Zubereitung')
        cards.append('<li><a class="journal-teaser-card" href="'+esc(path)+'" aria-label="'+esc('Artikel lesen: '+post['title'])+'"><img src="'+esc(post['image'])+'" alt="" width="280" height="308" loading="lazy"><div class="journal-teaser-copy"><span class="journal-category">'+esc(category)+'</span><h3>'+esc(short_titles.get(post['slug'],post['title']))+'</h3><span class="journal-card-arrow" aria-hidden="true">→</span></div></a></li>')
    return '''<section id="journal-teaser" aria-labelledby="journal-teaser-title">
  <div class="container">
    <div class="journal-teaser-heading">
      <div><span class="tag">Das Journal von M97 Factory</span><h2 id="journal-teaser-title">Neuigkeiten &amp; Artikel</h2></div>
      <div class="journal-teaser-actions">
        <a href="/aktuelles/" class="journal-all-link">Alle Geschichten ↗</a>
        <div class="journal-scroll-controls" hidden>
          <button type="button" data-journal-direction="-1" aria-label="Vorherige Artikel" aria-controls="journal-carousel">←</button>
          <button type="button" data-journal-direction="1" aria-label="Weitere Artikel" aria-controls="journal-carousel">→</button>
        </div>
      </div>
    </div>
    <ul id="journal-carousel" class="journal-carousel" tabindex="0" aria-label="Neuigkeiten und Artikel – horizontal blättern">
      '''+''.join(cards)+'''
    </ul>
  </div>
</section>'''
