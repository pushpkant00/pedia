(function () {
  'use strict';

  const lbEl = document.getElementById('article-lightbox');
  if (!lbEl) return;
  const lb: HTMLElement = lbEl;

  const imgEl = document.getElementById('lightbox-img') as HTMLImageElement | null;
  const captionEl = document.getElementById('lightbox-caption');
  const downloadLink = lb.querySelector<HTMLAnchorElement>('.lightbox-download');
  const closeBtn = lb.querySelector<HTMLElement>('.lightbox-close');
  const body = document.querySelector('.article-body');

  function open(src: string, alt: string, index: number, total: number): void {
    try {
      if (!imgEl) return;
      imgEl.src = src || '';
      imgEl.alt = alt || '';
      if (downloadLink) {
        downloadLink.href = src || '#';
        try {
          const name = (String(src).split('/').pop() || 'image').replace(/\?.*$/, '');
          downloadLink.setAttribute('download', name);
        } catch { /* filename from exotic URL — skip */ }
      }
      if (captionEl) {
        captionEl.textContent = (total > 1 ? `Image ${index} / ${total} — ` : '') + (alt || 'Image');
      }
      lb.classList.add('active');
      document.body.style.overflow = 'hidden';
    } catch (error) {
      console.error('[pedia lightbox] open failed', error);
      document.body.style.overflow = '';
    }
  }

  function close(): void {
    lb.classList.remove('active');
    if (imgEl) imgEl.src = '';
    document.body.style.overflow = '';
  }

  if (body) {
    body.addEventListener('click', function (event) {
      const e = event as MouseEvent;
      const target = e.target as Element | null;
      const img = target && target.closest
        ? target.closest<HTMLImageElement>('.article-body img, article img')
        : null;
      if (!img) return;
      // Skip broken/missing images to avoid frozen overlay.
      if (!img.src || (img.complete && img.naturalWidth === 0)) return;
      const imgs = Array.from(body.querySelectorAll<HTMLImageElement>('img'));
      const idx = imgs.indexOf(img) + 1;
      open(img.src, img.alt || '', idx, imgs.length);
      e.preventDefault();
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', close);
  }
  if (downloadLink) {
    // Native download happens through the href/download attributes set in open().
    downloadLink.addEventListener('click', function () { /* no-op */ });
  }
  lb.addEventListener('click', function (event) {
    const e = event as MouseEvent;
    const target = e.target as Element | null;
    if (target === lb || (target && target.classList.contains('lightbox-backdrop'))) {
      close();
    }
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' || event.key === 'Esc') {
      if (lb.classList.contains('active')) close();
    }
  });
})();
