(function () {
  var form = document.getElementById('edit-form');
  var contentField = document.getElementById('id_content');
  var holder = document.getElementById('editor');
  if (!form || !contentField || !holder) return;

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : '';
  }

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
          var data = new FormData();
          data.append('file', blob);
          fetch(holder.getAttribute('data-upload-url'), {
            method: 'POST',
            body: data,
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
          })
            .then(function (response) {
              return response.json().then(function (payload) {
                if (!response.ok) throw new Error(payload.error || 'Upload failed');
                return payload;
              });
            })
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
})();
