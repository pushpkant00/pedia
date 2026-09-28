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

  var editor;
  try {
    editor = new toastui.Editor({
      el: holder,
      height: '540px',
      initialEditType: 'wysiwyg',
      previewStyle: 'vertical',
      initialValue: contentField.value || '',
      usageStatistics: false,
      hooks: {
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
      }
    });
  } catch (error) {
    enablePlainEditor('The visual editor failed to start.', error);
    return;
  }

  form.addEventListener('submit', function () {
    contentField.value = editor.getHTML();
  });

  window.__pediaEditor = editor;
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

  var overlay = document.createElement('button');
  overlay.type = 'button';
  overlay.className = 'image-remove-btn';
  overlay.setAttribute('aria-label', 'Remove this image');
  overlay.textContent = '✕';
  document.body.appendChild(overlay);

  var activeImg = null;
  var ticker = 0;

  function hideOverlay() {
    overlay.style.display = 'none';
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
    var left = Math.min(Math.max(visRight - 34, host.left + 4), host.right - 32);
    var top = Math.min(Math.max(visTop + 6, host.top + 4), host.bottom - 32);
    overlay.style.display = 'block';
    overlay.style.left = left + 'px';
    overlay.style.top = top + 'px';
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
    positionOverlay(imgEl);
    if (activeImg) startTicker();
  }

  function imgFromTarget(t) {
    if (!t || t === overlay) return null;
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
    chain = chain.then(function () {
      var popup = document.querySelector('.toastui-editor-popup');
      var open = popup && popup.style.display !== 'none' &&
        getComputedStyle(popup).display !== 'none';
      if (open && editor.eventEmitter && typeof editor.eventEmitter.emit === 'function') {
        editor.eventEmitter.emit('closePopup');
      }
    });
    chain.catch(function (error) {
      window.alert('Image upload failed: ' + error.message);
    });
    return chain;
  }

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

    if (event.target === overlay) return;
    var img = imgFromTarget(event.target);
    if (!img && event.clientX !== undefined) {
      img = imgFromPoint(event.clientX, event.clientY);
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

  overlay.addEventListener('click', function () {
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

  return { deleteImageNode: deleteImageNode, showOverlay: showOverlay, hideOverlay: hideOverlay };
}
