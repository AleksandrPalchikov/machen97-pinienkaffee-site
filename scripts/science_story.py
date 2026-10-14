"""Accessible science editorial with traceable citations and scoped presentation."""
from datetime import datetime
import json
import re
from urllib.parse import urlparse
import editorial as e


def references():
    items = json.loads((e.ROOT / 'content/editorial/pinienkerne-studien.json').read_text())
    ids = [item['id'] for item in items]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate scientific reference')
    for item in items:
        url = urlparse(item['url'])
        if url.scheme != 'https' or not url.netloc:
            raise ValueError('Scientific references require HTTPS source URLs')
    return items


def prose(markdown, ids):
    def citation(match):
        number = int(match[1])
        if number not in ids:
            raise ValueError(f'Unknown scientific reference {number}')
        return f'<sup class="science-citation"><a href="#quelle-{number}" aria-label="Wissenschaftliche Quelle {number}">[{number}]</a></sup>'
    return re.sub(r'\[(\d+)\]', citation, e.blocks(markdown))


def render(post):
    refs = references()
    ids = {item['id'] for item in refs}
    intro, remaining = post['body'].split('\n## ', 1)
    story, questions = ('## ' + remaining).split('## Häufige Fragen', 1)
    chapters = re.findall(r'## (\d{2}) · (.+?)\n(.*?)(?=\n## |\Z)', story, re.S)
    pairs = [(q.strip(), a.strip()) for q, a in re.findall(r'### (.+?)\n(.*?)(?=\n### |\Z)', questions, re.S)]
    if not chapters or not pairs or set(map(int, re.findall(r'\[(\d+)\]', story))) != ids:
        raise ValueError('Science story needs chapters, FAQ and every listed reference')
    minutes = max(1, round(len(post['body'].split()) / 180))
    byline = 'Redaktioneller Entwurf' if post['status'] == 'draft' else e.esc(post['author']) + ' · <time datetime="' + e.esc(post['published']) + '">' + datetime.fromisoformat(post['published']).strftime('%d.%m.%Y') + '</time>'
    body = '<nav class="breadcrumbs" aria-label="Brotkrümelnavigation"><a href="/">Startseite</a><span>/</span><a href="/aktuelles/">Journal</a><span>/</span><span>Wissen &amp; Forschung</span></nav><article class="editorial science-story"><header class="story-heading"><span class="eyebrow">Wissen &amp; Forschung · Pinienkerne verstehen</span><h1>' + e.inline(post['heading']) + '</h1><div class="standfirst">' + e.blocks(intro) + '</div><p class="byline">' + byline + ' · ' + str(minutes) + ' Minuten Lesezeit</p></header>'
    ingredient = e.manifest()['ingredient-pine-nuts']
    stem = ingredient['file'].removesuffix('.webp')
    body += '<figure class="photo science-hero"><img src="' + e.esc(ingredient['file']) + '" srcset="' + stem + '-640.webp 640w, ' + stem + '-1280.webp 1280w, ' + ingredient['file'] + ' 1920w" sizes="(max-width: 700px) 100vw, 90vw" width="1920" height="1280" alt="Pinienkerne in einer Holzschale mit Holzlöffel – Zutaten-Stimmungsbild" fetchpriority="high" decoding="async"><figcaption>Zutaten-Stimmungsbild · Victoria Bowers / Pexels. Keine Aufnahme unseres Rohstoffs. <a href="' + e.esc(ingredient['source']) + '" target="_blank" rel="noopener noreferrer">Fotoquelle ↗</a></figcaption></figure>'
    body += '<aside class="science-compass" aria-label="Drei Fragen an die Forschung"><div><span class="eyebrow">Der Kern</span><h2>Was steckt drin?</h2><p>Eine Analyse beschreibt Inhaltsstoffe.</p></div><div><span class="eyebrow">Die Studie</span><h2>Was wurde geprüft?</h2><p>Menschen, Tiere, ganze Nüsse oder Öl?</p></div><div><span class="eyebrow">Deine Tasse</span><h2>Was gilt für den Latte?</h2><p>51 % sind ein Zutatenanteil, kein Wirkungsnachweis.</p></div></aside>'
    body += '<nav class="science-toc" aria-label="Themen dieses Beitrags"><span class="eyebrow">Dein Weg durch den Beitrag</span><ol>' + ''.join('<li><a href="#wissen-' + number + '"><span>' + number + '</span>' + e.esc(title) + '</a></li>' for number, title, _ in chapters) + '</ol></nav>'
    for number, title, copy in chapters:
        body += '<section class="science-chapter" id="wissen-' + number + '"><div class="science-chapter-heading"><span class="recipe-number">' + number + '</span><h2>' + e.esc(title) + '</h2></div><div class="prose science-copy">' + prose(copy, ids) + '</div>'
        if number == '06':
            body += '<aside class="science-portion" aria-label="Rechnerische Ausgangsmenge vor dem Aufgießen"><span class="eyebrow">Ein Blick auf die Portion</span><div><span>22–25 g<br><small>Mischung</small></span><span aria-hidden="true">×</span><span>51 %<br><small>Pinienkerne</small></span><span aria-hidden="true">=</span><span>11,2–12,8 g<br><small>Pinienkerne im Pulver</small></span></div><p>Vor dem Aufgießen. Keine Nährstoffmenge im gefilterten Getränk.</p></aside>'
        body += '</section>'
    body += e.faq(pairs)
    body += '<section class="science-sources" id="quellen"><span class="eyebrow">Zum Nachlesen · Stand 14.10.2026</span><h2>Die Forschung hinter dem Text.</h2><p>Die Zahlen im Beitrag führen zu diesen Originalarbeiten. Die Einordnung zeigt jeweils, was untersucht wurde. Keine der aufgeführten Arbeiten untersucht PINE NUT LATTE.</p><ol>'
    for item in refs:
        body += '<li id="quelle-' + str(item['id']) + '" tabindex="-1"><span class="eyebrow">' + e.esc(item['kind']) + '</span><h3><a href="' + e.esc(item['url']) + '" target="_blank" rel="noopener noreferrer">' + e.esc(item['title']) + ' ↗</a></h3><p class="science-reference-meta">' + e.esc(item['authors']) + ' · ' + str(item['year']) + ' · ' + e.esc(item['journal']) + '</p><p>' + e.esc(item['note']) + '</p><a class="science-doi" href="https://doi.org/' + e.esc(item['doi']) + '" target="_blank" rel="noopener noreferrer">DOI: ' + e.esc(item['doi']) + '</a></li>'
    body += '</ol><p class="science-source-note">Angaben zur Rezeptur und Zubereitung beruhen auf den von M97 Factory bereitgestellten Produktinformationen. Allgemeine Rohstoffanalysen sind keine Nährwertanalyse des aufgegossenen Getränks.</p></section>'
    body += '<aside class="production-reading"><span class="eyebrow">Mehr über unseren Kern</span><h2>Die Geschichte geht weiter.</h2><div><a href="/magazin/pine-nut-latte-herstellung/">Vom Zapfen bis in deine Tasse: die Herstellung →</a><a href="/aktuelles/pinienkaffee-zubereiten/">PINE NUT LATTE richtig zubereiten →</a><a href="' + e.RECIPES + '">7 experimentelle Ideen für neue Geschmackserlebnisse →</a><a href="/#shop">Classic und mit Gewürzen kennenlernen →</a></div></aside><a class="back-link" href="/aktuelles/">← Alle Geschichten</a></article>'
    url = e.BASE + post['path']
    publisher = {'@type': 'Organization', 'name': 'M97 Factory', 'url': e.BASE}
    schema = {'@type': 'BlogPosting', '@id': url + '#article', 'url': url, 'headline': post['heading'], 'description': post['description'], 'image': [e.BASE + post['image']], 'mainEntityOfPage': {'@id': url}, 'inLanguage': 'de-DE', 'articleSection': 'Wissen & Forschung', 'author': publisher, 'publisher': publisher, 'keywords': ['Pinienkerne', 'Pinienkerne Nährstoffe', 'Pinienkerne Verdauung', 'Pinienkernöl Forschung', 'PINE NUT LATTE', 'Pinienkaffee'], 'citation': [{'@type': 'ScholarlyArticle', 'name': item['title'], 'url': item['url'], 'identifier': 'https://doi.org/' + item['doi']} for item in refs]}
    if post['status'] == 'published':
        schema.update(datePublished=post['published'], dateModified=post['modified'])
    graph = [{'@type': 'WebPage', '@id': url, 'url': url, 'name': post['title'], 'inLanguage': 'de-DE'}, {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Startseite', 'item': e.BASE + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Journal', 'item': e.BASE + '/aktuelles/'}, {'@type': 'ListItem', 'position': 3, 'name': post['title'], 'item': url}]}, schema, {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in pairs]}]
    return e.shell(post['title'] + ' | M97 Factory', post['description'], post['path'], body, graph, post['image'], post['status'] == 'draft')
