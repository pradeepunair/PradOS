/**
 * Pradeep Nair — Website Chatbot Widget (Static / No-LLM version)
 *
 * Embed on any page with a single <script> tag:
 *   <script src="/widget.js"></script>
 *
 * No data-api-url needed — all answers are static (no server calls).
 * Dynamically loads qa-data.js from the same path as widget.js.
 * Also loads widget.css automatically.
 *
 * For local dev (FastAPI server), both files are served at localhost:8000.
 * For production (cPanel), both files sit at the site root.
 */

(function () {
  'use strict';

  // ── Resolve base path from this script's own URL ──────────────────────────
  const scriptEl  = document.currentScript;
  const scriptSrc = scriptEl ? scriptEl.src : '';
  const BASE_PATH = scriptSrc ? scriptSrc.replace(/\/widget\.js(\?.*)?$/, '') : '';
  // BASE_PATH: e.g. "https://pradeepunair.me" or "http://localhost:8000"

  // ── Load CSS ──────────────────────────────────────────────────────────────
  (function () {
    const link = document.createElement('link');
    link.rel  = 'stylesheet';
    link.href = BASE_PATH + '/widget.css?v=2';
    document.head.appendChild(link);
  })();

  // ── State ─────────────────────────────────────────────────────────────────
  let isOpen    = false;
  let answering = false;

  // ── Bootstrap: load qa-data.js then build UI ──────────────────────────────
  function bootstrap() {
    if (window.QA_DATA) {
      buildUI();
    } else {
      const s    = document.createElement('script');
      s.src      = BASE_PATH + '/qa-data.js';
      s.onload   = buildUI;
      s.onerror  = () => console.warn('[chatbot] Could not load qa-data.js');
      document.head.appendChild(s);
    }
  }

  // ── Build DOM ─────────────────────────────────────────────────────────────
  function buildUI() {
    // Floating trigger button
    const trigger = document.createElement('button');
    trigger.id = 'pn-chat-trigger';
    trigger.setAttribute('aria-label', 'Open chat assistant');
    trigger.innerHTML = `
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>`;
    trigger.onclick = toggleWindow;

    // Chat window
    const win = document.createElement('div');
    win.id = 'pn-chat-window';
    win.setAttribute('role', 'dialog');
    win.setAttribute('aria-label', "Prads Bot");
    win.innerHTML = `
      <div class="pn-chat-header">
        <div class="pn-chat-header-avatar">P</div>
        <div class="pn-chat-header-info">
          <strong>Prads Bot</strong>
          <span>Tap a question to learn more</span>
        </div>
        <button class="pn-close-btn" onclick="document.getElementById('pn-chat-window').classList.remove('pn-open')"
                aria-label="Close chat">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      <div class="pn-messages" id="pn-messages"></div>
      <div class="pn-footer-note">Tap a question · No data sent to any server</div>`;

    document.body.appendChild(trigger);
    document.body.appendChild(win);

    initChat();
  }

  // ── Initialise chat messages ───────────────────────────────────────────────
  function initChat() {
    const container = document.getElementById('pn-messages');
    container.innerHTML = '';

    // Greeting bot message
    addBotMsg(QA_DATA.greeting);

    // Question chips (compact — no category headers in widget)
    const allQs = QA_DATA.categories.flatMap(c => c.questions);
    const panel = document.createElement('div');
    panel.id = 'pn-panel';
    panel.style.cssText = 'display:flex;flex-direction:column;gap:5px;margin-top:4px;';

    // Category sections
    QA_DATA.categories.forEach(cat => {
      const label = document.createElement('div');
      label.style.cssText = 'font-size:10px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#94a3b8;margin-top:8px;padding-left:2px;';
      label.textContent = cat.label;
      panel.appendChild(label);

      cat.questions.forEach(qa => {
        const btn = document.createElement('button');
        btn.className = 'pn-suggestion';
        btn.textContent = qa.q;
        btn.onclick = () => handleQuestion(qa, panel);
        panel.appendChild(btn);
      });
    });

    container.appendChild(panel);
    scrollBottom();
  }

  // ── Handle question click ─────────────────────────────────────────────────
  async function handleQuestion(qa, panel) {
    if (answering) return;
    answering = true;

    panel.style.display = 'none';

    addUserMsg(qa.q);
    scrollBottom();

    const typingEl = addTyping();
    scrollBottom();

    await delay(600);

    typingEl.remove();
    addBotMsg(qa.a);

    // "Back" button
    const backBtn = document.createElement('button');
    backBtn.className = 'pn-suggestion';
    backBtn.style.cssText = 'margin-top:8px;color:#94a3b8;border-color:#334155;';
    backBtn.textContent = '← Ask another question';
    backBtn.onclick = () => {
      // Remove everything after the first bot message
      const container = document.getElementById('pn-messages');
      const children  = [...container.children];
      children.slice(1).forEach(el => el.remove());
      // Rebuild panel
      const newPanel = buildPanel();
      container.appendChild(newPanel);
      answering = false;
      scrollBottom();
    };
    document.getElementById('pn-messages').appendChild(backBtn);
    scrollBottom();
    answering = false;
  }

  // ── Build a fresh question panel ──────────────────────────────────────────
  function buildPanel() {
    const panel = document.createElement('div');
    panel.id = 'pn-panel';
    panel.style.cssText = 'display:flex;flex-direction:column;gap:5px;margin-top:4px;';

    QA_DATA.categories.forEach(cat => {
      const label = document.createElement('div');
      label.style.cssText = 'font-size:10px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#94a3b8;margin-top:8px;padding-left:2px;';
      label.textContent = cat.label;
      panel.appendChild(label);

      cat.questions.forEach(qa => {
        const btn = document.createElement('button');
        btn.className = 'pn-suggestion';
        btn.textContent = qa.q;
        btn.onclick = () => handleQuestion(qa, panel);
        panel.appendChild(btn);
      });
    });

    return panel;
  }

  // ── Toggle window open/close ──────────────────────────────────────────────
  function toggleWindow() {
    isOpen = !isOpen;
    document.getElementById('pn-chat-window').classList.toggle('pn-open', isOpen);
  }

  // ── DOM helpers ───────────────────────────────────────────────────────────
  function addBotMsg(text) {
    const container = document.getElementById('pn-messages');
    const wrap = document.createElement('div');
    wrap.className = 'pn-msg pn-bot';
    wrap.innerHTML = `
      <div class="pn-msg-av">AI</div>
      <div class="pn-bubble" style="white-space:pre-wrap">${escHtml(text)}</div>`;
    container.appendChild(wrap);
    return wrap;
  }

  function addUserMsg(text) {
    const container = document.getElementById('pn-messages');
    const wrap = document.createElement('div');
    wrap.className = 'pn-msg pn-user';
    wrap.innerHTML = `
      <div class="pn-msg-av">You</div>
      <div class="pn-bubble" style="white-space:pre-wrap">${escHtml(text)}</div>`;
    container.appendChild(wrap);
    return wrap;
  }

  function addTyping() {
    const container = document.getElementById('pn-messages');
    const wrap = document.createElement('div');
    wrap.className = 'pn-msg pn-bot';
    wrap.innerHTML = `
      <div class="pn-msg-av">AI</div>
      <div class="pn-bubble">
        <div class="pn-typing"><span></span><span></span><span></span></div>
      </div>`;
    container.appendChild(wrap);
    return wrap;
  }

  function scrollBottom() {
    const el = document.getElementById('pn-messages');
    if (el) el.scrollTop = el.scrollHeight;
  }

  function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

  function escHtml(str) {
    return String(str)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/\n/g,'<br>');
  }

  // ── Init ──────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrap);
  } else {
    bootstrap();
  }
})();
