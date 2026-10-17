/* Google Ads measurement: basic consent mode; no Google requests before consent. */
(() => {
  'use strict';
  const TAG = 'AW-18508694079';
  const ANALYTICS = 'G-531CMKHRTX';
  const GTM = 'GTM-3NTP6CFV';
  const CONVERSION = TAG + '/yj5xCMPTtJodEL-E0flE';
  const CHOICE = 'm97-ad-consent-v2';
  const SUBMISSION = 'm97-contact-conversion-v1';
  const CONSENT_AGE = 180 * 24 * 60 * 60 * 1000;
  const SUBMISSION_AGE = 30 * 60 * 1000;
  let consent = readChoice();
  let loaded = false;
  let gtmLoaded = false;
  let banner;
  let previousFocus;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('consent', 'default', {
    ad_storage: 'denied', ad_user_data: 'denied',
    ad_personalization: 'denied', analytics_storage: 'denied'
  });

  function readChoice() {
    try {
      const value = JSON.parse(localStorage.getItem(CHOICE));
      if (value && ['granted', 'denied'].includes(value.value) &&
          Number.isFinite(value.at) && value.at <= Date.now() && Date.now() - value.at < CONSENT_AGE) return value.value;
    } catch (_) { /* Storage can be disabled without affecting the contact form. */ }
    return null;
  }

  function loadTag() {
    if (loaded || consent !== 'granted') return;
    loaded = true;
    window.gtag('consent', 'update', {
      ad_storage: 'granted', ad_user_data: 'granted',
      ad_personalization: 'denied', analytics_storage: 'granted'
    });
    window.gtag('js', new Date());
    window.gtag('config', TAG, {
      allow_ad_personalization_signals: false, allow_google_signals: false
    });
    window.gtag('config', ANALYTICS, {
      allow_google_signals: false, allow_ad_personalization_signals: false
    });
    loadGtm();
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + TAG;
    document.head.appendChild(script);
    sendConversion();
  }

  function loadGtm() {
    if (gtmLoaded || consent !== 'granted') return;
    gtmLoaded = true;
    // GTM shares this dataLayer with the consent-gated Google tag. The page event
    // excludes query parameters and fires only after analytics consent.
    window.dataLayer.push({'gtm.start': Date.now(), event: 'gtm.js'});
    window.dataLayer.push({
      event: 'm97_page_view',
      page_path: location.pathname,
      page_title: document.title
    });
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtm.js?id=' + GTM;
    document.head.appendChild(script);
  }

  function sendConversion() {
    // Direct visits and reloads of the thank-you page must not create new leads.
    if (consent !== 'granted' || !/^\/danke(?:\.html)?\/?$/.test(location.pathname)) return;
    try {
      const submission = JSON.parse(sessionStorage.getItem(SUBMISSION));
      if (!submission || submission.sent || typeof submission.id !== 'string' ||
          !/^[a-zA-Z0-9-]{10,80}$/.test(submission.id) || !Number.isFinite(submission.at) ||
          submission.at > Date.now() || Date.now() - submission.at > SUBMISSION_AGE) return;
      submission.sent = true;
      sessionStorage.setItem(SUBMISSION, JSON.stringify(submission));
      window.dataLayer.push({
        event: 'm97_generate_lead',
        form_name: 'contact',
        page_path: location.pathname
      });
      window.dataLayer.push({
        event: 'm97_ads_conversion',
        conversion_label: 'begin_checkout',
        page_path: location.pathname
      });
      window.gtag('event', 'conversion', {
        send_to: CONVERSION, transaction_id: submission.id
      });
      window.gtag('event', 'generate_lead', {send_to: ANALYTICS});
    } catch (_) { /* An unavailable storage must never interrupt a successful submission. */ }
  }

  function recordSuccessfulSubmission() {
    if (consent !== 'granted') return;
    try {
      const id = window.crypto && typeof window.crypto.randomUUID === 'function'
        ? window.crypto.randomUUID()
        : Date.now().toString(36) + '-' + Math.random().toString(36).slice(2);
      // A short-lived success marker, never form fields or personal information.
      sessionStorage.setItem(SUBMISSION, JSON.stringify({id, at: Date.now(), sent: false}));
    } catch (_) { /* Sending the message and redirecting remain functional. */ }
  }

  function clearGoogleCookies() {
    const hostname = location.hostname;
    const domains = ['', hostname, '.' + hostname];
    if (hostname.startsWith('www.')) domains.push(hostname.slice(4), '.' + hostname.slice(4));
    document.cookie.split(';').forEach(cookie => {
      const name = cookie.trim().split('=')[0];
      if (!name.startsWith('_gcl_') && name !== '_ga' && !name.startsWith('_ga_')) return;
      domains.forEach(domain => {
        document.cookie = name + '=; Max-Age=0; path=/' + (domain ? '; domain=' + domain : '') + '; SameSite=Lax';
      });
    });
  }

  function choose(value) {
    consent = value;
    try { localStorage.setItem(CHOICE, JSON.stringify({value, at: Date.now()})); } catch (_) {}
    banner.hidden = true;
    if (previousFocus && document.contains(previousFocus)) previousFocus.focus();
    if (value === 'granted') loadTag();
    else {
      clearGoogleCookies();
      try { sessionStorage.removeItem(SUBMISSION); } catch (_) {}
      if (loaded) {
        window.gtag('consent', 'update', {
          ad_storage: 'denied', ad_user_data: 'denied',
          ad_personalization: 'denied', analytics_storage: 'denied'
        });
        // Reload without the Google tag after a previously granted consent is withdrawn.
        location.reload();
      }
    }
  }

  function showPreferences() {
    previousFocus = document.activeElement;
    banner.hidden = false;
    banner.querySelector('button').focus();
  }

  function mount() {
    banner = document.createElement('section');
    banner.id = 'm97-consent';
    banner.hidden = true;
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-labelledby', 'm97-consent-title');
    banner.innerHTML = '<div class="m97-consent-copy"><h2 id="m97-consent-title">Deine Datenschutzwahl</h2>' +
      '<p>Mit deiner Zustimmung nutzen wir Google Analytics zur Reichweitenmessung und Google Ads zur Anzeigenmessung. ' +
      'Dabei können Nutzungsdaten an Google übermittelt werden. Du kannst deine Wahl jederzeit ändern.</p>' +
      '<a href="/datenschutz.html#google-ads">Mehr zum Datenschutz</a></div>' +
      '<div class="m97-consent-actions"><button type="button" data-m97-choice="denied">Ablehnen</button>' +
      '<button type="button" data-m97-choice="granted">Zustimmen</button></div>';
    banner.querySelectorAll('[data-m97-choice]').forEach(button => {
      button.addEventListener('click', () => choose(button.dataset.m97Choice));
    });
    document.body.appendChild(banner);
    const settings = document.createElement('button');
    settings.type = 'button';
    settings.className = 'm97-privacy-settings';
    settings.textContent = 'Datenschutz-Einstellungen';
    settings.addEventListener('click', showPreferences);
    const footer = document.querySelector('footer');
    if (footer) footer.appendChild(settings);
    else document.body.appendChild(settings);
    if (consent === null) banner.hidden = false;
  }

  window.M97Ads = Object.freeze({ recordSuccessfulSubmission, openPreferences: showPreferences });
  window.addEventListener('storage', event => {
    if (event.key !== CHOICE) return;
    const next = readChoice();
    if (next === consent) return;
    consent = next;
    if (loaded && next !== 'granted') {
      clearGoogleCookies();
      location.reload();
    } else {
      if (banner) banner.hidden = next !== null;
      loadTag();
    }
  });
  loadTag();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, {once: true});
  else mount();
})();
