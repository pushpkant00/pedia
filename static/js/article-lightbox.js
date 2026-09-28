(function () {
  'use strict';
  var lb = document.getElementById('article-lightbox');
  if (!lb) return;
  var imgEl = document.getElementById('lightbox-img');
  var captionEl = document.getElementById('lightbox-caption');
  var downloadLink = lb.querySelector('.lightbox-download');
  var closeBtn = lb.querySelector('.lightbox-close');
  var body = document.querySelector('.article-body');

  function open(src, alt, index, total) {
    imgEl.src = src;
    imgEl.alt = alt || '';
    downloadLink.href = src;
    downloadLink.setAttribute('download', (src.split('/').pop() || 'image').replace(/\?.*$/, ''));
    captionEl.textContent = (total > 1 ? 'Image ' + index + ' / ' + total + ' — ' : '') + (alt || 'Image');
    lb.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
  function close() {
    lb.classList.remove('active');
    imgEl.src = '';
    document.body.style.overflow = '';
  }
  if (body) {
    body.addEventListener('click', function (e) {
      var img = e.target.closest ? e.target.closest('.article-body img, article img') : null;
      if (!img) return;
      var imgs = Array.from(body.querySelectorAll('img'));
      var idx = imgs.indexOf(img) + 1;
      open(img.src, img.alt || '', idx, imgs.length);
      e.preventDefault();
    });
  }
  closeBtn.addEventListener('click', close);
  downloadLink.addEventListener('click', function () { /* native download via href/download */ });
  lb.addEventListener('click', function (e) {
    if (e.target === lb || e.target.classList.contains('lightbox-backdrop')) close();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' || e.key === 'Esc') {
      if (lb.classList.contains('active')) close();
    }
  });
})();
