$(function () {

  /* ══ 工具函式 ═══════════════════════════════════════════════ */

  function showToast(msg, type = 'success') {
    const colors = { success: '#4caf82', error: '#e85b47', info: '#e8a847' };
    const $toast = $('<div>').text(msg).css({
      position: 'fixed', bottom: '2rem', left: '50%',
      transform: 'translateX(-50%)',
      background: colors[type] || colors.success,
      color: '#fff', padding: '12px 24px',
      borderRadius: '30px', fontSize: '0.9rem',
      fontWeight: '500', zIndex: 999,
      boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
      opacity: 0
    });
    $('body').append($toast);
    $toast.animate({ opacity: 1 }, 200);
    setTimeout(() => $toast.animate({ opacity: 0 }, 300, () => $toast.remove()), 3000);
  }

  function openModal(id)  { $(id).addClass('open'); }
  function closeModal(id) { $(id).removeClass('open'); }

  /* ══ 登入 Modal ═════════════════════════════════════════════ */

  $('#loginBtn').on('click', function () {
    openModal('#loginModal');
    $('#inputUsername').trigger('focus');
  });

  $('#closeModal').on('click', () => closeModal('#loginModal'));
  $('#loginModal').on('click', function (e) {
    if ($(e.target).is('#loginModal')) closeModal('#loginModal');
  });

  $('#submitLogin').on('click', submitLogin);
  $('#loginModal').on('keydown', function (e) {
    if (e.key === 'Enter') submitLogin();
  });

  function submitLogin() {
    const username = $('#inputUsername').val().trim();
    const password = $('#inputPassword').val();
    $('#loginError').text('');

    if (!username || !password) {
      $('#loginError').text('請填寫帳號與密碼');
      return;
    }

    $('#submitLogin').text('登入中...').prop('disabled', true);

    $.ajax({
      url: '/vendor/login',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ username, password }),
      success: function (data) {
        if (data.success) {
          showToast('歡迎回來，' + data.name + '！');
          setTimeout(() => location.reload(), 800);
        } else {
          $('#loginError').text(data.message || '帳號或密碼錯誤');
          $('#submitLogin').text('登入').prop('disabled', false);
        }
      },
      error: function () {
        $('#loginError').text('網路錯誤，請稍後再試');
        $('#submitLogin').text('登入').prop('disabled', false);
      }
    });
  }

/* ══漢堡選單點擊 ══════════════════════════════════════════ */
// Sidebar 小螢幕
$("#openSidebar").click(function () {
  $("#sidebar").addClass("show");
  $("#overlaySideber").show();
});

$("#closeSidebar, #overlaySideber").click(function () {
  $("#sidebar").removeClass("show");
  $("#overlaySideber").hide();
});

/* ══ 登出按鈕 ══════════════════════════════════════════ */
$("#logoutBtn").click(function () {
  $("#logoutPage").addClass("show");
  $("#overlayLogout").show();
});

$("#closeLogout, #overlayLogout").click(function () {
  $("#logoutPage").removeClass("show");
  $("#overlayLogout").hide();
});
$("#Logout").click(function () {
  window.location.href = "/vendor/logout";
});

  /* ══ 建立攤位 Modal ══════════════════════════════════════════ */

  $('#openStallForm').on('click', function () {
    openModal('#stallModal');
    $('#stallName').trigger('focus');
  });

  $('#closeStallModal').on('click', () => closeModal('#stallModal'));
  $('#stallModal').on('click', function (e) {
    if ($(e.target).is('#stallModal')) closeModal('#stallModal');
  });

  $('#submitStall').on('click', function () {
    const stall_name = $('#stallName').val().trim();
    const zone_type  = $('#zoneType').val();
    $('#stallError').text('');

    if (!stall_name) { $('#stallError').text('請填寫攤位名稱'); return; }
    if (!zone_type)  { $('#stallError').text('請選擇區域類型'); return; }

    $('#submitStall').text('送出中...').prop('disabled', true);

    $.ajax({
      url: '/vendor/stall',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ stall_name, zone_type }),
      success: function (data) {
        if (data.success) {
          closeModal('#stallModal');
          showToast('攤位申請已送出，等待管理員審核！');
          $('#stallName').val('');
          $('#zoneType').val('');
        } else {
          $('#stallError').text('送出失敗，請稍後再試');
        }
        $('#submitStall').text('送出申請').prop('disabled', false);
      },
      error: function () {
        $('#stallError').text('網路錯誤，請稍後再試');
        $('#submitStall').text('送出申請').prop('disabled', false);
      }
    });
  });

  /* ══ Filter Tabs ═════════════════════════════════════════════ */

  $('.filter-tabs').on('click', '.tab', function () {
    $('.filter-tabs .tab').removeClass('active');
    $(this).addClass('active');
  });

  /* ══ ESC 鍵關閉 Modal ════════════════════════════════════════ */

  $(document).on('keydown', function (e) {
    if (e.key === 'Escape') {
      closeModal('#loginModal');
      closeModal('#stallModal');
    }
  });

});

/* ══ 查看地圖按鈕 ════════════════════════════════════════════ */
function scrollToMap() {
  const map = document.getElementById('mapSection');
  if (map) map.scrollIntoView({ behavior: 'smooth' });
  // 若 sidebar 開著，順手關掉
  sidebar.classList.remove('show');
  overlaySideber.style.display = 'none';
}

// Hero 的「查看地圖」按鈕
$('.hero-actions .btn-secondary').on('click', scrollToMap);

// Sidebar 的「查看地圖」按鈕
$('.sidebar-actions .action-btn').filter(function() {
  return $(this).text().includes('查看地圖');
}).on('click', scrollToMap);