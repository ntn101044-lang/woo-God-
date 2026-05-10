/* ══ 登入 Modal ═════════════════════════════════════════════ */
const loginBtn   = document.getElementById('loginBtn');
const loginModal = document.getElementById('loginModal');
const closeModal = document.getElementById('closeModal');
const loginError = document.getElementById('loginError');

if (loginBtn) {
  loginBtn.addEventListener('click', () => {
    loginModal.classList.add('open');
    document.getElementById('inputUsername').focus();
  });
}

if (closeModal) {
  closeModal.addEventListener('click', () => loginModal.classList.remove('open'));
}

if (loginModal) {
  loginModal.addEventListener('click', (e) => {
    if (e.target === loginModal) loginModal.classList.remove('open');
  });
}

/* ── 送出登入 ─────────────────────────────────────────────── */
const submitLogin = document.getElementById('submitLogin');
if (submitLogin) {
  submitLogin.addEventListener('click', async () => {
    const username = document.getElementById('inputUsername').value.trim();
    const password = document.getElementById('inputPassword').value;
    loginError.textContent = '';

    if (!username || !password) {
      loginError.textContent = '請填寫帳號與密碼';
      return;
    }

    submitLogin.textContent = '登入中...';
    submitLogin.disabled = true;

    try {
      const res  = await fetch('/vendor/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();

      if (data.success) {
        window.location.reload();
      } else {
        loginError.textContent = data.message || '登入失敗';
        submitLogin.textContent = '登入';
        submitLogin.disabled = false;
      }
    } catch {
      loginError.textContent = '網路錯誤，請稍後再試';
      submitLogin.textContent = '登入';
      submitLogin.disabled = false;
    }
  });
}

/* ── Enter 鍵送出 ─────────────────────────────────────────── */
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && loginModal?.classList.contains('open')) {
    submitLogin?.click();
  }
});

/* ══ 建立攤位 Modal ══════════════════════════════════════════ */
const openStallForm  = document.getElementById('openStallForm');
const stallModal     = document.getElementById('stallModal');
const closeStallModal= document.getElementById('closeStallModal');
const stallError     = document.getElementById('stallError');

if (openStallForm) {
  openStallForm.addEventListener('click', () => stallModal.classList.add('open'));
}
if (closeStallModal) {
  closeStallModal.addEventListener('click', () => stallModal.classList.remove('open'));
}
if (stallModal) {
  stallModal.addEventListener('click', (e) => {
    if (e.target === stallModal) stallModal.classList.remove('open');
  });
}

/* ── 送出攤位申請 ─────────────────────────────────────────── */
const submitStall = document.getElementById('submitStall');
if (submitStall) {
  submitStall.addEventListener('click', async () => {
    const stall_name = document.getElementById('stallName').value.trim();
    const zone_type  = document.getElementById('zoneType').value;
    stallError.textContent = '';

    if (!stall_name) { stallError.textContent = '請填寫攤位名稱'; return; }
    if (!zone_type)  { stallError.textContent = '請選擇區域類型'; return; }

    submitStall.textContent = '送出中...';
    submitStall.disabled = true;

    try {
      const res  = await fetch('/vendor/stall', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stall_name, zone_type })
      });
      const data = await res.json();

      if (data.success) {
        stallModal.classList.remove('open');
        showToast('攤位申請已送出，等待管理員審核！');
        submitStall.textContent = '送出申請';
        submitStall.disabled = false;
      } else {
        stallError.textContent = '送出失敗，請稍後再試';
        submitStall.textContent = '送出申請';
        submitStall.disabled = false;
      }
    } catch {
      stallError.textContent = '網路錯誤，請稍後再試';
      submitStall.textContent = '送出申請';
      submitStall.disabled = false;
    }
  });
}

/* ══ Filter Tabs ═════════════════════════════════════════════ */
document.querySelectorAll('.filter-tabs .tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.filter-tabs .tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
  });
});

/* ══ Toast 通知 ══════════════════════════════════════════════ */
function showToast(msg) {
  const toast = document.createElement('div');
  toast.textContent = msg;
  Object.assign(toast.style, {
    position: 'fixed', bottom: '2rem', left: '50%',
    transform: 'translateX(-50%)',
    background: '#4caf82', color: '#fff',
    padding: '12px 24px', borderRadius: '30px',
    fontSize: '0.9rem', fontWeight: '500',
    zIndex: '999', boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
    animation: 'fadeIn 0.3s ease'
  });
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}