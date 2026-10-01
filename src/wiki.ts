(function () {
  const toc = document.getElementById('toc');
  const toggle = document.getElementById('toc-toggle');

  if (toc && toggle) {
    toggle.addEventListener('click', function () {
      const collapsed = toc.classList.toggle('collapsed');
      toggle.textContent = collapsed ? 'show' : 'hide';
      toggle.setAttribute('aria-expanded', String(!collapsed));
    });
  }

  const links: HTMLAnchorElement[] = toc
    ? Array.from(toc.querySelectorAll<HTMLAnchorElement>('a[href^="#"]'))
    : [];
  if (!links.length || !('IntersectionObserver' in window)) return;

  const targets = links
    .map(function (link) {
      const href = link.getAttribute('href') || '';
      return document.getElementById(decodeURIComponent(href.slice(1)));
    })
    .filter((target): target is HTMLElement => target !== null);

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      links.forEach(function (link) {
        link.classList.remove('toc-active');
      });
      const active = links.find(function (link) {
        const href = link.getAttribute('href') || '';
        return decodeURIComponent(href.slice(1)) === entry.target.id;
      });
      if (active) active.classList.add('toc-active');
    });
  }, { rootMargin: '0px 0px -70% 0px' });

  targets.forEach(function (target) {
    observer.observe(target);
  });
})();
