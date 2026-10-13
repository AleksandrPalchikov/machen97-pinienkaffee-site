# Google Ads integration

Installed from the two user-provided snippets:

- Google tag: `AW-18508694079`.
- Conversion destination: `AW-18508694079/yj5xCMPTtJodEL-E0flE`.
- The provided conversion is named “Begin checkout”. Its existing destination is retained; on this site it measures a successful contact enquiry, not a purchase or actual checkout. No Google Ads account settings were changed.

`assets/google-ads.js` implements the shared tag with basic consent mode. Default consent is denied for `ad_storage`, `ad_user_data`, `ad_personalization` and `analytics_storage`. The external Google script is loaded only after approval. Approval grants advertising storage and advertising data, while personalization and analytics remain denied. The consent choice is stored for up to 180 days and can be changed through the page footer. Advertising cookies created by this integration are cleared on withdrawal. Existing Google Fonts are separate from this integration.

The conversion runs on `/danke` (also `/danke.html`), only when an actual successful Web3Forms response created a fresh submission marker after consent. The marker has a 30-minute eligibility window and no personal form fields. A random transaction ID plus a sent flag prevents duplicate events after a reload. A new successful submission gets a new ID. Direct visits, invalid forms, unsuccessful responses, rejected consent and blocked storage do not emit conversions. Messages still send and redirect when measurement is unavailable. Events that occurred without consent are not retrospectively tracked after later approval.

`scripts/google_tags.py` injects one local integration include into every public HTML page. `scripts/build-news.py` calls it after generation so future articles receive the tag automatically. Generated article HTML must not be edited by hand.

The privacy page describes this integration and provides the settings link. This implementation does not certify the entire site's legal compliance.

Primary implementation references, checked 13 October 2026:

- https://developers.google.com/tag-platform/security/guides/consent
- https://developers.google.com/tag-platform/security/concepts/consent-mode
- https://support.google.com/google-ads/answer/7548399
- https://support.google.com/google-ads/answer/6386790

Verification covers consent, tag ordering and ID, successful and failed forms, repeat submissions, direct thank-you visits, refresh deduplication, expired markers, withdrawal, blocked storage and responsive panels at 320/390/768/1440 pixels. Browser tests intercept Web3Forms and the Google tag, so no real messages or test conversions are transmitted. Account-side attribution and reporting must be observed on real consented visitor traffic.
