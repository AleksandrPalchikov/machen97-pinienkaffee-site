"""Production reportage, separated from existing article templates."""
from datetime import datetime
import json
import re
import editorial as e


def photos():
    return {p['name']: p for p in json.loads((e.ROOT/'content/editorial/production-images.json').read_text())}


def photo(name, hero=False):
    item=photos()[name];stem=item['file'].removesuffix('.webp')
    widths=item['variant_widths']
    srcset=f'{stem}-640.webp {widths[0]}w, {stem}-1280.webp {widths[1]}w, {stem}.webp {widths[2]}w'
    return '<figure class="photo '+('hero-photo' if hero else '')+'"><img src="'+item['file']+'" srcset="'+srcset+'" sizes="'+('100vw' if hero else '(max-width: 700px) 100vw, 45vw')+'" width="'+str(item['width'])+'" height="'+str(item['height'])+'" alt="'+e.esc(item['alt'])+'" '+('fetchpriority="high"' if hero else 'loading="lazy"')+' decoding="async"><figcaption>'+e.esc(item['caption'])+'</figcaption></figure>'


def render(post):
    intro,remaining=post['body'].split('\n## ',1)
    story,faq_text=('## '+remaining).split('## Häufige Fragen',1)
    chapters=re.findall(r'## (\d{2}) · (.+?)\n(.*?)(?=\n## |\Z)',story,re.S)
    pairs=[(q.strip(),a.strip()) for q,a in re.findall(r'### (.+?)\n(.*?)(?=\n### |\Z)',faq_text,re.S)]
    if len(chapters)!=10 or len(pairs)!=6:raise ValueError('Production story requires ten chapters and six FAQ answers')
    byline='M97 Factory · Redaktioneller Entwurf' if post['status']=='draft' else post['author']+' · '+datetime.fromisoformat(post['published']).strftime('%d.%m.%Y')
    minutes=max(1,round(len(post['body'].split())/180))
    body='<nav class="breadcrumbs" aria-label="Brotkrümelnavigation"><a href="/">Startseite</a><span>/</span><a href="/aktuelles/">Journal</a><span>/</span><span>Herkunft &amp; Handwerk</span></nav><article class="editorial production-story"><header class="story-heading"><span class="eyebrow">Herkunft &amp; Handwerk · Eine Reise mit M97 Factory</span><h1>'+e.inline(post['heading'])+'</h1><div class="standfirst">'+e.blocks(intro)+'</div><p class="byline">'+e.esc(byline)+' · '+str(minutes)+' Minuten Lesezeit</p></header>'+photo('m97-pine-nut-latte-pinienkerne-sortierung',True)
    body+='<div class="production-facts" aria-label="Das Produkt in Kürze"><div><strong>51 %</strong><span>Pinienkerne laut Vorderetikett</span></div><div><strong>250 g</strong><span>Classic &amp; mit Gewürzen</span></div><div><strong>Von Hand</strong><span>Die Ernte am Anfang der Reise</span></div></div>'
    names=['Handernte','Der Kern','Ankunft','Sortierung','Wärme','Mahlen','Rezeptur','Verpackung','Deine Tasse','Was bleibt']
    body+='<nav class="production-route" aria-label="Stationen der Herstellung"><span class="eyebrow">Folge dem Kern</span><ol>'+''.join('<li><a href="#station-'+num+'"><span>'+num+'</span>'+e.esc(names[int(num)-1])+'</a></li>' for num,_,_ in chapters)+'</ol></nav>'
    chapter_images={1:'m97-pinienkerne-in-schale-siebung',3:'m97-pinienkerne-feuchtigkeitskontrolle',6:'m97-pine-nut-latte-mahlanlage',8:'m97-pine-nut-latte-schneckendosierung-abfuellung'}
    for num,title,copy in chapters:
        n=int(num);heading='<div class="production-chapter-title"><span class="recipe-number">'+num+'</span><h2>'+e.esc(title)+'</h2></div>'
        body+='<section id="station-'+num+'" class="production-chapter'+(' has-photo' if n in chapter_images else '')+'">'+heading
        text='<div class="production-copy">'+e.blocks(copy)+'</div>'
        if n in chapter_images:body+='<div class="production-chapter-layout">'+text+photo(chapter_images[n])+'</div>'
        else:body+=text
        if n==4:body+='<div class="production-diptych">'+photo('m97-pinienkerne-schalen-abtrennung')+photo('m97-pinienkerne-optische-sortierung-steuerung')+'</div>'
        if n==5:body+='<aside class="production-temperature" aria-label="Drei Schritte aus der Prozessbeschreibung"><div><span>Trocknen</span><strong>50–55 °C</strong><small>90–120 Minuten</small></div><div><span>Leicht rösten</span><strong>150–160 °C</strong><small>15–20 Minuten</small></div><div><span>Abkühlen</span><strong>≤ 35 °C</strong><small>Vor dem Mahlen</small></div></aside>'
        if n==7:body+='<div class="production-labels">'+e.image('label-classic')+e.image('label-spiced')+'</div>'
        body+='</section>'
    body+=e.faq(pairs)
    body+='<section class="production-sources prose"><span class="eyebrow">Die Grundlage dieser Geschichte</span><h2>Zum Nachlesen</h2><p>Die betrieblichen Schritte und Prozessbereiche beruhen auf der von M97 Factory bereitgestellten technischen Beschreibung. Die Handernte wird nach Angaben von M97 Factory beschrieben. Anlagen- und Rohstoffbilder stammen aus dem für diesen Beitrag bereitgestellten Material; die Vorderetiketten sind separat abgebildet. Die Fotos belegen keinen Produktionsstandort und keine lückenlose Verarbeitung einer einzelnen Charge.</p><p>Allgemeine botanische und verarbeitungstechnische Hintergründe:</p><ul><li><a href="https://powo.science.kew.org/taxon/urn%3Alsid%3Aipni.org%3Anames%3A263037-1" target="_blank" rel="noopener noreferrer">Royal Botanic Gardens, Kew · Pinus koraiensis</a></li><li><a href="https://www.kew.org/plants/stone-pine" target="_blank" rel="noopener noreferrer">Royal Botanic Gardens, Kew · Die Mittelmeer-Pinie</a></li><li><a href="https://www.fao.org/4/ad232e/ad232e06.htm" target="_blank" rel="noopener noreferrer">FAO · Gewinnung und Aufbereitung von Baumsamen</a></li></ul><p>Diese allgemeinen Quellen beschreiben Baumarten und Verfahren. Sie bestätigen keine Herkunft oder Zertifizierung unserer Lieferchargen.</p></section>'
    body+=e.cta()+'<aside class="production-reading"><span class="eyebrow">Deine nächste Entdeckung</span><h2>Von der Geschichte zum Genuss.</h2><div><a href="/aktuelles/pinienkaffee-zubereiten/">Die Standardzubereitung kennenlernen →</a><a href="'+e.RECIPES+'">7 experimentelle Rezeptideen entdecken →</a><a href="'+e.RENAME+'">Warum Pinienkaffee jetzt PINE NUT LATTE heißt →</a></div></aside><a class="back-link" href="/aktuelles/">← Alle Geschichten</a></article>'
    graph=[{'@type':'WebPage','@id':e.BASE+post['path'],'url':e.BASE+post['path'],'name':post['title'],'inLanguage':'de-DE'},
           {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Startseite','item':e.BASE+'/'},{'@type':'ListItem','position':2,'name':'Journal','item':e.BASE+'/aktuelles/'},{'@type':'ListItem','position':3,'name':post['title'],'item':e.BASE+post['path']}]},
           {'@type':'BlogPosting','headline':post['title'],'description':post['description'],'image':[e.BASE+post['image']],'mainEntityOfPage':{'@id':e.BASE+post['path']},'inLanguage':'de-DE','articleSection':'Herkunft & Handwerk','author':{'@type':'Organization','name':'M97 Factory'},'publisher':{'@type':'Organization','name':'M97 Factory','url':e.BASE},'keywords':['PINE NUT LATTE','Pinienkaffee Herstellung','Pinienkerne','Kaffeealternative ohne Koffein','Besondere Heißgetränke']},
           {'@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in pairs]}]
    if post['status']=='published':graph[2].update(datePublished=post['published'],dateModified=post['modified'])
    return e.shell(post['title']+' | M97 Factory',post['description'],post['path'],body,graph,post['image'],post['status']=='draft')
