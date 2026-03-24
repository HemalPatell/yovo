/* ═══════════════════════════════════════════════
   YOVO — Real-time Chat  (chat.js)
   ROOM_NAME, CURRENT_USER_ID, RECEIVER_ID,
   ITEM_ID, CSRF_TOKEN  defined in chat.html
═══════════════════════════════════════════════ */
'use strict';

/* ── DOM refs ─────────────────────────────────── */
const chatMessages = document.getElementById('chatMessages');
const chatInput    = document.getElementById('chatInput');
const sendBtn      = document.getElementById('sendBtn');
const wsStatus     = document.getElementById('wsStatus');
const wsForm       = document.getElementById('wsForm');
const postForm     = document.getElementById('postForm');

/* ── Scroll ───────────────────────────────────── */
function scrollBottom() {
  chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
}
scrollBottom();

/* ── Time format ──────────────────────────────── */
function fmtTime() {
  const d = new Date();
  let h = d.getHours(), m = d.getMinutes();
  const ap = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12;
  return `${h}:${String(m).padStart(2, '0')} ${ap}`;
}

/* ── Mark all sent messages as "Seen" ────────────
   Called when server sends messages_seen event     */
function markAllSeen() {
  document.querySelectorAll('.msg-group.sent .msg-meta').forEach(meta => {
    const sentTag = meta.querySelector('.sent-tag');
    if (sentTag) {
      sentTag.textContent = 'Seen \u2713\u2713';
      sentTag.classList.remove('sent-tag');
      sentTag.classList.add('seen-tag');
    }
  });
}

/* ── Append new bubble (for incoming WS messages) */
function appendBubble(content, isSelf, msgId, timestamp) {
  const empty = chatMessages.querySelector('.chat-empty');
  if (empty) empty.remove();

  const group = document.createElement('div');
  group.className = `msg-group ${isSelf ? 'sent' : 'recv'}`;
  group.id = `msg-${msgId || 'new-' + Date.now()}`;

  const row = document.createElement('div');
  row.className = 'msg-row';

  if (isSelf && msgId) {
    const actions = document.createElement('div');
    actions.className = 'msg-actions';
    actions.innerHTML = `
      <button class="msg-action-btn" onclick="startEdit(${msgId})" title="Edit">\u270f\ufe0f</button>
      <button class="msg-action-btn del-btn" onclick="deleteMsg(${msgId})" title="Delete">\ud83d\uddd1</button>`;
    row.appendChild(actions);
  }

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  if (msgId) bubble.id = `bubble-${msgId}`;
  bubble.textContent = content;
  row.appendChild(bubble);
  group.appendChild(row);

  if (isSelf && msgId) {
    const editWrap = document.createElement('div');
    editWrap.className = 'msg-edit-wrap';
    editWrap.id = `edit-wrap-${msgId}`;
    editWrap.innerHTML = `
      <input type="text" class="msg-edit-input" id="edit-input-${msgId}"
             value="${content.replace(/"/g, '&quot;')}"
             onkeydown="editKeydown(event, ${msgId})" />
      <button class="msg-edit-save"   onclick="saveEdit(${msgId})">Save</button>
      <button class="msg-edit-cancel" onclick="cancelEdit(${msgId})">Cancel</button>`;
    group.appendChild(editWrap);
  }

  const meta = document.createElement('div');
  meta.className = 'msg-meta';
  meta.textContent = timestamp || fmtTime();
  if (isSelf) {
    const tick = document.createElement('span');
    tick.className = 'sent-tag';
    tick.textContent = ' \u00b7 Sent \u2713';
    meta.appendChild(tick);
  }
  group.appendChild(meta);

  chatMessages.appendChild(group);
  scrollBottom();
}

/* ── WebSocket ────────────────────────────────── */
let socket, wsConnected = false;

function connectWS() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  try {
    socket = new WebSocket(`${proto}://${location.host}/ws/chat/${ROOM_NAME}/`);
  } catch (e) {
    showFallback();
    return;
  }

  socket.onopen = () => {
    wsConnected = true;
    wsStatus.textContent = '\u25cf Live';
    wsStatus.className = 'ws-status ok';
    wsForm.style.display = 'flex';
    postForm.style.display = 'none';
  };

  socket.onmessage = e => {
    const data = JSON.parse(e.data);

    if (data.type === 'messages_seen') {
      if (data.seen_by !== CURRENT_USER_ID) markAllSeen();
      return;
    }

    if (data.type === 'chat_message') {
      appendBubble(data.message, data.sender_id === CURRENT_USER_ID, data.msg_id, data.timestamp);
      if (data.sender_id !== CURRENT_USER_ID && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'mark_read' }));
      }
    }
  };

  socket.onclose = () => {
    wsConnected = false;
    showFallback();
    setTimeout(connectWS, 5000);
  };

  socket.onerror = () => showFallback();
}

function showFallback() {
  wsForm.style.display = 'none';
  postForm.style.display = 'block';
  wsStatus.textContent = '\u26a0 Using standard send';
  wsStatus.className = 'ws-status err';
}

function sendMessage() {
  const content = chatInput.value.trim();
  if (!content) return;
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      type:        'chat_message',
      message:     content,
      receiver_id: RECEIVER_ID,
      item_id:     ITEM_ID,
    }));
    chatInput.value = '';
    chatInput.focus();
  }
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

window.addEventListener('focus', () => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: 'mark_read' }));
  }
});

connectWS();

function startEdit(msgId) {
  const wrap  = document.getElementById(`edit-wrap-${msgId}`);
  const input = document.getElementById(`edit-input-${msgId}`);
  if (!wrap || !input) return;
  wrap.classList.add('open');
  input.focus(); input.select();
}

function cancelEdit(msgId) {
  const wrap = document.getElementById(`edit-wrap-${msgId}`);
  if (wrap) wrap.classList.remove('open');
}

function editKeydown(e, msgId) {
  if (e.key === 'Enter')  saveEdit(msgId);
  if (e.key === 'Escape') cancelEdit(msgId);
}

async function saveEdit(msgId) {
  const input = document.getElementById(`edit-input-${msgId}`);
  if (!input) return;
  const content = input.value.trim();
  if (!content) return;
  try {
    const res  = await fetch(`/message/${msgId}/edit/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `content=${encodeURIComponent(content)}`,
    });
    const data = await res.json();
    if (data.success) {
      const bubble = document.getElementById(`bubble-${msgId}`);
      if (bubble) bubble.textContent = data.content;
      cancelEdit(msgId);
      input.value = data.content;
      const meta = document.querySelector(`#msg-${msgId} .msg-meta`);
      if (meta && !meta.querySelector('.edited-tag')) {
        const tag = document.createElement('span');
        tag.className = 'edited-tag'; tag.textContent = ' \u00b7 edited';
        meta.appendChild(tag);
      }
    }
  } catch (err) { console.error('[YOVO] saveEdit error:', err); }
}

async function deleteMsg(msgId) {
  if (!confirm('Delete this message?')) return;
  try {
    const res  = await fetch(`/message/${msgId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN },
    });
    const data = await res.json();
    if (data.success) {
      const bubble = document.getElementById(`bubble-${msgId}`);
      if (bubble) { bubble.textContent = 'This message was deleted.'; bubble.classList.add('is-deleted'); }
      document.querySelector(`#msg-${msgId} .msg-actions`)?.remove();
      document.getElementById(`edit-wrap-${msgId}`)?.remove();
    }
  } catch (err) { console.error('[YOVO] deleteMsg error:', err); }
}