"use strict";
/* Pedia article editor: ToastUI wrapper with image tools, width sync,
   autosave drafts and prefs read from the form's data-* attributes. */
function getCookie(name) {
    const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : '';
}
function uploadImageFile(holder, file) {
    const data = new FormData();
    data.append('file', file);
    const url = holder.getAttribute('data-upload-url') || '';
    return fetch(url, {
        method: 'POST',
        body: data,
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
    }).then(function (response) {
        return response.json().then(function (payload) {
            if (!response.ok)
                throw new Error(payload.error || 'Upload failed');
            return payload;
        });
    });
}
let imageWidths = {};
function extractImageWidths(html) {
    const map = {};
    if (!html)
        return map;
    try {
        const doc = new DOMParser().parseFromString(html, 'text/html');
        const imgs = doc.body.querySelectorAll('img');
        for (let i = 0; i < imgs.length; i++) {
            const src = imgs[i].getAttribute('src');
            const w = imgs[i].getAttribute('width');
            if (src && w)
                map[src] = w;
        }
    }
    catch { /* unparsable HTML — no widths to extract */ }
    return map;
}
function applyImageWidth(imgEl, w) {
    const n = parseInt(String(w), 10);
    if (!imgEl || !n || n < 16)
        return;
    imgEl.style.width = n + 'px';
    imgEl.style.height = 'auto';
    imgEl.setAttribute('width', String(n));
}
function restoreImageWidths(map) {
    if (!map)
        return;
    const imgs = document.querySelectorAll('#editor img');
    for (let i = 0; i < imgs.length; i++) {
        const src = imgs[i].getAttribute('src') || '';
        const w = map[src];
        if (w)
            applyImageWidth(imgs[i], w);
    }
}
function syncImageWidths(html) {
    try {
        const live = document.querySelectorAll('#editor img');
        const liveW = {};
        for (let i = 0; i < live.length; i++) {
            const s = live[i].getAttribute('src');
            const lw = live[i].getAttribute('width');
            if (s && lw && !(s in liveW))
                liveW[s] = lw;
        }
        const doc = new DOMParser().parseFromString(html || '', 'text/html');
        const out = doc.body.querySelectorAll('img');
        let changed = false;
        for (let j = 0; j < out.length; j++) {
            const osrc = out[j].getAttribute('src') || '';
            const w = liveW[osrc] || imageWidths[osrc];
            if (w) {
                out[j].setAttribute('width', String(w).replace(/px$/, ''));
                changed = true;
            }
        }
        return changed ? doc.body.innerHTML : html || '';
    }
    catch {
        return html;
    }
}
function readPrefs(holder) {
    return {
        mode: holder.getAttribute('data-mode') || 'wysiwyg',
        toolbar: holder.getAttribute('data-toolbar') || 'full',
        theme: holder.getAttribute('data-theme') || 'light',
        uploads: holder.getAttribute('data-uploads') !== 'off',
        autosave: holder.getAttribute('data-autosave') !== 'off',
        interval: parseInt(holder.getAttribute('data-autosave-interval') || '', 10) || 30,
        draftKey: 'pedia-draft:' + (holder.getAttribute('data-draft-key') || location.pathname),
    };
}
function readDraft(prefs, serverContent) {
    if (!prefs.autosave)
        return null;
    try {
        const raw = localStorage.getItem(prefs.draftKey);
        if (!raw)
            return null;
        const draft = JSON.parse(raw);
        if (!draft || !draft.html) {
            localStorage.removeItem(prefs.draftKey);
            return null;
        }
        // Restore only while the article still matches what the draft was started from.
        if ((draft.seed || '') !== (serverContent || '')) {
            localStorage.removeItem(prefs.draftKey);
            return null;
        }
        if (draft.html === serverContent)
            return null;
        return draft;
    }
    catch {
        return null;
    }
}
function showDraftNotice(holder, draft, prefs) {
    const notice = document.createElement('div');
    notice.className = 'editor-draft-notice';
    const text = document.createElement('span');
    const when = new Date(draft.at);
    text.textContent = 'Unsaved draft restored (saved ' +
        (isNaN(when.getTime()) ? 'earlier' : when.toLocaleString()) + ').';
    const discard = document.createElement('button');
    discard.type = 'button';
    discard.className = 'link-button';
    discard.textContent = 'discard draft';
    discard.addEventListener('click', function () {
        try {
            localStorage.removeItem(prefs.draftKey);
        }
        catch { /* ignore */ }
        window.location.reload();
    });
    notice.appendChild(text);
    notice.appendChild(document.createTextNode(' '));
    notice.appendChild(discard);
    if (holder.parentNode)
        holder.parentNode.insertBefore(notice, holder);
}
(function () {
    const form = document.getElementById('edit-form');
    const contentField = document.getElementById('id_content');
    const holder = document.getElementById('editor');
    if (!form || !contentField || !holder)
        return;
    function enablePlainEditor(message, error) {
        console.error('[pedia editor] ' + message, error || '');
        const textarea = document.createElement('textarea');
        textarea.name = contentField.name;
        textarea.id = contentField.id;
        textarea.value = contentField.value;
        textarea.rows = 24;
        textarea.className = 'raw-textarea';
        textarea.setAttribute('aria-label', 'Article body (HTML)');
        if (contentField.parentNode) {
            contentField.parentNode.replaceChild(textarea, contentField);
        }
        const banner = document.createElement('div');
        banner.className = 'editor-hint';
        banner.textContent = message +
            (error && error.message ? ' (' + error.message + ')' : '') +
            ' You can edit the HTML below directly — images can be added with an <img> tag.';
        holder.replaceWith(banner);
    }
    if (typeof toastui === 'undefined') {
        enablePlainEditor('The editor library failed to load.');
        return;
    }
    if (!toastui.Editor) {
        enablePlainEditor('The editor library loaded but did not provide toastui.Editor.');
        return;
    }
    const prefs = readPrefs(holder);
    const serverContent = contentField.value || '';
    const draft = readDraft(prefs, serverContent);
    const initialValue = draft ? draft.html : serverContent;
    const FULL_ITEMS = [
        ['heading', 'bold', 'italic', 'strike'],
        ['hr', 'quote'],
        ['ul', 'ol', 'task', 'indent', 'outdent'],
        ['table', 'image', 'link'],
        ['code', 'codeblock'],
        ['scrollSync'],
    ];
    const COMPACT_ITEMS = [
        ['heading', 'bold', 'italic', 'link', 'image'],
        ['ol', 'ul', 'code'],
    ];
    function withoutImage(groups) {
        return groups
            .map(function (group) {
            return group.filter(function (name) { return name !== 'image'; });
        })
            .filter(function (group) { return group.length > 0; });
    }
    const editorOptions = {
        el: holder,
        height: '540px',
        initialEditType: prefs.mode === 'markdown' ? 'markdown' : 'wysiwyg',
        previewStyle: 'vertical',
        initialValue: initialValue,
        usageStatistics: false,
        theme: prefs.theme === 'dark' ? 'dark' : 'light',
    };
    const needCustomToolbar = prefs.toolbar === 'compact' || !prefs.uploads;
    if (needCustomToolbar) {
        let items = prefs.toolbar === 'compact' ? COMPACT_ITEMS : FULL_ITEMS;
        if (!prefs.uploads) {
            items = withoutImage(items);
        }
        editorOptions.toolbarItems = items;
    }
    if (prefs.uploads) {
        editorOptions.hooks = {
            addImageBlobHook: function (blob, callback) {
                uploadImageFile(holder, blob)
                    .then(function (payload) {
                    const file = blob;
                    callback(payload.url || '', file.name || payload.alt || 'image');
                })
                    .catch(function (error) {
                    window.alert('Image upload failed: ' + error.message);
                });
                return false;
            },
        };
    }
    let editor;
    const savedWidths = extractImageWidths(serverContent);
    try {
        editor = new toastui.Editor(editorOptions);
    }
    catch (error) {
        enablePlainEditor('The visual editor failed to start.', error);
        return;
    }
    if (draft) {
        showDraftNotice(holder, draft, prefs);
    }
    function saveDraftNow() {
        if (!prefs.autosave)
            return;
        try {
            const html = editor.getHTML();
            if (!html || html === '<p></p>' || html === serverContent)
                return;
            localStorage.setItem(prefs.draftKey, JSON.stringify({
                html: html,
                at: Date.now(),
                seed: serverContent,
            }));
        }
        catch { /* storage full or unavailable */ }
    }
    if (prefs.autosave) {
        setInterval(saveDraftNow, prefs.interval * 1000);
        window.addEventListener('pagehide', saveDraftNow);
    }
    form.addEventListener('submit', function () {
        contentField.value = syncImageWidths(editor.getHTML());
        if (prefs.autosave) {
            try {
                localStorage.removeItem(prefs.draftKey);
            }
            catch { /* ignore */ }
        }
    });
    window.__pediaEditor = editor;
    window.__pediaEditorPrefs = prefs;
    imageWidths = savedWidths;
    restoreImageWidths(savedWidths);
    setTimeout(function () { restoreImageWidths(savedWidths); }, 150);
    installImageRemoval(editor, holder);
})();
function installImageRemoval(editor, holder) {
    function getPMView() {
        var _a, _b;
        const candidates = [];
        try {
            candidates.push(editor.view);
        }
        catch { /* not ready */ }
        try {
            const modeEditor = editor.getCurrentModeEditor && editor.getCurrentModeEditor();
            if (modeEditor) {
                candidates.push(modeEditor.view, modeEditor.editorView);
            }
        }
        catch { /* mode editor unavailable */ }
        try {
            const ww = editor.wwEditor;
            if (ww)
                candidates.push(ww.view);
        }
        catch { /* wysiwyg editor unavailable */ }
        for (const candidate of candidates) {
            const view = candidate;
            if (view && 'state' in view && ((_a = view.state) === null || _a === void 0 ? void 0 : _a.doc) &&
                typeof view.dispatch === 'function') {
                return view;
            }
            if (view && 'view' in view && view.view && ((_b = view.view.state) === null || _b === void 0 ? void 0 : _b.doc) &&
                typeof view.view.dispatch === 'function') {
                return view.view;
            }
        }
        return null;
    }
    function findImageTarget(view, imgEl) {
        const found = [];
        view.state.doc.descendants(function (node, pos) {
            if (node.type && node.type.name === 'image') {
                found.push({ pos: pos, node: node, src: node.attrs && node.attrs.src });
            }
        });
        if (!found.length)
            return null;
        let domPos = null;
        try {
            domPos = view.posAtDOM(imgEl, 0);
        }
        catch { /* DOM mapping failed */ }
        if (typeof domPos === 'number') {
            const offsets = [domPos, domPos - 1, domPos + 1, domPos - 2];
            for (const offset of offsets) {
                for (const item of found) {
                    if (item.pos === offset)
                        return item;
                }
            }
        }
        const sameSrc = found.filter(function (f) { return f.src && f.src === imgEl.src; });
        if (sameSrc.length === 1)
            return sameSrc[0];
        if (sameSrc.length > 1 && typeof domPos === 'number') {
            sameSrc.sort(function (a, b) {
                return Math.abs(a.pos - domPos) - Math.abs(b.pos - domPos);
            });
            return sameSrc[0];
        }
        return found.length === 1 ? found[0] : null;
    }
    function deleteImageNode(imgEl) {
        const view = getPMView();
        if (!view)
            return false;
        const target = findImageTarget(view, imgEl);
        if (!target)
            return false;
        try {
            view.dispatch(view.state.tr.delete(target.pos, target.pos + target.node.nodeSize));
            return true;
        }
        catch (error) {
            console.error('[pedia editor] image delete failed', error);
            return false;
        }
    }
    const toolbar = document.createElement('div');
    toolbar.className = 'image-tools';
    toolbar.setAttribute('role', 'toolbar');
    toolbar.setAttribute('aria-label', 'Image options');
    function toolButton(label, text) {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'image-tool-btn';
        b.setAttribute('aria-label', label);
        b.title = label;
        b.textContent = text;
        toolbar.appendChild(b);
        return b;
    }
    const zoomOutBtn = toolButton('Zoom out', '−');
    const zoomInBtn = toolButton('Zoom in', '+');
    const downloadBtn = document.createElement('a');
    downloadBtn.className = 'image-tool-btn';
    downloadBtn.setAttribute('aria-label', 'Download image');
    downloadBtn.title = 'Download image';
    downloadBtn.textContent = '↓';
    downloadBtn.target = '_blank';
    downloadBtn.rel = 'noopener';
    toolbar.appendChild(downloadBtn);
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'image-remove-btn';
    removeBtn.setAttribute('aria-label', 'Remove this image');
    removeBtn.textContent = '✕';
    toolbar.appendChild(removeBtn);
    document.body.appendChild(toolbar);
    let activeImg = null;
    let ticker = 0;
    function hideOverlay() {
        toolbar.style.display = 'none';
        activeImg = null;
        if (ticker) {
            clearInterval(ticker);
            ticker = 0;
        }
    }
    function getClipHost() {
        const all = holder.getElementsByTagName('*');
        for (let i = 0; i < all.length; i++) {
            const el = all[i];
            if (el.scrollHeight > el.clientHeight + 40 && el.clientHeight > 150)
                return el;
        }
        return holder;
    }
    function positionOverlay(imgEl) {
        const rect = imgEl.getBoundingClientRect();
        const host = getClipHost().getBoundingClientRect();
        const visTop = Math.max(rect.top, host.top);
        const visBottom = Math.min(rect.bottom, host.bottom);
        const visLeft = Math.max(rect.left, host.left);
        const visRight = Math.min(rect.right, host.right);
        if (visBottom - visTop < 12 || visRight - visLeft < 12)
            return hideOverlay();
        toolbar.style.display = 'flex';
        const tw = toolbar.offsetWidth || 130;
        const th = toolbar.offsetHeight || 32;
        const left = Math.max(host.left + 4, Math.min(visRight - tw - 4, host.right - tw - 4));
        const top = Math.max(host.top + 4, Math.min(visTop + 6, host.bottom - th - 4));
        toolbar.style.left = left + 'px';
        toolbar.style.top = top + 'px';
    }
    function startTicker() {
        if (!ticker) {
            ticker = setInterval(function () {
                if (activeImg && document.body.contains(activeImg))
                    positionOverlay(activeImg);
                else
                    hideOverlay();
            }, 250);
        }
    }
    function showOverlay(imgEl) {
        if (!imgEl.getAttribute('src'))
            return hideOverlay();
        activeImg = imgEl;
        const src = imgEl.currentSrc || imgEl.src;
        let name = 'image';
        try {
            name = decodeURIComponent((src.split('?')[0].split('/').pop()) || 'image') || 'image';
        }
        catch { /* keep default */ }
        downloadBtn.href = src;
        downloadBtn.setAttribute('download', name);
        positionOverlay(imgEl);
        if (activeImg)
            startTicker();
    }
    function zoomImage(imgEl, dir) {
        if (!imgEl || !document.body.contains(imgEl))
            return null;
        const w = imgEl.getBoundingClientRect().width;
        if (!w)
            return null;
        let next = Math.round(w * (dir > 0 ? 1.25 : 0.8));
        const parentW = imgEl.parentElement && imgEl.parentElement.getBoundingClientRect().width;
        const max = Math.max(Math.round(parentW || holder.getBoundingClientRect().width) - 8, Math.round(w));
        next = Math.max(60, Math.min(next, max));
        const state = { w: w, next: next, max: max, skipped: false };
        if (next === Math.round(w)) {
            state.skipped = true;
            return state;
        }
        applyImageWidth(imgEl, next);
        const src = imgEl.getAttribute('src');
        if (src)
            imageWidths[src] = String(next);
        positionOverlay(imgEl);
        return state;
    }
    function imgFromTarget(t) {
        if (!t || !(t instanceof Element))
            return null;
        if (toolbar.contains(t))
            return null;
        if (t.tagName === 'IMG')
            return t;
        const inside = t.closest('img');
        if (inside && holder.contains(inside))
            return inside;
        return null;
    }
    function imgFromPoint(x, y) {
        const imgs = holder.querySelectorAll('img');
        for (let i = 0; i < imgs.length; i++) {
            const r = imgs[i].getBoundingClientRect();
            if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom)
                return imgs[i];
        }
        return null;
    }
    function imageAdjacentToCaret(x, y) {
        if (typeof x !== 'number' || typeof y !== 'number')
            return null;
        if (typeof document.caretRangeFromPoint !== 'function')
            return null;
        let range = null;
        try {
            range = document.caretRangeFromPoint(x, y);
        }
        catch {
            return null;
        }
        if (!range)
            return null;
        const node = range.startContainer;
        const off = range.startOffset;
        const isImg = (el) => !!el && el.nodeType === 1 && el.tagName === 'IMG';
        const isBlank = (el) => !!el && el.nodeType === 3 && !/\S/.test(el.textContent || '');
        let candidate = null;
        if (node.nodeType === 1) {
            const kids = node.childNodes;
            const a = kids[off];
            const b = kids[off - 1];
            if (isImg(a))
                candidate = a;
            else if (isImg(b))
                candidate = b;
            else if (isBlank(a) && isImg(kids[off + 1]))
                candidate = kids[off + 1];
            else if (isBlank(b) && isImg(kids[off - 2]))
                candidate = kids[off - 2];
        }
        else if (node.nodeType === 3) {
            const prev = node.previousSibling;
            const next = node.nextSibling;
            const text = node.textContent || '';
            if (off === 0 && isImg(prev))
                candidate = prev;
            else if (off >= text.length && isImg(next))
                candidate = next;
            else if (off === 0 && isBlank(prev) && prev && isImg(prev.previousSibling)) {
                candidate = prev.previousSibling;
            }
            else if (off >= text.length && isBlank(next) && next && isImg(next.nextSibling)) {
                candidate = next.nextSibling;
            }
        }
        return candidate;
    }
    function ensureFileInputMultiple() {
        const fi = document.getElementById('toastuiImageFileInput');
        if (fi && !fi.multiple)
            fi.multiple = true;
    }
    function insertImage(url, alt) {
        if (editor.eventEmitter && typeof editor.eventEmitter.emit === 'function') {
            editor.eventEmitter.emit('command', 'addImage', { imageUrl: url, altText: alt || 'image' });
        }
        else if (typeof editor.exec === 'function') {
            editor.exec('addImage', { imageUrl: url, altText: alt || 'image' });
        }
    }
    function insertFiles(files) {
        const altInput = document.getElementById('toastuiAltTextInput');
        const alt = (altInput && altInput.value) || '';
        let chain = Promise.resolve();
        Array.from(files).forEach(function (file) {
            chain = chain.then(function () {
                return uploadImageFile(holder, file).then(function (payload) {
                    insertImage(payload.url || '', alt || file.name || payload.alt || 'image');
                });
            });
        });
        return chain.catch(function (error) {
            window.alert('Image upload failed: ' + error.message);
        }).then(function () { });
    }
    document.addEventListener('mousedown', function (event) {
        const e = event;
        if (e.button !== 0 || !e.target)
            return;
        const target = e.target;
        if (target.closest && target.closest('.toastui-editor-popup'))
            return;
        if (toolbar.contains(target))
            return;
        let img = imgFromTarget(e.target);
        if (!img && typeof e.clientX === 'number') {
            img = imgFromPoint(e.clientX, e.clientY) ||
                imageAdjacentToCaret(e.clientX, e.clientY);
        }
        if (img && holder.contains(img)) {
            e.preventDefault();
            e.stopPropagation();
        }
    }, true);
    document.addEventListener('click', function (event) {
        ensureFileInputMultiple();
        setTimeout(ensureFileInputMultiple, 0);
        const target = event.target;
        const btn = target && target.closest ? target.closest('button') : null;
        if (btn && /ok-button/.test(btn.className || '') && btn.closest('.toastui-editor-popup')) {
            const fi = document.getElementById('toastuiImageFileInput');
            if (fi && fi.files && fi.files.length > 1) {
                event.preventDefault();
                event.stopImmediatePropagation();
                const picked = Array.from(fi.files);
                try {
                    fi.value = '';
                }
                catch { /* readonly in some browsers */ }
                insertFiles(picked);
                return;
            }
        }
        if (target && target.closest && target.closest('.toastui-editor-popup')) {
            hideOverlay();
            return;
        }
        if (target && toolbar.contains(target))
            return;
        let img = imgFromTarget(event.target);
        if (!img && event.clientX !== undefined) {
            img = imgFromPoint(event.clientX, event.clientY) ||
                imageAdjacentToCaret(event.clientX, event.clientY);
        }
        if (img && holder.contains(img)) {
            event.preventDefault();
            showOverlay(img);
        }
        else {
            hideOverlay();
        }
    }, true);
    document.addEventListener('drop', function (event) {
        const dt = event.dataTransfer;
        const files = dt && dt.files;
        if (!files || files.length < 2)
            return;
        const images = Array.from(files).filter(function (f) {
            return f.type && f.type.indexOf('image/') === 0;
        });
        if (images.length < 2)
            return;
        event.preventDefault();
        event.stopImmediatePropagation();
        insertFiles(images);
    }, true);
    document.addEventListener('paste', function (event) {
        const items = event.clipboardData &&
            event.clipboardData.items;
        if (!items)
            return;
        const images = [];
        for (let i = 0; i < items.length; i++) {
            if (items[i].kind === 'file' && items[i].type.indexOf('image/') === 0) {
                const f = items[i].getAsFile();
                if (f)
                    images.push(f);
            }
        }
        if (images.length < 2)
            return;
        event.preventDefault();
        event.stopImmediatePropagation();
        insertFiles(images);
    }, true);
    zoomOutBtn.addEventListener('click', function () {
        const r = zoomImage(activeImg, -1);
        if (r)
            window.__pediaLastZoom = { dir: -1, r: r };
    });
    zoomInBtn.addEventListener('click', function () {
        const r = zoomImage(activeImg, 1);
        if (r)
            window.__pediaLastZoom = { dir: 1, r: r };
    });
    removeBtn.addEventListener('click', function () {
        if (!activeImg)
            return hideOverlay();
        const img = activeImg;
        hideOverlay();
        if (!document.body.contains(img))
            return;
        if (!deleteImageNode(img)) {
            window.alert('Could not remove the image automatically — select it and press Delete.');
        }
    });
    window.addEventListener('scroll', function () {
        if (!activeImg)
            return;
        if (document.body.contains(activeImg))
            positionOverlay(activeImg);
        else
            hideOverlay();
    }, true);
    window.addEventListener('resize', function () {
        if (activeImg && document.body.contains(activeImg))
            positionOverlay(activeImg);
    });
    ensureFileInputMultiple();
    window.__pediaAdjProbe = function (x, y) {
        const out = { range: null, resolved: null };
        let range = null;
        try {
            range = typeof document.caretRangeFromPoint === 'function'
                ? document.caretRangeFromPoint(x, y)
                : null;
        }
        catch (error) {
            out.err = String(error);
        }
        if (range) {
            const c = range.startContainer;
            const o = range.startOffset;
            const info = { container: c.nodeName || c.nodeType, off: o };
            if (c.nodeType === 1) {
                info.kids = Array.from(c.childNodes).map(function (n) { return n.nodeName; }).join(',');
            }
            else if (c.nodeType === 3) {
                info.text = (c.textContent || '').slice(0, 60);
                info.prev = c.previousSibling && c.previousSibling.nodeName;
                info.next = c.nextSibling && c.nextSibling.nodeName;
                info.len = (c.textContent || '').length;
            }
            out.range = info;
        }
        const adj = imageAdjacentToCaret(x, y);
        out.resolved = adj ? adj.tagName : null;
        out.resolvedSrc = adj ? String(adj.getAttribute('src') || '').slice(-40) : null;
        const im = imgFromPoint(x, y);
        out.imgFromPoint = im ? String(im.getAttribute('src') || '').slice(-40) : null;
        return out;
    };
    return { deleteImageNode: deleteImageNode, showOverlay: showOverlay, hideOverlay: hideOverlay };
}
