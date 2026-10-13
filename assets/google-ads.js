/* Google Ads measurement: basic consent mode; no Google requests before consent. */
(() => {
  'use strict';
  const TAG = 'AW-18508694079';
  const CONVERSION = TAG + '/yj5xCMPTtJodEL-E0flE';
  const CHOICE = 'm97-ad-consent-v1';
  const SUBMISSION = 'm97-contact-conversion-v1';
  const CONSENT_AGE = 180 * 24 * 60 * 60 * 1000;
  const SUBMISSION_AGE = 30 * 60 * 1000;
  let consent = readChoice();
  let loaded = false;
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
      ad_personalization: 'denied', analytics_storage: 'denied'
    });
    window.gtag('js', new Date());
    window.gtag('config', TAG, {
      allow_ad_personalization_signals: false, allow_google_signals: false
    });
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + TAG;
    document.head.appendChild(script);
    sendConversion();
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
      window.gtag('event', 'conversion', {
        send_to: CONVERSION, transaction_id: submission.id
      });
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

  function clearAdCookies() {
    const hostname = location.hostname;
    const domains = ['', hostname, '.' + hostname];
    if (hostname.startsWith('www.')) domains.push(hostname.slice(4), '.' + hostname.slice(4));
    document.cookie.split(';').forEach(cookie => {
      const name = cookie.trim().split('=')[0];
      if (!name.startsWith('_gcl_')) return;
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
      clearAdCookies();
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
      '<p>Mit deiner Zustimmung nutzen wir Google Ads und Werbe-Cookies, um den Erfolg unserer Anzeigen zu messen. ' +
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
      clearAdCookies();
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
