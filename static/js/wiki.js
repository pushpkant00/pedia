(function () {
  var toc = document.getElementById('toc');
  var toggle = document.getElementById('toc-toggle');
  if (toc && toggle) {
    toggle.addEventListener('click', function () {
      var collapsed = toc.classList.toggle('collapsed');
      toggle.textContent = collapsed ? 'show' : 'hide';
      toggle.setAttribute('aria-expanded', String(!collapsed));
    });
  }

  var links = toc ? Array.prototype.slice.call(toc.querySelectorAll('a[href^="#"]')) : [];
  if (!links.length || !('IntersectionObserver' in window)) return;

  var targets = links
    .map(function (link) {
      return document.getElementById(decodeURIComponent(link.getAttribute('href').slice(1)));
    })
    .filter(Boolean);

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      links.forEach(function (link) { link.classList.remove('toc-active'); });
      var active = links.find(function (link) {
        return decodeURIComponent(link.getAttribute('href').slice(1)) === entry.target.id;
      });
      if (active) active.classList.add('toc-active');
    });
  }, { rootMargin: '0px 0px -70% 0px' });

  targets.forEach(function (target) { observer.observe(target); });
})();
