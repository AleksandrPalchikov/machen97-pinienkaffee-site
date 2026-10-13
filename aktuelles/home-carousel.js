(() => {
  const section = document.getElementById('journal-teaser');
  if (!section) return;
  const track = section.querySelector('.journal-carousel');
  const controls = section.querySelector('.journal-scroll-controls');
  const previous = controls.querySelector('[data-journal-direction="-1"]');
  const next = controls.querySelector('[data-journal-direction="1"]');
  controls.hidden = false;
  const update = () => {
    previous.disabled = track.scrollLeft <= 2;
    next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
  };
  const move = direction => {
    const card = track.querySelector('li');
    const distance = card.getBoundingClientRect().width + parseFloat(getComputedStyle(track).gap);
    track.scrollBy({ left: direction * distance, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
  };
  previous.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  track.addEventListener('keydown', event => {
    if (event.target !== track || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    move(event.key === 'ArrowRight' ? 1 : -1);
  });
  track.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  if ('ResizeObserver' in window) new ResizeObserver(update).observe(track);
  update();
})();
