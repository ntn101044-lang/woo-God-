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

  window.openModal = function(id) { $(id).addClass('open'); };
  window.closeModal = function(id) { $(id).removeClass('open'); };
  
  // 訂單狀態中文對照
  const STATUS_LABEL = {
    placed:      '已下單',
    confirming:  '確認中',
    making:      '製作中',
    ready:       '待取餐',
    completed:   '已完成',
    cancelled:   '已取消'
  };
  const STATUS_COLOR = {
    placed:      '#e8a847',
    confirming:  '#4a9eff',
    making:      '#a78bfa',
    ready:       '#4caf82',
    completed:   '#9b9890',
    cancelled:   '#e85b47'
  };

  /* ══ 登入 Modal ═════════════════════════════════════════════ */

  // 會員登入按鈕
$('#loginBtn').on('click', function () {
  openModal('#visitorLoginModal');
  $('#vLoginAccount').trigger('focus');
});

// 攤主登入按鈕
$('#vendorLoginTrigger').on('click', function () {
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

  /* ══ 漢堡選單點擊與四大核心跳轉 ════════════════════════════════ */
  $("#openSidebar").click(function () {
    $("#sidebar").addClass("show");
    $("#overlaySideber").show(); // 🎯 修正拼字：確保對應 HTML 裡的 id="overlaySideber"
  });

  // 點擊關閉按鈕或遮罩時隱藏側邊欄
  $("#closeSidebar, #overlaySideber").click(function () {
    $("#sidebar").removeClass("show");
    $("#overlaySideber").hide();
  });

  // 💡 【全新優化】控制四大功能點擊後的平滑滾動跳轉
  $(".sidebar-menu .menu-item").on('click', function (e) {
    e.preventDefault(); 
    const targetId = $(this).attr('href'); 
    const $target = $(targetId);

    if ($target.length) {
      $('html, body').animate({ scrollTop: $target.offset().top - 150 }, 500);
    }

    // 跳轉完成後收起側邊欄
    $("#sidebar").removeClass("show");
    $("#overlaySideber").hide();
  });

  /* ══ 登出按鈕 ════════════════════════════════════════════════ */
  $("#logoutBtn").click(function () {
    $("#logoutPage").addClass("show");
    $("#overlayLogout").show();
  });

  $("#closeLogout, #closeLogout2, #overlayLogout").click(function () {
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
          // ╔═ 【修正】建立成功後 reload，讓攤主後台即時更新 ═╗
          showToast('攤位已建立！');
          setTimeout(() => location.reload(), 800);
        } else {
          $('#stallError').text(data.message || '送出失敗，請稍後再試');
        }
        $('#submitStall').text('送出申請').prop('disabled', false);
      },
      error: function () {
        $('#stallError').text('網路錯誤，請稍後再試');
        $('#submitStall').text('送出申請').prop('disabled', false);
      }
    });
  });

  /* ══ 遊客登入 / 註冊 Modal ═══════════════════════════════════ */

  $('#visitorLoginBtn').on('click', function () {
    pendingOrder = null;
    openModal('#visitorLoginModal');
    $('#vLoginAccount').trigger('focus');
  });

  $('#closeVisitorLogin').on('click', () => closeModal('#visitorLoginModal'));
  $('#visitorLoginModal').on('click', function (e) {
    if ($(e.target).is('#visitorLoginModal')) closeModal('#visitorLoginModal');
  });

  // Tab 切換（登入 / 註冊）
  $('.modal-tab').on('click', function () {
    $('.modal-tab').removeClass('active');
    $(this).addClass('active');
    const tab = $(this).data('tab');
    if (tab === 'login') {
      $('#visitorLoginForm').show();
      $('#visitorRegisterForm').hide();
    } else {
      $('#visitorLoginForm').hide();
      $('#visitorRegisterForm').show();
    }
    $('#vLoginError, #vRegError').text('');
  });

  $('#submitVisitorLogin').on('click', submitVisitorLogin);
  $('#visitorLoginModal').on('keydown', function (e) {
    if (e.key === 'Enter') {
      if ($('#visitorLoginForm').is(':visible')) submitVisitorLogin();
      else submitVisitorRegister();
    }
  });

  function submitVisitorLogin() {
    const account  = $('#vLoginAccount').val().trim();
    const password = $('#vLoginPassword').val();
    $('#vLoginError').text('');
    if (!account || !password) { $('#vLoginError').text('請填寫帳號與密碼'); return; }

    $('#submitVisitorLogin').text('登入中...').prop('disabled', true);
    $.ajax({
      url: '/visitor/login', method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ account, password }),
      success: function (data) {
        if (data.success) {
          closeModal('#visitorLoginModal');
          updateVisitorUI(data.account);
          showToast('歡迎回來，' + data.account + '！');
          if (pendingOrder) doPlaceOrder();
        } else {
          $('#vLoginError').text(data.message || '帳號或密碼錯誤');
        }
        $('#submitVisitorLogin').text('登入並下單').prop('disabled', false);
      },
      error: function () {
        $('#vLoginError').text('網路錯誤，請稍後再試');
        $('#submitVisitorLogin').text('登入並下單').prop('disabled', false);
      }
    });
  }

  $('#submitVisitorRegister').on('click', submitVisitorRegister);

  function submitVisitorRegister() {
    const account  = $('#vRegAccount').val().trim();
    const password = $('#vRegPassword').val();
    $('#vRegError').text('');
    if (!account || !password) { $('#vRegError').text('請填寫帳號與密碼'); return; }
    if (password.length < 4)   { $('#vRegError').text('密碼至少 4 個字元'); return; }

    $('#submitVisitorRegister').text('註冊中...').prop('disabled', true);
    $.ajax({
      url: '/visitor/register', method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ account, password }),
      success: function (data) {
        if (data.success) {
          closeModal('#visitorLoginModal');
          updateVisitorUI(data.account);
          showToast('註冊成功，歡迎 ' + data.account + '！');
          if (pendingOrder) doPlaceOrder();
        } else {
          $('#vRegError').text(data.message || '註冊失敗');
        }
        $('#submitVisitorRegister').text('註冊並下單').prop('disabled', false);
      },
      error: function () {
        $('#vRegError').text('網路錯誤，請稍後再試');
        $('#submitVisitorRegister').text('註冊並下單').prop('disabled', false);
      }
    });
  }

  // 更新 Navbar 遊客狀態
  function updateVisitorUI(account) {
    if (account) {
      $('#visitorAccount').text('👤 ' + account);
      $('#visitorInfo').show();
      
      // 🎯 關鍵修正：遊客登入後，同時隱藏「會員登入」與「攤主登入」按鈕！
      $('#loginBtn').hide();
      $('#vendorLoginTrigger').hide(); 

      // 顯示 FAB 並更新 badge
      $('#visitorFab').show();
      updateFabBadge();
    } else {
      $('#visitorInfo').hide();
      
      // 🎯 關鍵修正：如果是未登出/未登入狀態，要把兩個按鈕都秀回來
      $('#loginBtn').show();
      $('#vendorLoginTrigger').show();

      // 隱藏 FAB
      $('#visitorFab').hide();
    }
  }

  // 會員登出按鈕點擊事件
  $(document).on('click', '#visitorLogoutBtn', function () {
    if (confirm('確定要登出會員嗎？')) {
      // 呼叫後端的遊客登出路由 (對齊你們 app.py 的設計)
      window.location.href = "/visitor/logout"; 
    }
  });

  // 頁面載入時檢查遊客 session
  function checkVisitorSession() {
    $.get('/visitor/session', function (data) {
      if (data.logged_in) {
        updateVisitorUI(data.account);
      } else {
        updateVisitorUI(null);
      }
    });
  }
  if ($('#visitorLoginBtn').length) checkVisitorSession();

  /* ══ 攤位商品 & 購物車 ════════════════════════════════════════ */

  let cart           = {};
  let currentStallId = null;
  let pendingOrder   = null;

  $(document).on('click', '.open-stall-btn', function () {
    // ╔═ 【修正】scroll-card 本身就是 .open-stall-btn，直接取 data；
    //           stall-card 內的按鈕則往上找父元素，兩者都能正確取到 stall_id ═╗
    const stallId = $(this).data('stall-id') ||
                    $(this).closest('[data-stall-id]').data('stall-id');
    if (!stallId) return;
    openStallProducts(stallId);
  });

  function openStallProducts(stallId) {
    currentStallId = stallId;
    cart = {};
    renderCart();
    $('#productList').html('<p class="loading-text">載入商品中...</p>');
    $('#orderError').text('');
    openModal('#stallProductModal');

    $.get('/stall/' + stallId + '/products', function (data) {
      $('#stallProductTitle').text(data.stall_name);
      $('#stallProductZone').text(data.zone_type || '');
      renderProducts(data.products);
    }).fail(function () {
      $('#productList').html('<p class="loading-text">載入失敗，請稍後再試</p>');
    });
  }

  function renderProducts(products) {
    if (!products || products.length === 0) {
      $('#productList').html('<p class="loading-text">此攤位尚未新增商品</p>');
      return;
    }
    const $list = $('<div class="product-grid">');
    products.forEach(function (p) {
      const $item = $(`
        <div class="product-item" data-id="${p.product_id}" data-name="${p.name}" data-price="${p.price}">
          <div class="product-name">${p.name}</div>
          <div class="product-price">$${p.price}</div>
          <div class="product-qty-ctrl">
            <button class="qty-btn qty-minus">－</button>
            <span class="qty-num">0</span>
            <button class="qty-btn qty-plus">＋</button>
          </div>
        </div>
      `);
      $list.append($item);
    });
    $('#productList').html($list);
  }

  $(document).on('click', '.qty-plus', function () {
    const $item  = $(this).closest('.product-item');
    const id     = $item.data('id');
    const name   = $item.data('name');
    const price  = parseFloat($item.data('price'));
    if (!cart[id]) cart[id] = { name, price, quantity: 0 };
    cart[id].quantity++;
    $item.find('.qty-num').text(cart[id].quantity);
    renderCart();
  });

  $(document).on('click', '.qty-minus', function () {
    const $item = $(this).closest('.product-item');
    const id    = $item.data('id');
    if (!cart[id] || cart[id].quantity === 0) return;
    cart[id].quantity--;
    $item.find('.qty-num').text(cart[id].quantity);
    if (cart[id].quantity === 0) delete cart[id];
    renderCart();
  });

  function renderCart() {
    const ids = Object.keys(cart);
    if (ids.length === 0) {
      $('#cartItems').html('<p class="cart-empty">尚未選擇任何商品</p>');
      $('#cartTotal').text('$0');
      return;
    }
    let total = 0;
    const $rows = $('<div>');
    ids.forEach(function (id) {
      const item = cart[id];
      total += item.price * item.quantity;
      $rows.append(`
        <div class="cart-row">
          <span class="cart-item-name">${item.name}</span>
          <span class="cart-item-detail">x${item.quantity}　$${(item.price * item.quantity).toFixed(0)}</span>
        </div>
      `);
    });
    $('#cartItems').html($rows);
    $('#cartTotal').text('$' + total.toFixed(0));
  }

  $('#closeStallProduct').on('click', () => closeModal('#stallProductModal'));
  $('#stallProductModal').on('click', function (e) {
    if ($(e.target).is('#stallProductModal')) closeModal('#stallProductModal');
  });

  /* ══ 送出訂單 ════════════════════════════════════════════════ */

  $('#submitOrder').on('click', function () {
    const ids = Object.keys(cart);
    if (ids.length === 0) { $('#orderError').text('請先選擇商品'); return; }

    pendingOrder = {
      stall_id: currentStallId,
      items: ids.map(id => ({ product_id: id, quantity: cart[id].quantity }))
    };

    $.get('/visitor/session', function (data) {
      if (data.logged_in) {
        doPlaceOrder();
      } else {
        closeModal('#stallProductModal');
        openModal('#visitorLoginModal');
        $('#vLoginAccount').trigger('focus');
      }
    });
  });

  function doPlaceOrder() {
    if (!pendingOrder) return;
    $('#submitOrder').text('送出中...').prop('disabled', true);

    $.ajax({
      url: '/order/place', method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(pendingOrder),
      success: function (data) {
        if (data.success) {
          closeModal('#stallProductModal');
          closeModal('#visitorLoginModal');
          showToast('訂單送出成功！訂單編號：' + data.order_id.slice(0, 8) + '...');
          cart = {};
          pendingOrder = null;
          // ╔═ 【新增】下單成功後更新 FAB badge ═╗
          updateFabBadge();
        } else {
          $('#orderError').text(data.message || '下單失敗，請稍後再試');
          openModal('#stallProductModal');
        }
        $('#submitOrder').text('確認下單').prop('disabled', false);
      },
      error: function () {
        $('#orderError').text('網路錯誤，請稍後再試');
        $('#submitOrder').text('確認下單').prop('disabled', false);
        openModal('#stallProductModal');
      }
    });
  }

  /* ══ 遊客查詢自己的訂單 ══════════════════════════════════════ */

  // ╔═ 【新增】FAB 按鈕（右下角）點擊開啟訂單 Modal ═╗
  $('#fabOrderBtn').on('click', function () {
    openModal('#myOrdersModal');
    loadMyOrders();
  });

  $('#myOrdersBtn').on('click', function () {
    openModal('#myOrdersModal');
    loadMyOrders();
  });

  function loadMyOrders() {
    $('#myOrdersList').html('<p class="loading-text">載入中...</p>');
    $.get('/visitor/orders', function (data) {
      if (data.orders.length === 0) {
        $('#myOrdersList').html('<p class="loading-text">目前沒有訂單</p>');
        return;
      }
      const $list = $('<div>');
      data.orders.forEach(function (o) {
        $list.append(buildOrderCard(o, 'visitor'));
      });
      $('#myOrdersList').html($list);
      // ╔═ 【新增】載入訂單後同步更新 badge ═╗
      const active = data.orders.filter(o => !['completed','cancelled'].includes(o.status)).length;
      if (active > 0) { $('#fabBadge').text(active).show(); }
      else            { $('#fabBadge').hide(); }
    }).fail(function () {
      $('#myOrdersList').html('<p class="loading-text">載入失敗</p>');
    });
  }

  $('#closeMyOrders').on('click', () => closeModal('#myOrdersModal'));
  $('#myOrdersModal').on('click', function (e) {
    if ($(e.target).is('#myOrdersModal')) closeModal('#myOrdersModal');
  });

  // ╔═ 【新增】FAB badge 更新函式（AJAX 查詢進行中訂單數量）═╗
  function updateFabBadge() {
    $.get('/visitor/orders', function (data) {
      const active = (data.orders || []).filter(
        o => !['completed', 'cancelled'].includes(o.status)
      ).length;
      if (active > 0) { $('#fabBadge').text(active).show(); }
      else            { $('#fabBadge').hide(); }
    });
  }

  /* ══ 攤主訂單管理 ════════════════════════════════════════════ */

  $('#vendorOrdersBtn').on('click', function () {
    openModal('#vendorOrdersModal');
    loadVendorOrders();
  });

  function loadVendorOrders() {
    $('#vendorOrdersList').html('<p class="loading-text">載入中...</p>');
    $.get('/vendor/orders', function (data) {
      if (data.orders.length === 0) {
        $('#vendorOrdersList').html('<p class="loading-text">目前沒有訂單</p>');
        return;
      }
      const $list = $('<div>');
      data.orders.forEach(function (o) {
        $list.append(buildOrderCard(o, 'vendor'));
      });
      $('#vendorOrdersList').html($list);
    }).fail(function () {
      $('#vendorOrdersList').html('<p class="loading-text">載入失敗</p>');
    });
  }

  $('#closeVendorOrders').on('click', () => closeModal('#vendorOrdersModal'));
  $('#vendorOrdersModal').on('click', function (e) {
    if ($(e.target).is('#vendorOrdersModal')) closeModal('#vendorOrdersModal');
  });

  $(document).on('click', '.order-next-btn', function () {
    const orderId   = $(this).data('order-id');
    const newStatus = $(this).data('next-status');
    const $btn      = $(this);

    $btn.text('更新中...').prop('disabled', true);
    $.ajax({
      url: '/order/' + orderId + '/status',
      method: 'PATCH',
      contentType: 'application/json',
      data: JSON.stringify({ status: newStatus }),
      success: function (data) {
        if (data.success) {
          showToast('訂單已更新為：' + STATUS_LABEL[data.status]);
          loadVendorOrders();
        } else {
          showToast(data.message, 'error');
          $btn.text('更新').prop('disabled', false);
        }
      },
      error: function () {
        showToast('更新失敗，請稍後再試', 'error');
        $btn.text('更新').prop('disabled', false);
      }
    });
  });

  $(document).on('click', '.order-cancel-btn', function () {
    if (!confirm('確定要取消這筆訂單嗎？')) return;
    const orderId = $(this).data('order-id');
    $.ajax({
      url: '/order/' + orderId + '/status',
      method: 'PATCH',
      contentType: 'application/json',
      data: JSON.stringify({ status: 'cancelled' }),
      success: function (data) {
        if (data.success) {
          showToast('訂單已取消', 'info');
          loadVendorOrders();
        }
      }
    });
  });

  /* ══ 共用訂單卡片建構函式 ════════════════════════════════════ */

  function buildOrderCard(o, viewAs) {
    const color   = STATUS_COLOR[o.status] || '#9b9890';
    const label   = STATUS_LABEL[o.status] || o.status;
    const shortId = o.order_id.slice(0, 8);

    let itemsHtml = '';
    let total = 0;
    o.items.forEach(function (i) {
      const sub = i.sold_price * i.quantity;
      total += sub;
      itemsHtml += `<div class="order-item-row">
        <span>${i.name} x${i.quantity}</span>
        <span>$${sub.toFixed(0)}</span>
      </div>`;
    });

    let actionHtml = '';
    if (viewAs === 'vendor') {
      const NEXT = {
        placed:     { status: 'confirming', label: '✅ 確認接單' },
        confirming: { status: 'making',     label: '🍳 開始製作' },
        making:     { status: 'ready',      label: '🔔 通知取餐' },
        ready:      { status: 'completed',  label: '✔ 完成取餐' }
      };
      const next = NEXT[o.status];
      if (next) {
        actionHtml += `<button class="btn btn-sm btn-primary order-next-btn"
          data-order-id="${o.order_id}" data-next-status="${next.status}">
          ${next.label}
        </button>`;
      }
      if (o.status !== 'completed' && o.status !== 'cancelled') {
        actionHtml += `<button class="btn btn-sm btn-cancel order-cancel-btn"
          data-order-id="${o.order_id}">取消訂單</button>`;
      }
    }

    const subInfo = viewAs === 'vendor'
      ? `👤 ${o.visitor_account}`
      : `🏪 ${o.stall_name}`;

    return $(`
      <div class="order-card">
        <div class="order-card-header">
          <div>
            <span class="order-id">#${shortId}</span>
            <span class="order-sub">${subInfo}</span>
          </div>
          <span class="order-status-badge" style="background:${color}20;color:${color};border:1px solid ${color}40">
            ${label}
          </span>
        </div>
        <div class="order-items">${itemsHtml}</div>
        <div class="order-footer">
          <span class="order-time">${o.order_time}</span>
          <span class="order-total">合計 $${(o.total || total).toFixed(0)}</span>
        </div>
        ${actionHtml ? `<div class="order-actions">${actionHtml}</div>` : ''}
      </div>
    `);
  }

  // ╔═ 【新增】攤主商品管理 Modal ═╗
  $(document).on('click', '.open-product-mgmt', function () {
    openModal('#productMgmtModal');
    loadVendorProducts();
  });

  $('#closeProductMgmt').on('click', () => closeModal('#productMgmtModal'));
  $('#productMgmtModal').on('click', function (e) {
    if ($(e.target).is('#productMgmtModal')) closeModal('#productMgmtModal');
  });

  function loadVendorProducts() {
    $('#productMgmtList').html('<p class="loading-text">載入中...</p>');
    $.get('/vendor/products', function (data) {
      $('#productMgmtStallName').text(data.stall_name || '');
      if (!data.has_stall) {
        $('#productMgmtList').html('<p class="loading-text">請先建立攤位</p>');
        return;
      }
      renderProductMgmtList(data.products);
    });
  }

  function renderProductMgmtList(products) {
    if (products.length === 0) {
      $('#productMgmtList').html('<p class="loading-text">尚無商品，請新增</p>');
      return;
    }
    const $list = $('<div class="product-mgmt-list">');
    products.forEach(function (p) {
      $list.append(`
        <div class="product-mgmt-item">
          <div><span class="p-name">${p.name}</span></div>
          <div style="display:flex;align-items:center;gap:12px">
            <span class="p-price">$${p.price}</span>
            <button class="btn-delete" data-id="${p.product_id}">刪除</button>
          </div>
        </div>`);
    });
    $('#productMgmtList').html($list);
  }

  $('#addProductBtn').on('click', function () {
    const name  = $('#newProductName').val().trim();
    const price = $('#newProductPrice').val();
    $('#productError').text('');
    if (!name)  { $('#productError').text('請填寫商品名稱'); return; }
    if (!price) { $('#productError').text('請填寫價格'); return; }

    $('#addProductBtn').text('新增中...').prop('disabled', true);
    $.ajax({
      url: '/vendor/products', method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ name, price: parseFloat(price) }),
      success: function (data) {
        if (data.success) {
          showToast('商品已新增！');
          $('#newProductName').val('');
          $('#newProductPrice').val('');
          loadVendorProducts();
        } else {
          $('#productError').text(data.message || '新增失敗');
        }
        $('#addProductBtn').text('新增').prop('disabled', false);
      },
      error: function () {
        $('#productError').text('網路錯誤');
        $('#addProductBtn').text('新增').prop('disabled', false);
      }
    });
  });

  $(document).on('click', '.btn-delete', function () {
    const id = $(this).data('id');
    if (!confirm('確定刪除此商品？')) return;
    $.ajax({
      url: '/vendor/products/' + id, method: 'DELETE',
      success: function (data) {
        if (data.success) { showToast('商品已刪除', 'info'); loadVendorProducts(); }
        else showToast(data.message, 'error');
      }
    });
  });

  // ╔═ 【新增】攤主「管理商品」panel 按鈕綁定 class ═╗
  $('.panel-card').each(function () {
    if ($(this).find('h3').text().includes('管理商品')) {
      $(this).find('.btn-outline').addClass('open-product-mgmt');
    }
  });

  /* ══ Filter Tabs ═════════════════════════════════════════════ */

  $('.filter-tabs').on('click', '.tab', function () {
    $('.filter-tabs .tab').removeClass('active');
    $(this).addClass('active');
  });

  /* ══ ESC 鍵關閉 Modal ════════════════════════════════════════ */

  $(document).on('keydown', function (e) {
    if (e.key === 'Escape') {
      // ╔═ 【新增】補上所有 Modal 的 ESC 關閉 ═╗
      ['#loginModal','#stallModal','#visitorLoginModal',
       '#stallProductModal','#myOrdersModal','#vendorOrdersModal','#productMgmtModal'
      ].forEach(closeModal);
    }
  });

});

/* ══════════════════════════════════════════════════════════════
   攤位列表：熱門 / 少人 / 全部（頁面載入時執行，保留原有邏輯）
   ══════════════════════════════════════════════════════════════ */

const ZONE_EMOJI = {
  food: '🍜', drink: '🧋', craft: '🎨', other: '🏪', '': '🏪'
};

function queueClass(n) {
  if (n <= 5)  return 'green';
  if (n <= 15) return 'yellow';
  return 'red';
}
function queueDot(n) {
  if (n <= 5)  return '🟢';
  if (n <= 15) return '🟡';
  return '🔴';
}

function buildScrollCard(stall) {
  const cls   = queueClass(stall.queue_count);
  const dot   = queueDot(stall.queue_count);
  const emoji = ZONE_EMOJI[stall.zone_type] || '🏪';
  // ╔═ 【修正】加入「查看商品」按鈕，讓 .open-stall-btn 事件能正確觸發 ═╗
  return $(`
    <div class="scroll-card" data-stall-id="${stall.stall_id}">
      <div class="stall-img">${emoji}</div>
      <div class="stall-name">${stall.stall_name}</div>
      <div class="stall-zone">${stall.zone_type || '一般區'}</div>
      <div class="queue-badge ${cls}">${dot} ${stall.queue_count} 人・約 ${stall.wait_minutes} 分</div>
      <button class="btn btn-sm open-stall-btn" style="margin-top:6px">查看商品</button>
    </div>
  `);
}

function buildGridCard(stall) {
  const cls   = queueClass(stall.queue_count);
  const dot   = queueDot(stall.queue_count);
  const emoji = ZONE_EMOJI[stall.zone_type] || '🏪';
  return $(`
    <div class="stall-card" data-stall-id="${stall.stall_id}" data-zone="${stall.zone_type || 'other'}">
      <div class="stall-img">${emoji}</div>
      <div class="stall-info">
        <h3>${stall.stall_name}</h3>
        <p class="zone">${stall.zone_type || '一般區'}</p>
        <div class="queue-badge ${cls}">${dot} ${stall.queue_count} 人排隊・約 ${stall.wait_minutes} 分鐘</div>
      </div>
      <button class="btn btn-sm open-stall-btn">查看商品</button>
    </div>
  `);
}

function loadStallSections() {
  if (!$('#hotStallTrack').length) return;

  $.get('/stalls', function (data) {
    const stalls = data.stalls || [];

    const hot = stalls.filter(s => s.queue_count > 5).slice(0, 10);
    if (hot.length === 0) {
      $('#hotStallTrack').html('<p class="scroll-loading">目前沒有熱門攤位</p>');
    } else {
      $('#hotStallTrack').empty();
      hot.forEach(s => $('#hotStallTrack').append(buildScrollCard(s)));
    }

    const few = stalls.filter(s => s.queue_count <= 5)
                      .sort((a, b) => a.queue_count - b.queue_count)
                      .slice(0, 10);
    if (few.length === 0) {
      $('#fewStallTrack').html('<p class="scroll-loading">目前沒有資料</p>');
    } else {
      $('#fewStallTrack').empty();
      few.forEach(s => $('#fewStallTrack').append(buildScrollCard(s)));
    }

    renderAllStalls(stalls, 'all');
    $('#allStallGrid').data('stalls', stalls);

  }).fail(function () {
    ['#hotStallTrack', '#fewStallTrack'].forEach(id =>
      $(id).html('<p class="scroll-loading">載入失敗，請重新整理</p>')
    );
    $('#allStallGrid').html('<p class="stall-empty">載入失敗，請重新整理</p>');
  });
}

function renderAllStalls(stalls, filter) {
  const filtered = filter === 'all'
    ? stalls
    : stalls.filter(s => (s.zone_type || 'other') === filter);

  if (filtered.length === 0) {
    $('#allStallGrid').html('<p class="stall-empty">此分類目前沒有攤位</p>');
    return;
  }
  $('#allStallGrid').empty();
  filtered.forEach(s => $('#allStallGrid').append(buildGridCard(s)));
}

$(document).on('click', '.filter-tabs .tab', function () {
  $('.filter-tabs .tab').removeClass('active');
  $(this).addClass('active');
  const filter = $(this).data('filter') || 'all';
  const stalls = $('#allStallGrid').data('stalls') || [];
  renderAllStalls(stalls, filter);
});

// ╔═ 【新增】左右箭頭滑動 ═╗
function bindArrows(trackId, leftId, rightId) {
  const STEP = 220;
  $(leftId).on('click',  () => $(trackId).animate({ scrollLeft: '-=' + STEP }, 200));
  $(rightId).on('click', () => $(trackId).animate({ scrollLeft: '+=' + STEP }, 200));
}
bindArrows('#hotStallTrack', '#hotArrowLeft',  '#hotArrowRight');
bindArrows('#fewStallTrack', '#fewArrowLeft',  '#fewArrowRight');

loadStallSections();

/* ══ 查看地圖按鈕 ════════════════════════════════════════════ */
function scrollToMap() {
  const $map = $('#mapSection');
  if ($map.length) {
    // 🎯 這裡也同步改成 - 120 喔！
    $('html, body').animate({ scrollTop: $map.offset().top - 50 }, 500);
  }
  $('#sidebar').removeClass('show');
  $("#overlaySideber").hide(); // 順手把剛剛說的 overlay 蟲修正好
}
/* ══ Hero 市集資訊卡 ════════════════════════════════════════ */
(function initMarketCard() {

  let countdownInterval = null;

  function updateCountdown(targetDateStr) {
    if (countdownInterval) clearInterval(countdownInterval);

    function tick() {
      const diff = new Date(targetDateStr) - new Date();
      if (diff <= 0) {
        $('#countdownRow').html('<span style="color:var(--green);font-size:0.9rem">🎉 市集開始了！</span>');
        clearInterval(countdownInterval);
        return;
      }
      const d = Math.floor(diff / 86400000);
      const h = Math.floor((diff % 86400000) / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      $('#cdDays').text(String(d).padStart(2,'0'));
      $('#cdHours').text(String(h).padStart(2,'0'));
      $('#cdMins').text(String(m).padStart(2,'0'));
    }
    tick();
    countdownInterval = setInterval(tick, 30000);
  }

  $.get('/market/info', function(data) {

    // ── 活躍市集狀態 ──
    if (data.active_event) {
      const e = data.active_event;
      $('#marketStatusLabel').text('市集進行中：' + e.event_name);
      $('#marketStatusTime').text(e.start_date + ' ～ ' + e.end_date);
      $('.status-dot').removeClass('inactive').addClass('active');
      // 有市集就隱藏倒數區塊
      $('.market-next').hide();
    } else {
      $('#marketStatusLabel').text('目前無市集');
      $('#marketStatusTime').text('');
      $('.status-dot').removeClass('active').addClass('inactive');

      // ── 下一場市集倒數 ──
      if (data.next_event) {
        const n = data.next_event;
        const d = n.start_date; // 'YYYY-MM-DD'
        const formatted = d.replace(/-/g, ' / ');
        // 加上星期幾
        const weekDay = ['日','一','二','三','四','五','六'][new Date(d).getDay()];
        $('#nextMarketDate').text(formatted + '（' + weekDay + '）');
        updateCountdown(d + 'T00:00:00');
        $('.market-next').show();
      } else {
        $('.market-next').hide();
      }
    }

    // ── 統計數字 ──
    const s = data.stats;
    $('#statStalls').text(s.stall_count);
    $('#statQueue').text(s.total_queue);
    $('#statOrders').text(s.today_orders);

  }).fail(function() {
    $('#marketStatusLabel').text('資料載入失敗');
    $('.status-dot').removeClass('active').addClass('inactive');
  });

  // ── 熱門攤位 mini list（沿用 /stalls）──
  $.get('/stalls', function(data) {
    const stalls = data.stalls || [];
    const top3   = stalls.slice(0, 3); // 已按 queue_count 降序排列

    if (top3.length === 0) {
      $('#miniStallList').html('<p style="font-size:0.8rem;color:var(--text-muted)">目前無攤位資料</p>');
      return;
    }
    $('#miniStallList').empty();
    top3.forEach(function(s, i) {
      const cls = s.queue_count <= 5 ? 'green' : s.queue_count <= 15 ? 'yellow' : 'red';
      const dot = s.queue_count <= 5 ? '🟢' : s.queue_count <= 15 ? '🟡' : '🔴';
      $('#miniStallList').append(`
        <div class="mini-stall-row">
          <span class="mini-stall-name">${i+1}. ${s.stall_name}</span>
          <span class="mini-stall-queue queue-badge ${cls}">${dot} ${s.queue_count} 人</span>
        </div>
      `);
    });
  }).fail(function() {
    $('#miniStallList').html('<p style="font-size:0.8rem;color:var(--text-muted)">資料載入失敗</p>');
  });

})();
/* ══ Event 管理 Modal ═══════════════════════════════════════ */
$('#eventMgmtBtn').on('click', function () {
  openModal('#eventMgmtModal');
  loadEvents();
});

$('#closeEventMgmt').on('click', () => closeModal('#eventMgmtModal'));
$('#eventMgmtModal').on('click', function (e) {
  if ($(e.target).is('#eventMgmtModal')) closeModal('#eventMgmtModal');
});

function loadEvents() {
  $('#eventMgmtList').html('<p class="loading-text">載入中...</p>');
  const today = new Date().toISOString().slice(0, 10);

  $.get('/admin/events', function (data) {
    if (data.events.length === 0) {
      $('#eventMgmtList').html('<p class="loading-text">尚無活動，請新增</p>');
      return;
    }
    const $list = $('<div class="event-mgmt-list">');
    data.events.forEach(function (e) {
      let tag, cls;
      if (e.start_date <= today && today <= e.end_date) {
        tag = '進行中'; cls = 'active is-active';
      } else if (e.start_date > today) {
        tag = '即將開始'; cls = 'next is-next';
      } else {
        tag = '已結束'; cls = 'past';
      }

      $list.append(`
        <div class="event-mgmt-item ${cls}" data-event-id="${e.event_id}">
          <span class="event-name-badge">${e.event_name}</span>
          <span class="event-date-range">${e.start_date} ～ ${e.end_date}</span>
          <span class="event-tag ${cls.split(' ')[0]}">${tag}</span>
          <button class="btn-delete event-delete-btn" data-id="${e.event_id}">刪除</button>
        </div>
      `);
    });
    $('#eventMgmtList').html($list);
  }).fail(function () {
    $('#eventMgmtList').html('<p class="loading-text">載入失敗</p>');
  });
}

$('#addEventBtn').on('click', function () {
  const name  = $('#newEventName').val().trim();
  const start = $('#newEventStart').val();
  const end   = $('#newEventEnd').val();
  $('#eventError').text('');

  if (!name)  { $('#eventError').text('請填寫活動名稱'); return; }
  if (!start) { $('#eventError').text('請選擇開始日期'); return; }
  if (!end)   { $('#eventError').text('請選擇結束日期'); return; }

  $('#addEventBtn').text('新增中...').prop('disabled', true);
  $.ajax({
    url: '/admin/events', method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ event_name: name, start_date: start, end_date: end }),
    success: function (data) {
      if (data.success) {
        showToast('活動已新增！');
        $('#newEventName, #newEventStart, #newEventEnd').val('');
        loadEvents();
      } else {
        $('#eventError').text(data.message);
      }
      $('#addEventBtn').text('＋ 新增活動').prop('disabled', false);
    },
    error: function () {
      $('#eventError').text('網路錯誤，請稍後再試');
      $('#addEventBtn').text('＋ 新增活動').prop('disabled', false);
    }
  });
});

$(document).on('click', '.event-delete-btn', function () {
  if (!confirm('確定刪除此活動？')) return;
  const id = $(this).data('id');
  $.ajax({
    url: '/admin/events/' + id, method: 'DELETE',
    success: function (data) {
      if (data.success) { showToast('活動已刪除', 'info'); loadEvents(); }
      else showToast('刪除失敗', 'error');
    }
  });
});

/* ══ 🎯 【全新追加】管理/刪除攤位核心邏輯 ═════════════════════════ */

  // 1. 頁面載入時，動態檢查攤主是否有攤位，並切換按鈕
  function checkVendorStallStatus() {
    // 借用你們既有的這個 API 來判斷攤主狀態
    $.get('/vendor/products', function (data) {
      if (data.has_stall) {
        // 如果已經有攤位了，立刻將「建立」魔改成「管理」
        $('#stallCardTitle').text('管理攤位');
        $('#stallCardDesc').text('修改攤位基本資訊，或進行結束營業刪除。');
        $('#stallCardActionBtnContainer').html(
          '<button class="btn btn-primary btn-full" id="openManageStallBtn">管理攤位</button>'
        );
      }
    });
  }
  // 如果畫面上有攤主面板，就啟動檢查
  if ($('.vendor-panel').length) checkVendorStallStatus();

// 2. 控制「管理攤位」Modal 的開關（🎯 補齊開啟、✕ 按鈕、與遮罩關閉邏輯）
  $(document).on('click', '#openManageStallBtn', function () {
    openModal('#manageStallModal');
  });
  
  // 📢 【全新補上】點擊 ✕ 按鈕時，要乖乖關閉管理視窗
  $(document).on('click', '#closeManageStall', function () {
    closeModal('#manageStallModal');
  });

  // 📢 【全新補上】點擊視窗外的半透明遮罩時，也要自動關閉
  $(document).on('click', '#manageStallModal', function (e) {
    if ($(e.target).is('#manageStallModal')) closeModal('#manageStallModal');
  });

  // 3. 🚨 核心功能：刪除攤位（含二次高強度提醒防誤觸）
  $(document).on('click', '#deleteStallBtn', function () {
    // 第一次提醒
    if (confirm('⚠️ 警告：確定要刪除您的攤位嗎？此動作將會清除所有攤位資訊！')) {
      // 第二次終極提醒
      if (confirm('🛑 這是最後確認！刪除後連同您的「商品資料」也將一併消失，真的要刪除嗎？')) {
        
        // 兩關都通過了，正式發射 DELETE 請求給後端
        $.ajax({
          url: '/vendor/stall',
          method: 'DELETE',
          success: function (data) {
            if (data.success) {
              // 1. 關閉管理視窗
              closeModal('#manageStallModal'); // 請對齊你原本關彈窗的 id
              
              // 2. 跳出成功通知（如果你們有寫 Toast 的話，沒有的話可以刪掉這行）
              if (typeof showToast === "function") {
                showToast('攤位已成功刪除！', 'info');
              } else {
                alert('攤位已成功刪除！');
              }
              
              // 🎯 3. 關鍵大絕招：延遲半秒後，強制全網頁重新整理！
              // 網頁一刷新，就會重新呼叫 checkVendorStallStatus() ➔ 發現沒攤位 ➔ 按鈕一秒變回「建立攤位」
              setTimeout(function() {
                window.location.reload(true); // true 代表強制跟伺服器抓最新資料，不吃瀏覽器快取
              }, 500);

            } else {
              alert(data.message || '刪除失敗，請稍後再試');
            }
          },
          error: function (xhr, status, error) {
            console.error("🚨 刪除請求失敗:", error);
            alert("伺服器發生錯誤，請檢查主控台");
          }
        });

      }
    }
  });

  // 4. 別忘了順手把新 Modal 加進 ESC 鍵關閉清單裡
  $(document).on('keydown', function (e) {
    if (e.key === 'Escape') closeModal('#manageStallModal');
  });

