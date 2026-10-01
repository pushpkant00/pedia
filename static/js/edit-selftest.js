"use strict";
/* Dev-only self-test for the article editor (?selftest=1).
   Drives the image popup, overlay toolbar, zoom, delete and width sync,
   then writes RESULTS:{...} into #selftest-results. */
(function () {
    const results = [];
    const errors = [];
    function rec(t, ok, d) {
        results.push({ t: t, ok: !!ok, d: d === undefined ? null : d });
        const el = document.getElementById('selftest-results');
        if (el)
            el.textContent = 'LIVESTEP:' + t + ':' + (ok ? 'ok' : 'no');
    }
    function finish() {
        let el = document.getElementById('selftest-results');
        if (!el) {
            el = document.createElement('div');
            el.id = 'selftest-results';
            document.body.appendChild(el);
        }
        const pass = results.every(function (r) { return r.ok; });
        el.textContent = 'RESULTS:' + JSON.stringify({
            status: pass ? 'PASS' : 'FAIL', results: results, errors: errors,
        });
    }
    function recErr(m) {
        errors.push(String(m).slice(0, 300));
    }
    function sleep(ms) {
        return new Promise(function (resolve) { setTimeout(resolve, ms); });
    }
    function waitFor(fn, timeout) {
        const limit = timeout || 12000;
        const start = Date.now();
        return new Promise(function (resolve) {
            (function poll() {
                let v = null;
                try {
                    v = fn();
                }
                catch {
                    v = null;
                }
                if (v)
                    return resolve(v);
                if (Date.now() - start > limit)
                    return resolve(null);
                setTimeout(poll, 120);
            })();
        });
    }
    let tries = 0;
    (function poll() {
        try {
            if (window.__pediaEditor && document.readyState === 'complete')
                return run();
            if (++tries > 250) {
                rec('editor-init', false, 'timeout');
                return finish();
            }
        }
        catch (e) {
            recErr('poll:' + e);
        }
        setTimeout(poll, 100);
    })();
    async function run() {
        try {
            rec('editor-init', true);
            window.addEventListener('error', function (e) {
                recErr('win:' + (e.message || String(e)) + ' | ' +
                    ((e.error && e.error.stack) || '').slice(0, 200));
            });
            const alertLog = [];
            window.alert = function (m) { alertLog.push(String(m).slice(0, 200)); };
            const fetchLog = [];
            const origFetch = window.fetch.bind(window);
            window.fetch = function (input, init) {
                const url = String(input);
                const p = origFetch(input, init);
                p.then(function (r) { fetchLog.push(url + ' -> ' + r.status); }, function (e) { fetchLog.push(url + ' -> ERR ' + e); });
                return p;
            };
            const btn = (document.querySelector('[aria-label="Insert image"]') ||
                Array.from(document.querySelectorAll('.toastui-editor-toolbar button'))
                    .filter(function (b) {
                    return /image/i.test(b.className + ' ' + (b.getAttribute('aria-label') || ''));
                })[0]);
            if (!btn) {
                rec('image-button-found', false, 'missing');
                return finish();
            }
            const br = btn.getBoundingClientRect();
            btn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, clientX: br.left + 5, clientY: br.top + 5 }));
            btn.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, clientX: br.left + br.width / 2, clientY: br.top + br.height / 2 }));
            btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, clientX: br.left + br.width / 2, clientY: br.top + br.height / 2 }));
            const input = await waitFor(() => document.getElementById('toastuiImageFileInput'), 6000);
            rec('file-input-in-popup', !!input, input ? { multiple: input.multiple } : 'not found');
            if (input) {
                await waitFor(() => (input.multiple ? true : null), 3000);
                rec('file-input-allows-multiple', input.multiple === true, 'multiple=' + input.multiple);
            }
            if (!input)
                return finish();
            const before = document.querySelectorAll('.ProseMirror img').length;
            rec('baseline-img-count', before >= 1, 'count=' + before);
            function makeDt(names) {
                const bytes = Uint8Array.from(atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='), function (c) { return c.charCodeAt(0); });
                const dt = new DataTransfer();
                names.forEach(function (n) {
                    dt.items.add(new File([bytes], n, { type: 'image/png' }));
                });
                return dt;
            }
            function clickOk() {
                const ok = (document.querySelector('.toastui-editor-popup [class*="ok-button"]') ||
                    Array.from(document.querySelectorAll('.toastui-editor-popup button'))
                        .filter(function (b) { return /ok-button/.test(b.className); })[0]);
                if (!ok)
                    return false;
                const r = ok.getBoundingClientRect();
                const ev = { bubbles: true, cancelable: true, clientX: r.left + 5, clientY: r.top + 5 };
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
            }
            catch (e) {
                rec('ok-clicked', false, String(e));
            }
            await waitFor(() => document.querySelectorAll('.ProseMirror img').length > before, 8000);
            await sleep(1500);
            const after = document.querySelectorAll('.ProseMirror img').length;
            rec('two-files-inserted', after === (before + 2), 'before=' + before + ' after=' + after);
            rec('fetch-log', true, fetchLog.slice(0, 6));
            rec('alerts', alertLog.length === 0, alertLog.slice(0, 4));
            // Single-file regression: reopen the popup, pick one file, OK.
            try {
                btn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, clientX: br.left + 5, clientY: br.top + 5 }));
                btn.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, clientX: br.left + br.width / 2, clientY: br.top + br.height / 2 }));
                btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, clientX: br.left + br.width / 2, clientY: br.top + br.height / 2 }));
                let input2 = await waitFor(() => document.getElementById('toastuiImageFileInput'), 6000);
                if (!input2)
                    throw new Error('popup did not reopen');
                await sleep(700);
                let fileCount = 0;
                for (let attempt = 0; attempt < 4; attempt++) {
                    input2 = document.getElementById('toastuiImageFileInput') || input2;
                    input2.files = makeDt(['single-c.png']).files;
                    fileCount = input2.files ? input2.files.length : 0;
                    if (fileCount === 1)
                        break;
                    await sleep(400);
                }
                if (fileCount === 1) {
                    input2.dispatchEvent(new Event('input', { bubbles: true }));
                    input2.dispatchEvent(new Event('change', { bubbles: true }));
                }
                rec('single-files-ready', fileCount === 1, 'files=' + fileCount);
                rec('single-ok-clicked', fileCount === 1 && clickOk());
            }
            catch (e) {
                rec('single-ok-clicked', false, String(e));
            }
            const singleTarget = (after || before) + 1;
            await waitFor(() => document.querySelectorAll('.ProseMirror img').length >= singleTarget, 8000);
            await sleep(800);
            const afterSingle = document.querySelectorAll('.ProseMirror img').length;
            rec('single-file-inserted', afterSingle === singleTarget, 'after=' + afterSingle + ' expected=' + singleTarget);
            const popup = document.querySelector('.toastui-editor-popup');
            const popupState = !popup ? 'missing' :
                (popup.style.display === 'none' || getComputedStyle(popup).display === 'none') ? 'closed' : 'open';
            rec('popup-closed-after-insert', popupState === 'closed', popupState);
            const findCont = function () {
                const holder = document.getElementById('editor');
                if (!holder)
                    return null;
                const nodes = [holder].concat(Array.from(holder.querySelectorAll('*')));
                for (const node of nodes) {
                    const el = node;
                    if (el.scrollHeight > el.clientHeight + 40 && el.clientHeight > 150)
                        return el;
                }
                return null;
            };
            const cont = findCont();
            rec('scroll-container-found', !!cont, cont ? ('class=' + cont.className) : 'none');
            if (!cont)
                return finish();
            cont.scrollTop = 420;
            await sleep(500);
            let clickedImg = null;
            const clickRes = await (async function () {
                const imgs = Array.from(document.querySelectorAll('.ProseMirror img'));
                if (!imgs.length)
                    return { err: 'no imgs' };
                imgs.sort(function (a, b) {
                    const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
                    return (rb.width * rb.height) - (ra.width * ra.height);
                });
                const img = imgs[0];
                clickedImg = img;
                const r = img.getBoundingClientRect();
                const hr = cont.getBoundingClientRect();
                const visTop = Math.max(r.top, hr.top), visBottom = Math.min(r.bottom, hr.bottom);
                const visLeft = Math.max(r.left, hr.left), visRight = Math.min(r.right, hr.right);
                if (visBottom - visTop < 20 || visRight - visLeft < 20) {
                    return { empty: true, x: 0, y: 0 };
                }
                const x = Math.max(visLeft + 12, visRight - 90);
                const y = visTop + Math.min(80, (visBottom - visTop) / 2);
                const top = document.elementFromPoint(x, y);
                const info = {
                    topmost: top ? (top.tagName + '|' + String(top.className || '').slice(0, 40)) : null,
                    x: x, y: y,
                };
                const ev = { bubbles: true, cancelable: true, clientX: x, clientY: y };
                (top || img).dispatchEvent(new MouseEvent('mousedown', ev));
                (top || img).dispatchEvent(new MouseEvent('mouseup', ev));
                (top || img).dispatchEvent(new MouseEvent('click', ev));
                return info;
            })();
            rec('image-visible-click', !!clickRes && !clickRes.empty, clickRes);
            await sleep(400);
            const overlay = document.querySelector('.image-tools');
            let ostate = null;
            if (overlay && cont) {
                const orct = overlay.getBoundingClientRect();
                const hrct = cont.getBoundingClientRect();
                ostate = {
                    display: overlay.style.display,
                    left: Math.round(orct.left), top: Math.round(orct.top),
                    right: Math.round(orct.right), bottom: Math.round(orct.bottom),
                    host: [Math.round(hrct.left), Math.round(hrct.top), Math.round(hrct.right), Math.round(hrct.bottom)],
                };
                const inside = overlay.style.display !== 'none' &&
                    orct.top >= hrct.top - 1 && orct.bottom <= hrct.bottom + 1 &&
                    orct.left >= hrct.left - 1 && orct.right <= hrct.right + 1;
                rec('overlay-inside-editor-box', inside, ostate);
            }
            else {
                rec('overlay-inside-editor-box', false, 'overlay missing');
            }
            // --- image toolbar: blank-area click, zoom, download ---
            const zinBtn = overlay && overlay.querySelector('[aria-label="Zoom in"]');
            const zoutBtn = overlay && overlay.querySelector('[aria-label="Zoom out"]');
            const dlBtn = overlay && overlay.querySelector('[aria-label="Download image"]');
            const rmBtn = overlay && overlay.querySelector('.image-remove-btn');
            rec('image-toolbar-options', !!(zinBtn && zoutBtn && dlBtn && rmBtn), {
                zoomIn: !!zinBtn, zoomOut: !!zoutBtn, download: !!dlBtn, remove: !!rmBtn,
            });
            const selBefore = (function () {
                const s = window.getSelection();
                return s && s.rangeCount ? { node: s.anchorNode, off: s.anchorOffset } : null;
            })();
            let blankInfo = null;
            if (clickedImg && cont) {
                const rb2 = clickedImg.getBoundingClientRect();
                const hrb = cont.getBoundingClientRect();
                const bx = rb2.right + 14;
                const by = Math.max(rb2.top, hrb.top) + Math.min(30, rb2.height / 2);
                const bel = document.elementFromPoint(bx, by);
                const bev = { bubbles: true, cancelable: true, clientX: bx, clientY: by };
                blankInfo = {
                    x: Math.round(bx), y: Math.round(by),
                    top: bel ? (bel.tagName + '|' + String(bel.className || '').slice(0, 30)) : null,
                    probe: window.__pediaAdjProbe ? window.__pediaAdjProbe(bx, by) : 'no-probe',
                };
                (bel || clickedImg).dispatchEvent(new MouseEvent('mousedown', bev));
                (bel || clickedImg).dispatchEvent(new MouseEvent('mouseup', bev));
                (bel || clickedImg).dispatchEvent(new MouseEvent('click', bev));
            }
            await sleep(400);
            const selAfter = (function () {
                const s = window.getSelection();
                return s && s.rangeCount ? { node: s.anchorNode, off: s.anchorOffset } : null;
            })();
            const caretMoved = selAfter
                ? (!selBefore || selAfter.node !== selBefore.node || selAfter.off !== selBefore.off)
                : false;
            const toolsShown = !!overlay && overlay.style.display !== 'none' &&
                getComputedStyle(overlay).display !== 'none';
            rec('blank-click-shows-toolbar-no-caret', !!clickedImg && toolsShown && !caretMoved, { blank: blankInfo, shown: toolsShown, caretMoved: caretMoved });
            // Zoom: out first (makes room), then in must widen again.
            if (zinBtn && zoutBtn && clickedImg) {
                const img = clickedImg;
                const w0 = img.getBoundingClientRect().width;
                const rzo = zoutBtn.getBoundingClientRect();
                const ezo = { bubbles: true, cancelable: true, clientX: rzo.left + 4, clientY: rzo.top + 4 };
                zoutBtn.dispatchEvent(new MouseEvent('mousedown', ezo));
                zoutBtn.dispatchEvent(new MouseEvent('mouseup', ezo));
                zoutBtn.dispatchEvent(new MouseEvent('click', ezo));
                await sleep(350);
                const wo = img.getBoundingClientRect().width;
                rec('zoom-out-narrows-image', wo < w0 - 2, {
                    from: Math.round(w0), to: Math.round(wo), lastZoom: window.__pediaLastZoom || null,
                });
                const rzi = zinBtn.getBoundingClientRect();
                const ezi = { bubbles: true, cancelable: true, clientX: rzi.left + 4, clientY: rzi.top + 4 };
                zinBtn.dispatchEvent(new MouseEvent('mousedown', ezi));
                zinBtn.dispatchEvent(new MouseEvent('mouseup', ezi));
                zinBtn.dispatchEvent(new MouseEvent('click', ezi));
                await sleep(350);
                const wi = img.getBoundingClientRect().width;
                rec('zoom-in-widens-image', wi > wo + 2, {
                    from: Math.round(wo), to: Math.round(wi),
                    style: img.style.width, attr: img.getAttribute('width'),
                    holderW: Math.round(document.getElementById('editor').getBoundingClientRect().width),
                    pW: Math.round(img.parentElement.getBoundingClientRect().width),
                    lastZoom: window.__pediaLastZoom || null,
                });
            }
            else {
                rec('zoom-out-narrows-image', false, 'missing button or image');
                rec('zoom-in-widens-image', false, 'missing button or image');
            }
            let dlOk = false;
            let dlDetail = 'missing';
            if (dlBtn && clickedImg) {
                dlOk = !!dlBtn.getAttribute('download') &&
                    (dlBtn.href === clickedImg.src || dlBtn.href === (clickedImg.currentSrc || ''));
                dlDetail = {
                    download: dlBtn.getAttribute('download'),
                    href: (dlBtn.getAttribute('href') || '').slice(0, 90),
                };
            }
            rec('download-link-prepared', dlOk, dlDetail);
            // Zoomed width must survive getHTML() (saved as width="N", allowed by the sanitizer).
            let serOk = false;
            let serDetail = 'skipped';
            if (clickedImg && typeof syncImageWidths === 'function') {
                const restoreW = clickedImg.getAttribute('width');
                const restoreStyleW = clickedImg.style.width;
                applyImageWidth(clickedImg, 137);
                try {
                    const ser = syncImageWidths(window.__pediaEditor.getHTML());
                    serOk = /width="137"/.test(ser);
                    serDetail = serOk ? null : ser.replace(/\s+/g, ' ').slice(0, 160);
                }
                catch (e) {
                    serDetail = String(e);
                }
                if (restoreW) {
                    clickedImg.setAttribute('width', restoreW);
                    clickedImg.style.width = restoreStyleW || (restoreW + 'px');
                    clickedImg.style.height = 'auto';
                }
                else {
                    clickedImg.removeAttribute('width');
                    clickedImg.style.width = '';
                    clickedImg.style.height = '';
                }
            }
            rec('zoom-width-serialized-on-save', serOk, serDetail);
            if (cont)
                cont.scrollTop = cont.scrollHeight;
            await sleep(600);
            const imgStillVisible = await (async function () {
                const imgs = Array.from(document.querySelectorAll('.ProseMirror img'));
                if (!imgs.length || !cont)
                    return false;
                imgs.sort(function (a, b) {
                    const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
                    return (rb.width * rb.height) - (ra.width * ra.height);
                });
                const r = imgs[0].getBoundingClientRect();
                const hr = cont.getBoundingClientRect();
                return (Math.min(r.bottom, hr.bottom) - Math.max(r.top, hr.top)) >= 12 &&
                    (Math.min(r.right, hr.right) - Math.max(r.left, hr.left)) >= 12;
            })();
            const vis = !overlay ? 'missing' :
                (overlay.style.display === 'none' || getComputedStyle(overlay).display === 'none') ? 'hidden' : 'visible';
            if (imgStillVisible && overlay && cont) {
                const orct2 = overlay.getBoundingClientRect();
                const hrct2 = cont.getBoundingClientRect();
                const inBox = orct2.top >= hrct2.top - 1 && orct2.bottom <= hrct2.bottom + 1 &&
                    orct2.left >= hrct2.left - 1 && orct2.right <= hrct2.right + 1;
                rec('overlay-hides-when-image-scrolled-out', vis === 'visible' && inBox, { note: 'image still partially visible at max scroll', vis: vis, inBox: inBox });
            }
            else {
                rec('overlay-hides-when-image-scrolled-out', vis === 'hidden', { note: 'image fully out', vis: vis });
            }
            // Scroll back, click the image, delete it via the overlay.
            if (cont)
                cont.scrollTop = 0;
            await sleep(400);
            const imgs2 = Array.from(document.querySelectorAll('.ProseMirror img'));
            if (imgs2.length) {
                const target = imgs2.sort(function (a, b) {
                    const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
                    return (rb.width * rb.height) - (ra.width * ra.height);
                })[0];
                const r2 = target.getBoundingClientRect();
                const x2 = r2.left + Math.min(30, r2.width / 2);
                const y2 = r2.top + Math.min(30, r2.height / 2);
                const top2 = document.elementFromPoint(x2, y2);
                const ev2 = { bubbles: true, cancelable: true, clientX: x2, clientY: y2 };
                (top2 || target).dispatchEvent(new MouseEvent('mousedown', ev2));
                (top2 || target).dispatchEvent(new MouseEvent('mouseup', ev2));
                (top2 || target).dispatchEvent(new MouseEvent('click', ev2));
                await sleep(300);
                const shown = !!overlay && overlay.style.display !== 'none';
                rec('overlay-shown-for-delete', !!shown, shown ? null : 'not shown');
                if (shown && overlay) {
                    const beforeDelete = document.querySelectorAll('.ProseMirror img').length;
                    const delBtn = overlay.querySelector('.image-remove-btn');
                    if (delBtn) {
                        const or2 = delBtn.getBoundingClientRect();
                        delBtn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, clientX: or2.left + 10, clientY: or2.top + 10 }));
                        delBtn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, clientX: or2.left + 10, clientY: or2.top + 10 }));
                    }
                    const gone = await waitFor(() => document.querySelectorAll('.ProseMirror img').length < beforeDelete, 8000);
                    rec('image-removed-via-overlay', !!gone, 'before=' + beforeDelete + ' imgs=' + document.querySelectorAll('.ProseMirror img').length);
                }
                else {
                    rec('image-removed-via-overlay', false, 'no overlay');
                }
            }
            else {
                rec('overlay-shown-for-delete', false, 'no images');
                rec('image-removed-via-overlay', false, 'no images');
            }
            finish();
        }
        catch (e) {
            const err = e;
            rec('run-exception', false, String((err && err.stack) || e).slice(0, 400));
            finish();
        }
    }
})();
