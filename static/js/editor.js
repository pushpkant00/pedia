function getCookie(name) {
  var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : '';
}

function uploadImageFile(holder, file) {
  var data = new FormData();
  data.append('file', file);
  return fetch(holder.getAttribute('data-upload-url'), {
    method: 'POST',
    body: data,
    headers: { 'X-CSRFToken': getCookie('csrftoken') }
  }).then(function (response) {
    return response.json().then(function (payload) {
      if (!response.ok) throw new Error(payload.error || 'Upload failed');
      return payload;
    });
  });
}

var imageWidths = {};

function extractImageWidths(html) {
  var map = {};
  if (!html) return map;
  try {
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var imgs = doc.body.querySelectorAll('img');
    for (var i = 0; i < imgs.length; i++) {
      var src = imgs[i].getAttribute('src');
      var w = imgs[i].getAttribute('width');
      if (src && w) map[src] = w;
    }
  } catch (e) {}
  return map;
}

function applyImageWidth(imgEl, w) {
  var n = parseInt(w, 10);
  if (!imgEl || !n || n < 16) return;
  imgEl.style.width = n + 'px';
  imgEl.style.height = 'auto';
  imgEl.setAttribute('width', String(n));
}

function restoreImageWidths(map) {
  if (!map) return;
  var imgs = document.querySelectorAll('#editor img');
  for (var i = 0; i < imgs.length; i++) {
    var w = map[imgs[i].getAttribute('src')];
    if (w) applyImageWidth(imgs[i], w);
  }
}

function syncImageWidths(html) {
  try {
    var live = document.querySelectorAll('#editor img');
    var liveW = {};
    for (var i = 0; i < live.length; i++) {
      var s = live[i].getAttribute('src');
      var lw = live[i].getAttribute('width');
      if (s && lw && !(s in liveW)) liveW[s] = lw;
    }
    var doc = new DOMParser().parseFromString(html || '', 'text/html');
    var out = doc.body.querySelectorAll('img');
    var changed = false;
    for (var j = 0; j < out.length; j++) {
      var osrc = out[j].getAttribute('src');
      var w = liveW[osrc] || imageWidths[osrc];
      if (w) {
        out[j].setAttribute('width', String(w).replace(/px$/, ''));
        changed = true;
      }
    }
    return changed ? doc.body.innerHTML : (html || '');
  } catch (e) {
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
    interval: parseInt(holder.getAttribute('data-autosave-interval'), 10) || 30,
    draftKey: 'pedia-draft:' + (holder.getAttribute('data-draft-key') || location.pathname)
  };
}

function readDraft(prefs, serverContent) {
  if (!prefs.autosave) return null;
  try {
    var raw = localStorage.getItem(prefs.draftKey);
    if (!raw) return null;
    var draft = JSON.parse(raw);
    if (!draft || !draft.html) {
      localStorage.removeItem(prefs.draftKey);
      return null;
    }
    // Restore only while the article still matches what the draft was started from.
    if ((draft.seed || '') !== (serverContent || '')) {
      localStorage.removeItem(prefs.draftKey);
      return null;
    }
    if (draft.html === serverContent) return null;
    return draft;
  } catch (error) {
    return null;
  }
}

function showDraftNotice(holder, draft, prefs) {
  var notice = document.createElement('div');
  notice.className = 'editor-draft-notice';
  var text = document.createElement('span');
  var when = new Date(draft.at);
  text.textContent = 'Unsaved draft restored (saved ' +
    (isNaN(when.getTime()) ? 'earlier' : when.toLocaleString()) + ').';
  var discard = document.createElement('button');
  discard.type = 'button';
  discard.className = 'link-button';
  discard.textContent = 'discard draft';
  discard.addEventListener('click', function () {
    try { localStorage.removeItem(prefs.draftKey); } catch (error) {}
    window.location.reload();
  });
  notice.appendChild(text);
  notice.appendChild(document.createTextNode(' '));
  notice.appendChild(discard);
  holder.parentNode.insertBefore(notice, holder);
}

(function () {
  var form = document.getElementById('edit-form');
  var contentField = document.getElementById('id_content');
  var holder = document.getElementById('editor');
  if (!form || !contentField || !holder) return;

  function enablePlainEditor(message, error) {
    console.error('[pedia editor] ' + message, error || '');
    var textarea = document.createElement('textarea');
    textarea.name = contentField.name;
    textarea.id = contentField.id;
    textarea.value = contentField.value;
    textarea.rows = 24;
    textarea.className = 'raw-textarea';
    textarea.setAttribute('aria-label', 'Article body (HTML)');
    contentField.parentNode.replaceChild(textarea, contentField);
    var banner = document.createElement('div');
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

  var prefs = readPrefs(holder);
  var serverContent = contentField.value || '';
  var draft = readDraft(prefs, serverContent);
  var initialValue = draft ? draft.html : serverContent;

  var FULL_ITEMS = [['heading', 'bold', 'italic', 'strike'], ['hr', 'quote'],
                    ['ul', 'ol', 'task', 'indent', 'outdent'], ['table', 'image', 'link'],
                    ['code', 'codeblock'], ['scrollSync']];
  var COMPACT_ITEMS = [['heading', 'bold', 'italic', 'link', 'image'], ['ol', 'ul', 'code']];

  function withoutImage(groups) {
    return groups
      .map(function (group) {
        return group.filter(function (name) { return name !== 'image'; });
      })
      .filter(function (group) { return group.length > 0; });
  }

  var editorOptions = {
    el: holder,
    height: '540px',
    initialEditType: prefs.mode === 'markdown' ? 'markdown' : 'wysiwyg',
    previewStyle: 'vertical',
    initialValue: initialValue,
    usageStatistics: false,
    theme: prefs.theme === 'dark' ? 'dark' : 'light'
  };

  var needCustomToolbar = prefs.toolbar === 'compact' || !prefs.uploads;
  if (needCustomToolbar) {
    var items = prefs.toolbar === 'compact' ? COMPACT_ITEMS : FULL_ITEMS;
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
            callback(payload.url, blob.name || payload.alt || 'image');
          })
          .catch(function (error) {
            window.alert('Image upload failed: ' + error.message);
          });
        return false;
      }
    };
  }

  var editor;
  var savedWidths = extractImageWidths(serverContent);
  try {
    editor = new toastui.Editor(editorOptions);
  } catch (error) {
    enablePlainEditor('The visual editor failed to start.', error);
    return;
  }

  if (draft) {
    showDraftNotice(holder, draft, prefs);
  }

  function saveDraftNow() {
    if (!prefs.autosave) return;
    try {
      var html = editor.getHTML();
      if (!html || html === '<p></p>' || html === serverContent) return;
      localStorage.setItem(prefs.draftKey, JSON.stringify({
        html: html,
        at: Date.now(),
        seed: serverContent
      }));
    } catch (error) { /* storage full or unavailable */ }
  }

  if (prefs.autosave) {
    setInterval(saveDraftNow, prefs.interval * 1000);
    window.addEventListener('pagehide', saveDraftNow);
  }

  form.addEventListener('submit', function () {
    contentField.value = syncImageWidths(editor.getHTML());
    if (prefs.autosave) {
      try { localStorage.removeItem(prefs.draftKey); } catch (error) {}
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
    var candidates = [];
    try { candidates.push(editor.view); } catch (e) {}
    try {
      var modeEditor = editor.getCurrentModeEditor && editor.getCurrentModeEditor();
      if (modeEditor) candidates.push(modeEditor.view, modeEditor.editorView);
    } catch (e) {}
    try { candidates.push(editor.wwEditor && editor.wwEditor.view); } catch (e) {}
    for (var i = 0; i < candidates.length; i++) {
      var view = candidates[i];
      if (view && view.state && view.state.doc && typeof view.dispatch === 'function') {
        return view;
      }
      if (view && view.view && view.view.state && typeof view.view.dispatch === 'function') {
        return view.view;
      }
    }
    return null;
  }

  function findImageTarget(view, imgEl) {
    var found = [];
    view.state.doc.descendants(function (node, pos) {
      if (node.type && node.type.name === 'image') {
        found.push({ pos: pos, node: node, src: node.attrs && node.attrs.src });
      }
    });
    if (!found.length) return null;

    var domPos = null;
    try { domPos = view.posAtDOM(imgEl, 0); } catch (e) {}
    if (typeof domPos === 'number') {
      var offsets = [domPos, domPos - 1, domPos + 1, domPos - 2];
      for (var i = 0; i < offsets.length; i++) {
        for (var j = 0; j < found.length; j++) {
          if (found[j].pos === offsets[i]) return found[j];
        }
      }
    }
    var sameSrc = found.filter(function (f) { return f.src && f.src === imgEl.src; });
    if (sameSrc.length === 1) return sameSrc[0];
    if (sameSrc.length > 1 && typeof domPos === 'number') {
      sameSrc.sort(function (a, b) {
        return Math.abs(a.pos - domPos) - Math.abs(b.pos - domPos);
      });
      return sameSrc[0];
    }
    return found.length === 1 ? found[0] : null;
  }

  function deleteImageNode(imgEl) {
    var view = getPMView();
    if (!view) return false;
    var target = findImageTarget(view, imgEl);
    if (!target) return false;
    try {
      view.dispatch(view.state.tr.delete(target.pos, target.pos + target.node.nodeSize));
      return true;
    } catch (error) {
      console.error('[pedia editor] image delete failed', error);
      return false;
    }
  }

  var toolbar = document.createElement('div');
  toolbar.className = 'image-tools';
  toolbar.setAttribute('role', 'toolbar');
  toolbar.setAttribute('aria-label', 'Image options');

  function toolButton(label, text) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'image-tool-btn';
    b.setAttribute('aria-label', label);
    b.title = label;
    b.textContent = text;
    toolbar.appendChild(b);
    return b;
  }

  var zoomOutBtn = toolButton('Zoom out', '−');
  var zoomInBtn = toolButton('Zoom in', '+');
  var downloadBtn = document.createElement('a');
  downloadBtn.className = 'image-tool-btn';
  downloadBtn.setAttribute('aria-label', 'Download image');
  downloadBtn.title = 'Download image';
  downloadBtn.textContent = '↓';
  downloadBtn.target = '_blank';
  downloadBtn.rel = 'noopener';
  toolbar.appendChild(downloadBtn);

  var removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.className = 'image-remove-btn';
  removeBtn.setAttribute('aria-label', 'Remove this image');
  removeBtn.textContent = '✕';
  toolbar.appendChild(removeBtn);

  document.body.appendChild(toolbar);

  var activeImg = null;
  var ticker = 0;

  function hideOverlay() {
    toolbar.style.display = 'none';
    activeImg = null;
    if (ticker) {
      clearInterval(ticker);
      ticker = 0;
    }
  }

  function getClipHost() {
    var all = holder.getElementsByTagName('*');
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.scrollHeight > el.clientHeight + 40 && el.clientHeight > 150) return el;
    }
    return holder;
  }

  function positionOverlay(imgEl) {
    var rect = imgEl.getBoundingClientRect();
    var host = getClipHost().getBoundingClientRect();
    var visTop = Math.max(rect.top, host.top);
    var visBottom = Math.min(rect.bottom, host.bottom);
    var visLeft = Math.max(rect.left, host.left);
    var visRight = Math.min(rect.right, host.right);
    if (visBottom - visTop < 12 || visRight - visLeft < 12) return hideOverlay();
    toolbar.style.display = 'flex';
    var tw = toolbar.offsetWidth || 130;
    var th = toolbar.offsetHeight || 32;
    var left = Math.max(host.left + 4, Math.min(visRight - tw - 4, host.right - tw - 4));
    var top = Math.max(host.top + 4, Math.min(visTop + 6, host.bottom - th - 4));
    toolbar.style.left = left + 'px';
    toolbar.style.top = top + 'px';
  }

  function startTicker() {
    if (!ticker) {
      ticker = setInterval(function () {
        if (activeImg && document.body.contains(activeImg)) positionOverlay(activeImg);
        else hideOverlay();
      }, 250);
    }
  }

  function showOverlay(imgEl) {
    if (!imgEl.getAttribute('src')) return hideOverlay();
    activeImg = imgEl;
    var src = imgEl.currentSrc || imgEl.src;
    var name = 'image';
    try {
      name = decodeURIComponent((src.split('?')[0].split('/').pop()) || 'image') || 'image';
    } catch (e) {}
    downloadBtn.href = src;
    downloadBtn.setAttribute('download', name);
    positionOverlay(imgEl);
    if (activeImg) startTicker();
  }

  function zoomImage(imgEl, dir) {
    if (!imgEl || !document.body.contains(imgEl)) return null;
    var w = imgEl.getBoundingClientRect().width;
    if (!w) return null;
    var next = Math.round(w * (dir > 0 ? 1.25 : 0.8));
    var parentW = imgEl.parentElement && imgEl.parentElement.getBoundingClientRect().width;
    var max = Math.max(Math.round(parentW || holder.getBoundingClientRect().width) - 8, Math.round(w));
    next = Math.max(60, Math.min(next, max));
    if (next === Math.round(w)) return { w: w, next: next, max: max, skipped: true };
    applyImageWidth(imgEl, next);
    imageWidths[imgEl.getAttribute('src')] = String(next);
    positionOverlay(imgEl);
    return { w: w, next: next, max: max, skipped: false };
  }

  function imgFromTarget(t) {
    if (!t || (toolbar && toolbar.contains(t))) return null;
    if (t.tagName === 'IMG') return t;
    if (t.closest) {
      var inside = t.closest('img');
      if (inside && holder.contains(inside)) return inside;
    }
    return null;
  }

  function imgFromPoint(x, y) {
    var imgs = holder.querySelectorAll('img');
    for (var i = 0; i < imgs.length; i++) {
      var r = imgs[i].getBoundingClientRect();
      if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) return imgs[i];
    }
    return null;
  }

  function imageAdjacentToCaret(x, y) {
    if (typeof x !== 'number' || typeof y !== 'number' || !document.caretRangeFromPoint) return null;
    var range = null;
    try { range = document.caretRangeFromPoint(x, y); } catch (e) { return null; }
    if (!range) return null;
    var node = range.startContainer;
    var off = range.startOffset;
    var isImg = function (el) { return el && el.nodeType === 1 && el.tagName === 'IMG'; };
    var isBlank = function (el) { return el && el.nodeType === 3 && !/\S/.test(el.textContent || ''); };
    var candidate = null;
    if (node.nodeType === 1) {
      var kids = node.childNodes;
      var a = kids[off], b = kids[off - 1];
      if (isImg(a)) candidate = a;
      else if (isImg(b)) candidate = b;
      else if (isBlank(a) && isImg(kids[off + 1])) candidate = kids[off + 1];
      else if (isBlank(b) && isImg(kids[off - 2])) candidate = kids[off - 2];
    } else if (node.nodeType === 3) {
      var prev = node.previousSibling, next = node.nextSibling;
      var text = node.textContent || '';
      if (off === 0 && isImg(prev)) candidate = prev;
      else if (off >= text.length && isImg(next)) candidate = next;
      else if (off === 0 && isBlank(prev) && isImg(prev.previousSibling)) candidate = prev.previousSibling;
      else if (off >= text.length && isBlank(next) && isImg(next.nextSibling)) candidate = next.nextSibling;
    }
    return candidate;
  }

  function ensureFileInputMultiple() {
    var fi = document.getElementById('toastuiImageFileInput');
    if (fi && !fi.multiple) fi.multiple = true;
  }

  function insertImage(url, alt) {
    if (editor.eventEmitter && typeof editor.eventEmitter.emit === 'function') {
      editor.eventEmitter.emit('command', 'addImage', { imageUrl: url, altText: alt || 'image' });
    } else if (typeof editor.exec === 'function') {
      editor.exec('addImage', { imageUrl: url, altText: alt || 'image' });
    }
  }

  function insertFiles(files) {
    var altInput = document.getElementById('toastuiAltTextInput');
    var alt = (altInput && altInput.value) || '';
    var chain = Promise.resolve();
    Array.prototype.forEach.call(files, function (file) {
      chain = chain.then(function () {
        return uploadImageFile(holder, file).then(function (payload) {
          insertImage(payload.url, alt || file.name || payload.alt || 'image');
        });
      });
    });
    chain.catch(function (error) {
      window.alert('Image upload failed: ' + error.message);
    });
    return chain;
  }

  document.addEventListener('mousedown', function (event) {
    if (event.button !== 0 || !event.target) return;
    if (event.target.closest && event.target.closest('.toastui-editor-popup')) return;
    if (toolbar.contains(event.target)) return;
    var img = imgFromTarget(event.target);
    if (!img && typeof event.clientX === 'number') {
      img = imgFromPoint(event.clientX, event.clientY) ||
        imageAdjacentToCaret(event.clientX, event.clientY);
    }
    if (img && holder.contains(img)) {
      event.preventDefault();
      event.stopPropagation();
    }
  }, true);

  document.addEventListener('click', function (event) {
    ensureFileInputMultiple();
    setTimeout(ensureFileInputMultiple, 0);

    var btn = event.target && event.target.closest ? event.target.closest('button') : null;
    if (btn && /ok-button/.test(btn.className || '') && btn.closest('.toastui-editor-popup')) {
      var fi = document.getElementById('toastuiImageFileInput');
      if (fi && fi.files && fi.files.length > 1) {
        event.preventDefault();
        event.stopImmediatePropagation();
        var picked = Array.prototype.slice.call(fi.files);
        try { fi.value = ''; } catch (e) {}
        insertFiles(picked);
        return;
      }
    }

    if (event.target && event.target.closest && event.target.closest('.toastui-editor-popup')) {
      hideOverlay();
      return;
    }

    if (event.target && toolbar.contains(event.target)) return;
    var img = imgFromTarget(event.target);
    if (!img && event.clientX !== undefined) {
      img = imgFromPoint(event.clientX, event.clientY) ||
        imageAdjacentToCaret(event.clientX, event.clientY);
    }
    if (img && holder.contains(img)) {
      event.preventDefault();
      showOverlay(img);
    } else {
      hideOverlay();
    }
  }, true);

  document.addEventListener('drop', function (event) {
    var files = event.dataTransfer && event.dataTransfer.files;
    if (!files || files.length < 2) return;
    var images = Array.prototype.filter.call(files, function (f) {
      return f.type && f.type.indexOf('image/') === 0;
    });
    if (images.length < 2) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    insertFiles(images);
  }, true);

  document.addEventListener('paste', function (event) {
    var items = event.clipboardData && event.clipboardData.items;
    if (!items) return;
    var images = [];
    for (var i = 0; i < items.length; i++) {
      if (items[i].kind === 'file' && items[i].type.indexOf('image/') === 0) {
        var f = items[i].getAsFile();
        if (f) images.push(f);
      }
    }
    if (images.length < 2) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    insertFiles(images);
  }, true);

  zoomOutBtn.addEventListener('click', function () {
    var r = zoomImage(activeImg, -1);
    if (r) window.__pediaLastZoom = { dir: -1, r: r };
  });

  zoomInBtn.addEventListener('click', function () {
    var r = zoomImage(activeImg, 1);
    if (r) window.__pediaLastZoom = { dir: 1, r: r };
  });

  removeBtn.addEventListener('click', function () {
    if (!activeImg) return hideOverlay();
    var img = activeImg;
    hideOverlay();
    if (!document.body.contains(img)) return;
    if (!deleteImageNode(img)) {
      window.alert('Could not remove the image automatically — select it and press Delete.');
    }
  });

  window.addEventListener('scroll', function () {
    if (!activeImg) return;
    if (document.body.contains(activeImg)) positionOverlay(activeImg);
    else hideOverlay();
  }, true);

  window.addEventListener('resize', function () {
    if (activeImg && document.body.contains(activeImg)) positionOverlay(activeImg);
  });

  ensureFileInputMultiple();

  window.__pediaAdjProbe = function (x, y) {
    var out = { range: null, resolved: null };
    var range = null;
    try { range = document.caretRangeFromPoint(x, y); } catch (e) { out.err = String(e); }
    if (range) {
      var c = range.startContainer, o = range.startOffset;
      var info = { container: c.nodeName || c.nodeType, off: o };
      if (c.nodeType === 1) {
        info.kids = Array.prototype.map.call(c.childNodes, function (n) { return n.nodeName; }).join(',');
      } else if (c.nodeType === 3) {
        info.text = (c.textContent || '').slice(0, 60);
        info.prev = c.previousSibling && c.previousSibling.nodeName;
        info.next = c.nextSibling && c.nextSibling.nodeName;
        info.len = (c.textContent || '').length;
      }
      out.range = info;
    }
    var adj = imageAdjacentToCaret(x, y);
    out.resolved = adj ? adj.tagName : null;
    out.resolvedSrc = adj ? String(adj.getAttribute('src') || '').slice(-40) : null;
    out.imgFromPoint = (function () {
      var im = imgFromPoint(x, y);
      return im ? String(im.getAttribute('src') || '').slice(-40) : null;
    })();
    return out;
  };

  return { deleteImageNode: deleteImageNode, showOverlay: showOverlay, hideOverlay: hideOverlay };
}
