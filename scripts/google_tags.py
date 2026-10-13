"""Install the shared, consent-gated Google Ads integration on every public page."""
TAG_BLOCK = '''<!-- M97 Google Ads: consent-gated shared tag -->
<link rel="stylesheet" href="/assets/google-ads.css">
<script src="/assets/google-ads.js" defer></script>
<!-- /M97 Google Ads -->'''


def install(root):
    pages = list(root.glob('*.html'))
    for directory in ['aktuelles', 'magazin']:
        pages.extend((root/directory).rglob('*.html'))
    for page in pages:
        html = page.read_text(encoding='utf-8')
        if '<!-- M97 Google Ads:' in html:
            continue
        if '</head>' not in html:
            raise ValueError(f'{page}: missing HTML head')
        page.write_text(html.replace('</head>', TAG_BLOCK+'\n</head>', 1), encoding='utf-8')
