(function () {
  var results = [], errors = [];
  function rec(t, ok, d) {
    results.push({ t: t, ok: !!ok, d: (d === undefined ? null : d) });
    var el = document.getElementById('selftest-results');
    if (el) el.textContent = 'LIVESTEP:' + t + ':' + (ok ? 'ok' : 'no');
  }
  function finish() {
    var el = document.getElementById('selftest-results');
    if (!el) {
      el = document.createElement('div');
      el.id = 'selftest-results';
      document.body.appendChild(el);
    }
    var pass = results.every(function (r) { return r.ok; });
    el.textContent = 'RESULTS:' + JSON.stringify({
      status: pass ? 'PASS' : 'FAIL', results: results, errors: errors
    });
  }
  function recErr(m) { errors.push(String(m).slice(0, 300)); }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function waitFor(fn, timeout) {
    timeout = timeout || 12000;
    var start = Date.now();
    return new Promise(function (resolve) {
      (function poll() {
        var v;
        try { v = fn(); } catch (e) { v = null; }
        if (v) return resolve(v);
        if (Date.now() - start > timeout) return resolve(null);
        setTimeout(poll, 120);
      })();
    });
  }

  var tries = 0;
  (function poll() {
    try {
      if (window.__pediaEditor && document.readyState === 'complete') return run();
      if (++tries > 250) { rec('editor-init', false, 'timeout'); return finish(); }
    } catch (e) { recErr('poll:' + e); }
    setTimeout(poll, 100);
  })();

  async function run() {
    try {
      rec('editor-init', true);
      window.addEventListener('error', function (e) { recErr('win:' + (e.message || e) + ' | ' + ((e.error && e.error.stack) || '').slice(0, 200)); });
      var alertLog = [];
      window.alert = function (m) { alertLog.push(String(m).slice(0, 200)); };
      var fetchLog = [];
      var origFetch = window.fetch;
      window.fetch = function () {
        var url = String(arguments[0]);
        var p = origFetch.apply(this, arguments);
        p.then(function (r) { fetchLog.push(url + ' -> ' + r.status); },
               function (e) { fetchLog.push(url + ' -> ERR ' + e); });
        return p;
      };

      var btn = document.querySelector('[aria-label="Insert image"]') ||
        Array.from(document.querySelectorAll('.toastui-editor-toolbar button')).filter(function (b) {
          return /image/i.test(b.className + ' ' + (b.getAttribute('aria-label') || ''));
        })[0];
      if (!btn) { rec('image-button-found', false, 'missing'); return finish(); }
      var br = btn.getBoundingClientRect();
      btn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, clientX: br.left + 5, clientY: br.top + 5 }));
      btn.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, clientX: br.left + br.width / 2, clientY: br.top + br.height / 2 }));
      btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, clientX: br.left + br.width / 2, clientY: br.top + br.height / 2 }));

      var input = await waitFor(function () { return document.getElementById('toastuiImageFileInput'); }, 6000);
      rec('file-input-in-popup', !!input, input ? { multiple: input.multiple } : 'not found');
      if (input) {
        await waitFor(function () { return input.multiple ? true : null; }, 3000);
        rec('file-input-allows-multiple', input.multiple === true, 'multiple=' + input.multiple);
      }
      if (!input) return finish();

      var before = document.querySelectorAll('.ProseMirror img').length;
      rec('baseline-img-count', before >= 1, 'count=' + before);

      function makeDt(names) {
        var bytes = Uint8Array.from(atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='), function (c) { return c.charCodeAt(0); });
        var dt = new DataTransfer();
        names.forEach(function (n) { dt.items.add(new File([bytes], n, { type: 'image/png' })); });
        return dt;
      }
      function clickOk() {
        var ok = document.querySelector('.toastui-editor-popup [class*="ok-button"]') ||
          Array.from(document.querySelectorAll('.toastui-editor-popup button')).filter(function (b) {
            return /ok-button/.test(b.className);
          })[0];
        if (!ok) return false;
        var r = ok.getBoundingClientRect();
        var ev = { bubbles: true, cancelable: true, clientX: r.left + 5, clientY: r.top + 5 };
        ok.dispatchEvent(new MouseEvent('mousedown', ev));
        ok.dispatchEvent(new MouseEvent('mouseup', ev));
        ok.dispatchEvent(new MouseEvent('click', ev));
        return true;
      }

      try {
        input.files = makeDt(['multi-a.png', 'multi-b.png']).files;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        rec('ok-clicked', clickOk());
      } catch (e) {
        rec('ok-clicked', false, String(e));
      }

      await waitFor(function () {
        return document.querySelectorAll('.ProseMirror img').length > before;
      }, 8000);
      await sleep(1500);
      var after = document.querySelectorAll('.ProseMirror img').length;
      rec('two-files-inserted', after === (before + 2), 'before=' + before + ' after=' + after);
      rec('fetch-log', true, fetchLog.slice(0, 6));
      rec('alerts', alertLog.length === 0, alertLog.slice(0, 4));

      // single-file regression: reopen popup, pick one file, OK
      try {
        btn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, clientX: br.left + 5, clientY: br.top + 5 }));
        btn.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, clientX: br.left + br.width / 2, clientY: br.top + br.height / 2 }));
        btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, clientX: br.left + br.width / 2, clientY: br.top + br.height / 2 }));
        var input2 = await waitFor(function () { return document.getElementById('toastuiImageFileInput'); }, 6000);
        if (!input2) throw new Error('popup did not reopen');
        await sleep(700);
        for (var attempt = 0; attempt < 4; attempt++) {
          input2 = document.getElementById('toastuiImageFileInput') || input2;
          input2.files = makeDt(['single-c.png']).files;
          if (input2.files.length === 1) break;
          await sleep(400);
        }
        if (input2.files.length === 1) {
          input2.dispatchEvent(new Event('input', { bubbles: true }));
          input2.dispatchEvent(new Event('change', { bubbles: true }));
        }
        rec('single-files-ready', input2.files.length === 1, 'files=' + input2.files.length);
        rec('single-ok-clicked', input2.files.length === 1 && clickOk());
      } catch (e) {
        rec('single-ok-clicked', false, String(e));
      }
      var singleTarget = (after || before) + 1;
      await waitFor(function () {
        return document.querySelectorAll('.ProseMirror img').length >= singleTarget;
      }, 8000);
      await sleep(800);
      var afterSingle = document.querySelectorAll('.ProseMirror img').length;
      rec('single-file-inserted', afterSingle === singleTarget, 'after=' + afterSingle + ' expected=' + singleTarget);

      var popup = document.querySelector('.toastui-editor-popup');
      var popupState = !popup ? 'missing' :
        (popup.style.display === 'none' || getComputedStyle(popup).display === 'none') ? 'closed' : 'open';
      rec('popup-closed-after-insert', popupState === 'closed', popupState);

      var findCont = function () {
        var holder = document.getElementById('editor');
        var nodes = [holder].concat(Array.from(holder.querySelectorAll('*')));
        for (var i = 0; i < nodes.length; i++) {
          var el = nodes[i];
          if (el.scrollHeight > el.clientHeight + 40 && el.clientHeight > 150) return el;
        }
        return null;
      };
      var cont = findCont();
      rec('scroll-container-found', !!cont, cont ? ('class=' + cont.className) : 'none');
      if (!cont) return finish();

      cont.scrollTop = 420;
      await sleep(500);

      var clickRes = await (async function () {
        var imgs = Array.from(document.querySelectorAll('.ProseMirror img'));
        if (!imgs.length) return { err: 'no imgs' };
        imgs.sort(function (a, b) {
          var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
          return (rb.width * rb.height) - (ra.width * ra.height);
        });
        var img = imgs[0];
        var r = img.getBoundingClientRect();
        var hr = cont.getBoundingClientRect();
        var visTop = Math.max(r.top, hr.top), visBottom = Math.min(r.bottom, hr.bottom);
        var visLeft = Math.max(r.left, hr.left), visRight = Math.min(r.right, hr.right);
        if (visBottom - visTop < 20 || visRight - visLeft < 20)
          return { empty: true, img: [r.top, r.bottom], host: [hr.top, hr.bottom] };
        var x = Math.max(visLeft + 12, visRight - 90);
        var y = visTop + Math.min(80, (visBottom - visTop) / 2);
        var top = document.elementFromPoint(x, y);
        var info = { topmost: top ? (top.tagName + '|' + (top.className || '').slice(0, 40)) : null, x: x, y: y };
        var ev = { bubbles: true, cancelable: true, clientX: x, clientY: y };
        (top || img).dispatchEvent(new MouseEvent('mousedown', ev));
        (top || img).dispatchEvent(new MouseEvent('mouseup', ev));
        (top || img).dispatchEvent(new MouseEvent('click', ev));
        return info;
      })();
      rec('image-visible-click', !!clickRes && !clickRes.empty, clickRes);
      await sleep(400);

      var overlay = document.querySelector('.image-remove-btn');
      var ostate = null;
      if (overlay) {
        var orct = overlay.getBoundingClientRect();
        var hrct = cont.getBoundingClientRect();
        ostate = {
          display: overlay.style.display,
          left: Math.round(orct.left), top: Math.round(orct.top),
          right: Math.round(orct.right), bottom: Math.round(orct.bottom),
          host: [Math.round(hrct.left), Math.round(hrct.top), Math.round(hrct.right), Math.round(hrct.bottom)]
        };
        var inside = overlay.style.display !== 'none' &&
          orct.top >= hrct.top - 1 && orct.bottom <= hrct.bottom + 1 &&
          orct.left >= hrct.left - 1 && orct.right <= hrct.right + 1;
        rec('overlay-inside-editor-box', inside, ostate);
      } else {
        rec('overlay-inside-editor-box', false, 'overlay missing');
      }

      cont.scrollTop = cont.scrollHeight;
      await sleep(600);
      var imgStillVisible = await (async function () {
        var imgs = Array.from(document.querySelectorAll('.ProseMirror img'));
        if (!imgs.length) return false;
        imgs.sort(function (a, b) {
          var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
          return (rb.width * rb.height) - (ra.width * ra.height);
        });
        var r = imgs[0].getBoundingClientRect();
        var hr = cont.getBoundingClientRect();
        return (Math.min(r.bottom, hr.bottom) - Math.max(r.top, hr.top)) >= 12 &&
               (Math.min(r.right, hr.right) - Math.max(r.left, hr.left)) >= 12;
      })();
      var vis = !overlay ? 'missing' :
        (overlay.style.display === 'none' || getComputedStyle(overlay).display === 'none') ? 'hidden' : 'visible';
      if (imgStillVisible) {
        var orct2 = overlay && overlay.getBoundingClientRect();
        var hrct2 = cont.getBoundingClientRect();
        var inBox = orct2 && orct2.top >= hrct2.top - 1 && orct2.bottom <= hrct2.bottom + 1 &&
          orct2.left >= hrct2.left - 1 && orct2.right <= hrct2.right + 1;
        rec('overlay-hides-when-image-scrolled-out', vis === 'visible' && inBox,
            { note: 'image still partially visible at max scroll', vis: vis, inBox: !!inBox });
      } else {
        rec('overlay-hides-when-image-scrolled-out', vis === 'hidden', { note: 'image fully out', vis: vis });
      }

      // scroll back, click image, delete via overlay
      cont.scrollTop = 0;
      await sleep(400);
      var imgs2 = Array.from(document.querySelectorAll('.ProseMirror img'));
      if (imgs2.length) {
        var target = imgs2.sort(function (a, b) {
          var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
          return (rb.width * rb.height) - (ra.width * ra.height);
        })[0];
        var r2 = target.getBoundingClientRect();
        var x2 = r2.left + Math.min(30, r2.width / 2), y2 = r2.top + Math.min(30, r2.height / 2);
        var top2 = document.elementFromPoint(x2, y2);
        var ev2 = { bubbles: true, cancelable: true, clientX: x2, clientY: y2 };
        (top2 || target).dispatchEvent(new MouseEvent('mousedown', ev2));
        (top2 || target).dispatchEvent(new MouseEvent('mouseup', ev2));
        (top2 || target).dispatchEvent(new MouseEvent('click', ev2));
        await sleep(300);
        var shown = overlay && overlay.style.display !== 'none';
        rec('overlay-shown-for-delete', !!shown, shown ? null : 'not shown');
        if (shown) {
          var beforeDelete = document.querySelectorAll('.ProseMirror img').length;
          var or2 = overlay.getBoundingClientRect();
          overlay.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, clientX: or2.left + 10, clientY: or2.top + 10 }));
          overlay.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, clientX: or2.left + 10, clientY: or2.top + 10 }));
          var gone = await waitFor(function () {
            return document.querySelectorAll('.ProseMirror img').length < beforeDelete;
          }, 8000);
          rec('image-removed-via-overlay', !!gone, 'before=' + beforeDelete + ' imgs=' + document.querySelectorAll('.ProseMirror img').length);
        } else {
          rec('image-removed-via-overlay', false, 'no overlay');
        }
      } else {
        rec('overlay-shown-for-delete', false, 'no images');
        rec('image-removed-via-overlay', false, 'no images');
      }

      finish();
    } catch (e) {
      rec('run-exception', false, String(e && e.stack || e).slice(0, 400));
      finish();
    }
  }
})();
