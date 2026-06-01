$(function () {

  /* ══ Tool Functions ═══════════════════════════════════════════ */

  /* ══ Tool Functions ═══════════════════════════════════════════ */

  window.showToast = function(msg, type = 'success') {
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
  };

  window.openModal = function(id) { $(id).addClass('open'); };
  window.closeModal = function(id) { $(id).removeClass('open'); };
  
  // Order Status Label Mapping
  const STATUS_LABEL = {
    placed:      'Placed',
    confirming:  'Confirming',
    making:      'Making',
    ready:       'Ready for Pickup',
    completed:   'Completed',
    cancelled:   'Cancelled'
  };
  const STATUS_COLOR = {
    placed:      '#e8a847',
    confirming:  '#4a9eff',
    making:      '#a78bfa',
    ready:       '#4caf82',
    completed:   '#9b9890',
    cancelled:   '#e85b47'
  };

  /* ══ Login Modal ═════════════════════════════════════════════ */

  // Visitor Login Button
  $('#loginBtn').on('click', function () {
    openModal('#visitorLoginModal');
    $('#vLoginAccount').trigger('focus');
  });

  // Vendor Login Button Trigger Modal
  $('#vendorLoginTrigger').on('click', function () {
    openModal('#loginModal');
    $('#inputUsername').trigger('focus');
  });

  // Close Vendor Modal 
  $('#closeModal').on('click', () => closeModal('#loginModal'));
  $('#loginModal').on('click', function (e) {
    if ($(e.target).is('#loginModal')) closeModal('#loginModal');
  });

  // Tab Switch inside Vendor Modal
  $('.vendor-tab').on('click', function () {
    $('.vendor-tab').removeClass('active');
    $(this).addClass('active');
    
    const tab = $(this).data('tab');
    if (tab === 'vdr-login') {
      $('#vendorLoginForm').show();
      $('#vendorRegisterForm').hide();
    } else {
      $('#vendorLoginForm').hide();
      $('#vendorRegisterForm').show();
    }
    $('#loginError, #vdrRegError').text('');
  });

  // Vendor Login Form Submit Button
  $('#submitLoginBtn').on('click', function() {
    submitLogin();
  });

  // Vendor Register Form Submit Button
  $('#submitVendorRegisterBtn').on('click', function() {
    submitVendorRegister();
  });

  // Handle Enter Key for Vendor Modal
  $('#loginModal').on('keydown', function (e) {
    if (e.key === 'Enter') {
      if ($('#vendorLoginForm').is(':visible')) {
        submitLogin();
      } else {
        submitVendorRegister();
      }
    }
  });

  // Vendor Register AJAX Function
  function submitVendorRegister() {
    const name     = $('#vdrRegName').val().trim();
    const account  = $('#vdrRegAccount').val().trim();
    const password = $('#vdrRegPassword').val();
    const phone    = $('#vdrRegPhone').val().trim();
    
    $('#vdrRegError').text('');

    if (!name || !account || !password || !phone) { 
      $('#vdrRegError').text('Please fill in all fields'); 
      return;
    }
    if (password.length < 4) { 
      $('#vdrRegError').text('Password must be at least 4 characters'); 
      return;
    }

    $('#submitVendorRegisterBtn').text('Registering...').prop('disabled', true);

    $.ajax({
      url: '/vendor/register',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ name, username: account, password, phone }), 
      success: function (data) {
        if (data.success) {
          closeModal('#loginModal');
          showToast('Vendor account successfully registered! Welcome to the market!');
          setTimeout(() => location.reload(), 1000);
        } else {
          $('#vdrRegError').text(data.message || 'Registration failed');
        }
        $('#submitVendorRegisterBtn').text('Register and Login').prop('disabled', false);
      },
      error: function () {
        $('#vdrRegError').text('Network error or backend route not yet established, please try again later');
        $('#submitVendorRegisterBtn').text('Register and Login').prop('disabled', false);
      }
    });
  }

  function submitLogin() {
    const username = $('#inputUsername').val().trim();
    const password = $('#inputPassword').val();
    $('#loginError').text('');

    if (!username || !password) {
      $('#loginError').text('Please enter username and password');
      return;
    }

    $('#submitLoginBtn').text('Logging in...').prop('disabled', true);

    $.ajax({
      url: '/vendor/login',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ username, password }),
      success: function (data) {
        if (data.success) {
          showToast('Welcome back, ' + data.name + '!');
          setTimeout(() => location.reload(), 800);
        } else {
          $('#loginError').text(data.message || 'Incorrect username or password');
          $('#submitLoginBtn').text('Login').prop('disabled', false);
        }
      },
      error: function () {
        $('#loginError').text('Network error, please try again later');
        $('#submitLoginBtn').text('Login').prop('disabled', false);
      }
    });
  }

  /* ══ Sidebar Click and Smooth Scroll ════════════════════════════ */
  $("#openSidebar").click(function () {
    $("#sidebar").addClass("show");
    $("#overlaySideber").show();
  });

  $("#closeSidebar, #overlaySideber").click(function () {
    $("#sidebar").removeClass("show");
    $("#overlaySideber").hide();
  });

  $(".sidebar-menu .menu-item").on('click', function (e) {
    e.preventDefault(); 
    const targetId = $(this).attr('href'); 
    const $target = $(targetId);

    if ($target.length) {
      $('html, body').animate({ scrollTop: $target.offset().top - 150 }, 500);
    }

    $("#sidebar").removeClass("show");
    $("#overlaySideber").hide();
  });

  /* ══ Logout Buttons ════════════════════════════════════════════ */
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

  /* ══ Create Stall Modal ══════════════════════════════════════════ */

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

    if (!stall_name) { $('#stallError').text('Please enter stall name'); return; }
    if (!zone_type)  { $('#stallError').text('Please select zone type'); return; }

    $('#submitStall').text('Submitting...').prop('disabled', true);

    $.ajax({
      url: '/vendor/stall',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ stall_name, zone_type }),
      success: function (data) {
        if (data.success) {
          closeModal('#stallModal');
          showToast('Stall created!');
          setTimeout(() => location.reload(), 800);
        } else {
          $('#stallError').text(data.message || 'Submission failed, please try again later');
        }
        $('#submitStall').text('Submit Application').prop('disabled', false);
      },
      error: function () {
        $('#stallError').text('Network error, please try again later');
        $('#submitStall').text('Submit Application').prop('disabled', false);
      }
    });
  });

  /* ══ Visitor Login / Register Modal ═══════════════════════════ */

  $('#visitorLoginBtn').on('click', function () {
    pendingOrder = null;
    openModal('#visitorLoginModal');
    $('#vLoginAccount').trigger('focus');
  });

  $('#closeVisitorLogin').on('click', () => closeModal('#visitorLoginModal'));
  $('#visitorLoginModal').on('click', function (e) {
    if ($(e.target).is('#visitorLoginModal')) closeModal('#visitorLoginModal');
  });

  // Tab Switch (Login / Register)
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

    if (!account || !password) { $('#vLoginError').text('Please enter username and password'); return; }

    $('#submitVisitorLogin').text('Logging in...').prop('disabled', true);

    $.ajax({
      url: '/visitor/login', method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ account, password }),
      success: function (data) {
        if (data.success) {
          closeModal('#visitorLoginModal');
          updateVisitorUI(data.account);
          showToast('Welcome back, ' + data.account + '!');
          if (pendingOrder) doPlaceOrder();
        } else {
          $('#vLoginError').text(data.message || 'Incorrect username or password');
        }
        $('#submitVisitorLogin').text('Login and Order').prop('disabled', false);
      },
      error: function () {
        $('#vLoginError').text('Network error, please try again later');
        $('#submitVisitorLogin').text('Login and Order').prop('disabled', false);
      }
    });
  }

  $('#submitVisitorRegister').on('click', submitVisitorRegister);

  function submitVisitorRegister() {
    const account  = $('#vRegAccount').val().trim();
    const password = $('#vRegPassword').val();
    $('#vRegError').text('');

    if (!account || !password) { $('#vRegError').text('Please enter username and password'); return; }
    if (password.length < 4)   { $('#vRegError').text('Password must be at least 4 characters'); return; }

    $('#submitVisitorRegister').text('Registering...').prop('disabled', true);
    $.ajax({
      url: '/visitor/register', method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ account, password }),
      success: function (data) {
        if (data.success) {
          closeModal('#visitorLoginModal');
          updateVisitorUI(data.account);
          showToast('Registration successful, welcome ' + data.account + '!');
          if (pendingOrder) doPlaceOrder();
        } else {
          $('#vRegError').text(data.message || 'Registration failed');
        }
        $('#submitVisitorRegister').text('Register and Login').prop('disabled', false);
      },
      error: function () {
        $('#vRegError').text('Network error, please try again later');
        $('#submitVisitorRegister').text('Register and Login').prop('disabled', false);
      }
    });
  }

  // Update Navbar Visitor UI
  function updateVisitorUI(account) {
    if (account) {
      $('#visitorAccount').text('👤 ' + account);
      $('#visitorInfo').show();
      $('#loginBtn').hide();
      $('#vendorLoginTrigger').hide();
      $('#visitorFab').show();
      updateFabBadge();
    } else {
      $('#visitorInfo').hide();
      $('#loginBtn').show();
      $('#vendorLoginTrigger').show();
      $('#visitorFab').hide();
    }
  }

  // Visitor Logout Layers
  $(document).on('click', '#visitorLogoutBtn', function () {
    $("#visitorLogoutPage").addClass("show");
    $("#overlayVisitorLogout").show();
  });

  $(document).on('click', '#closeVisitorLogout, #closeVisitorLogout2, #overlayVisitorLogout', function () {
    $("#visitorLogoutPage").removeClass("show");
    $("#overlayVisitorLogout").hide();
  });

  $(document).on('click', '#confirmVisitorLogout', function () {
    window.location.href = "/visitor/logout";
  });

  // Check Visitor Session on Load
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

  /* ══ Stall Products & Cart ════════════════════════════════════ */

  let cart           = {};
  let currentStallId = null;
  let pendingOrder   = null;

  $(document).on('click', '.open-stall-btn', function () {
    const stallId = $(this).data('stall-id') || $(this).closest('[data-stall-id]').data('stall-id');
    if (!stallId) return;
    openStallProducts(stallId);
  });

  function openStallProducts(stallId) {
    currentStallId = stallId;
    cart = {};
    renderCart();
    $('#productList').html('<p class="loading-text">Loading products...</p>');
    $('#orderError').text('');
    openModal('#stallProductModal');

    $.get('/stall/' + stallId + '/products', function (data) {
      $('#stallProductTitle').text(data.stall_name);
      $('#stallProductZone').text(data.zone_type || '');
      renderProducts(data.products);
    }).fail(function () {
      $('#productList').html('<p class="loading-text">Load failed, please try again later</p>');
    });
  }

  function renderProducts(products) {
    if (!products || products.length === 0) {
      $('#productList').html('<p class="loading-text">No products added to this stall yet</p>');
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
      $('#cartItems').html('<p class="cart-empty">No products selected</p>');
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

  /* ══ Submit Order ════════════════════════════════════════════ */

  $('#submitOrder').on('click', function () {
    const ids = Object.keys(cart);
    if (ids.length === 0) { $('#orderError').text('Please select products first'); return; }

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
    $('#submitOrder').text('Submitting...').prop('disabled', true);

    $.ajax({
      url: '/order/place', method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(pendingOrder),
      success: function (data) {
        if (data.success) {
          closeModal('#stallProductModal');
          closeModal('#visitorLoginModal');
          showToast('Order submitted successfully! Order number: ' + data.order_id.slice(0, 8) + '...');
          cart = {};
          pendingOrder = null;
          updateFabBadge();
        } else {
          $('#orderError').text(data.message || 'Order placement failed, please try again later');
          openModal('#stallProductModal');
        }
        $('#submitOrder').text('Confirm Order').prop('disabled', false);
      },
      error: function () {
        $('#orderError').text('Network error, please try again later');
        $('#submitOrder').text('Confirm Order').prop('disabled', false);
        openModal('#stallProductModal');
      }
    });
  }

  /* ══ Visitor Order Query ══════════════════════════════════════ */

  $('#fabOrderBtn').on('click', function () {
    openModal('#myOrdersModal');
    loadMyOrders();
  });

  $('#myOrdersBtn').on('click', function () {
    openModal('#myOrdersModal');
    loadMyOrders();
  });

  function loadMyOrders() {
    $('#myOrdersList').html('<p class="loading-text">Loading...</p>');
    $.get('/visitor/orders', function (data) {
      if (data.orders.length === 0) {
        $('#myOrdersList').html('<p class="loading-text">No orders yet</p>');
        return;
      }
      const $list = $('<div style="display:flex; flex-direction:column; gap:20px; padding:4px 2px;">');
      data.orders.forEach(function (o) {
        $list.append(buildOrderCard(o, 'visitor'));
      });
      $('#myOrdersList').html($list);
      
      const active = data.orders.filter(o => !['completed','cancelled'].includes(o.status)).length;
      if (active > 0) { $('#fabBadge').text(active).show(); }
      else            { $('#fabBadge').hide(); }
    }).fail(function () {
      $('#myOrdersList').html('<p class="loading-text">Load failed</p>');
    });
  }

  $('#closeMyOrders').on('click', () => closeModal('#myOrdersModal'));
  $('#myOrdersModal').on('click', function (e) {
    if ($(e.target).is('#myOrdersModal')) closeModal('#myOrdersModal');
  });

  function updateFabBadge() {
    $.get('/visitor/orders', function (data) {
      const active = (data.orders || []).filter(
        o => !['completed', 'cancelled'].includes(o.status)
      ).length;
      if (active > 0) { $('#fabBadge').text(active).show(); }
      else            { $('#fabBadge').hide(); }
    });
  }

  /* ══ Vendor Order Management ══════════════════════════════════ */

  $('#vendorOrdersBtn').on('click', function () {
    openModal('#vendorOrdersModal');
    loadVendorOrders();
  });

  function loadVendorOrders() {
    $('#vendorOrdersList').html('<p class="loading-text">Loading...</p>');
    $.get('/vendor/orders', function (data) {
      if (data.orders.length === 0) {
        $('#vendorOrdersList').html('<p class="loading-text">No orders yet</p>');
        return;
      }
      const $list = $('<div style="display:flex; flex-direction:column; gap:20px; padding:4px 2px;">');
      data.orders.forEach(function (o) {
        $list.append(buildOrderCard(o, 'vendor'));
      });
      $('#vendorOrdersList').html($list);
    }).fail(function () {
      $('#vendorOrdersList').html('<p class="loading-text">Load failed</p>');
    });
  }

  $('#closeVendorOrders').on('click', () => closeModal('#vendorOrdersModal'));
  $('#vendorOrdersModal').on('click', function (e) {
    if ($(e.target).is('#vendorOrdersModal')) closeModal('#vendorOrdersModal');
  });

  $(document).on('click', '.order-next-btn', function () {
    const orderId = $(this).data('order-id');
    const newStatus = $(this).data('next-status');
    const $btn = $(this);

    $btn.text('Updating...').prop('disabled', true);
    $.ajax({
      url: '/order/' + orderId + '/status',
      method: 'PATCH',
      contentType: 'application/json',
      data: JSON.stringify({ status: newStatus }),
      success: function (data) {
        if (data.success) {
          showToast('Order updated to: ' + STATUS_LABEL[data.status]);
          loadVendorOrders();
        } else {
          showToast(data.message, 'error');
          $btn.text('Update').prop('disabled', false);
        }
      },
      error: function () {
        showToast('Update failed, please try again later', 'error');
        $btn.text('Update').prop('disabled', false);
      }
    });
  });

  $(document).on('click', '.order-cancel-btn', function () {
    if (!confirm('Are you sure you want to cancel this order?')) return;
    const orderId = $(this).data('order-id');
    $.ajax({
      url: '/order/' + orderId + '/status',
      method: 'PATCH',
      contentType: 'application/json',
      data: JSON.stringify({ status: 'cancelled' }),
      success: function (data) {
        if (data.success) {
          showToast('Order cancelled', 'info');
          loadVendorOrders();
        }
      }
    });
  });

/* ══ 🎯 Added Queue Modal Logic ══════════════════════════════ */

  // Open Queue Status Modal
  $('#viewQueueBtn').on('click', function () {
    openModal('#queueModal');
    loadVendorQueue(); // 開啟時同步向後端要資料
  });

  // Close Queue Status Modal
  $('#closeQueueModal').on('click', () => closeModal('#queueModal'));
  $('#queueModal').on('click', function (e) {
    if ($(e.target).is('#queueModal')) closeModal('#queueModal');
  });

  // 抓取並渲染排隊名單
  function loadVendorQueue() {
    $('#queueList').html('<p class="loading-text">Loading queue data...</p>');
    
    $.get('/vendor/queue', function (data) {
      if (!data.success || !data.tickets || data.tickets.length === 0) {
        $('#queueList').html('<p class="loading-text">No customers waiting in line currently.</p>');
        return;
      }

      const $list = $('<div style="display:flex; flex-direction:column; gap:12px; padding:10px 0;">');
      
      data.tickets.forEach(function (t, index) {
        // 特別把第一位（正在叫號的客人）用亮色框標示出來
        const isFirst = index === 0; 
        $list.append(`
          <div class="product-item" style="${isFirst ? 'border-color: var(--accent); box-shadow: 0 0 12px rgba(232,168,71,0.2);' : ''}">
            <div style="display:flex; flex-direction:column; gap:4px;">
              <div class="product-name" style="font-size:1.1rem; color: ${isFirst ? 'var(--accent)' : 'var(--text)'};">
                Ticket #${t.ticket_number} 
                ${isFirst ? '<span class="event-tag next" style="margin-left:8px;">Now Serving</span>' : ''}
              </div>
              <div style="font-size:0.8rem; color:var(--text-muted);">Visitor: ${t.visitor_account}</div>
            </div>
            <button class="btn btn-sm btn-primary complete-ticket-btn" data-ticket="${t.ticket_number}">
              Call & Complete
            </button>
          </div>
        `);
      });
      $('#queueList').html($list);
    }).fail(function () {
      $('#queueList').html('<p class="loading-text">Failed to load queue data.</p>');
    });
  }

  // 點擊「叫號/完成」按鈕，把該位客人消化掉
  $(document).on('click', '.complete-ticket-btn', function () {
    const ticketNum = $(this).data('ticket');
    const $btn = $(this);
    
    $btn.text('Processing...').prop('disabled', true);
    
    $.ajax({
      url: '/vendor/queue/' + ticketNum,
      method: 'PATCH',
      success: function (data) {
        if (data.success) {
          showToast('Ticket #' + ticketNum + ' processed!');
          loadVendorQueue(); // 成功後自動重新抓取最新排隊名單
        } else {
          showToast(data.message || 'Failed to process ticket', 'error');
          $btn.text('Call & Complete').prop('disabled', false);
        }
      },
      error: function () {
        showToast('Network error, please try again.', 'error');
        $btn.text('Call & Complete').prop('disabled', false);
      }
    });
  });

  /* ══ Shared Order Card Builder ════════════════════════════════ */

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
        placed:     { status: 'confirming', label: '✅ Confirm Order' },
        confirming: { status: 'making',     label: '🍳 Start Making' },
        making:     { status: 'ready',      label: '🔔 Notify Pickup' },
        ready:      { status: 'completed',  label: '✔ Order Completed' }
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
          data-order-id="${o.order_id}">Cancel Order</button>`;
      }
    }

    const subInfo = viewAs === 'vendor' ? `👤 ${o.visitor_account}` : `🏪 ${o.stall_name}`;

    return $(`
      <div class="order-card" style="margin-bottom: 20px;">
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
          <span class="order-total">Total $${(o.total || total).toFixed(0)}</span>
        </div>
        ${actionHtml ? `<div class="order-actions">${actionHtml}</div>` : ''}
      </div>
    `);
  }

  /* ══ Vendor Product Management Modal ═══════════════════════════ */
  $(document).on('click', '.open-product-mgmt', function () {
    openModal('#productMgmtModal');
    loadVendorProducts();
  });

  $('#closeProductMgmt').on('click', () => closeModal('#productMgmtModal'));
  $('#productMgmtModal').on('click', function (e) {
    if ($(e.target).is('#productMgmtModal')) closeModal('#productMgmtModal');
  });

  function loadVendorProducts() {
    $('#productMgmtList').html('<p class="loading-text">Loading...</p>');
    $.get('/vendor/products', function (data) {
      $('#productMgmtStallName').text(data.stall_name || '');
      if (!data.has_stall) {
        $('#productMgmtList').html('<p class="loading-text">Please create a stall first</p>');
        return;
      }
      renderProductMgmtList(data.products);
    });
  }

  function renderProductMgmtList(products) {
    if (products.length === 0) {
      $('#productMgmtList').html('<p class="loading-text">No products, please add some</p>');
      return;
    }
    const $list = $('<div class="product-mgmt-list">');

    products.forEach(function (p) {
      $list.append(`
        <div class="product-mgmt-item" style="flex-wrap: wrap; gap: 10px;">
          <div class="p-display" style="display:flex; justify-content:space-between; width:100%; align-items:center;">
            <span class="p-name" style="font-weight:bold;">${p.name}</span>
            <div style="display:flex; align-items:center; gap:12px;">
              <span class="p-price" style="color:var(--accent);">$${p.price}</span>
              <button class="btn-edit" style="background:none; border:1px solid #ccc; padding:4px 10px; border-radius:4px; cursor:pointer;">Edit</button>
              <button class="btn-delete" data-id="${p.product_id}">Delete</button>
            </div>
          </div>
          
          <div class="p-edit" style="display:none; justify-content:space-between; width:100%; align-items:center; gap:10px;">
            <div style="display:flex; gap:10px; flex:1;">
              <input type="text" class="edit-name" value="${p.name}" style="flex:2; padding:5px; border:1px solid #ddd; border-radius:4px;">
              <input type="number" class="edit-price" value="${p.price}" min="0" style="flex:1; padding:5px; border:1px solid #ddd; border-radius:4px;">
            </div>
            <div style="display:flex; gap:8px;">
              <button class="btn-save btn-primary" data-id="${p.product_id}" style="padding:4px 10px; border:none; border-radius:4px; cursor:pointer; color:white;">Save</button>
              <button class="btn-cancel" style="background:#eee; border:none; padding:4px 10px; border-radius:4px; cursor:pointer;">Cancel</button>
            </div>
          </div>
        </div>`);
    });

    $('#productMgmtList').html($list);
  }
  // 點擊 Edit：隱藏顯示模式，展開編輯模式
  $(document).on('click', '.btn-edit', function () {
    const $item = $(this).closest('.product-mgmt-item');
    $item.find('.p-display').hide();
    $item.find('.p-edit').css('display', 'flex');
  });

  // 點擊 Cancel：放棄修改，切回顯示模式
  $(document).on('click', '.btn-cancel', function () {
    const $item = $(this).closest('.product-mgmt-item');
    $item.find('.p-edit').hide();
    $item.find('.p-display').css('display', 'flex');
  });

  // 點擊 Save：送出修改資料到後端
  $(document).on('click', '.btn-save', function () {
    const $item = $(this).closest('.product-mgmt-item');
    const id = $(this).data('id');
    const newName = $item.find('.edit-name').val().trim();
    const newPrice = $item.find('.edit-price').val();

    if (!newName || !newPrice) {
      showToast('Please enter both name and price', 'error');
      return;
    }

    $(this).text('Saving...').prop('disabled', true);

    $.ajax({
      url: '/vendor/products/' + id,
      method: 'PATCH',
      contentType: 'application/json',
      data: JSON.stringify({ name: newName, price: parseFloat(newPrice) }),
      success: function (data) {
        if (data.success) {
          showToast('Product updated successfully!');
          loadVendorProducts(); // 重新讀取列表
        } else {
          showToast(data.message || 'Update failed', 'error');
          $item.find('.btn-save').text('Save').prop('disabled', false);
        }
      },
      error: function () {
        showToast('Network error', 'error');
        $item.find('.btn-save').text('Save').prop('disabled', false);
      }
    });
  });
  $('#addProductBtn').on('click', function () {
    const name  = $('#newProductName').val().trim();
    const price = $('#newProductPrice').val();
    $('#productError').text('');
    if (!name)  { $('#productError').text('Please enter product name'); return; }
    if (!price) { $('#productError').text('Please enter price'); return; }

    $('#addProductBtn').text('Adding...').prop('disabled', true);
    $.ajax({
      url: '/vendor/products', method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ name, price: parseFloat(price) }),
      success: function (data) {
        if (data.success) {
          showToast('Product added!');
          $('#newProductName').val('');
          $('#newProductPrice').val('');
          loadVendorProducts();
        } else {
          $('#productError').text(data.message || 'Add failed');
        }
        $('#addProductBtn').text('Add').prop('disabled', false);
      },
      error: function () {
        $('#productError').text('Network error');
        $('#addProductBtn').text('Add').prop('disabled', false);
      }
    });
  });

  $(document).on('click', '.btn-delete', function () {
    if (!confirm('Are you sure you want to delete this product?')) return;
    const id = $(this).data('id');
    $.ajax({
      url: '/vendor/products/' + id, method: 'DELETE',
      success: function (data) {
        if (data.success) { showToast('Product deleted', 'info'); loadVendorProducts(); }
        else showToast(data.message, 'error');
      }
    });
  });

  $('.panel-card').each(function () {
    if ($(this).find('h3').text().includes('Manage Products')) {
      $(this).find('.btn-outline').addClass('open-product-mgmt');
    }
  });

  /* ══ Filter Tabs ═════════════════════════════════════════════ */

  $('.filter-tabs').on('click', '.tab', function () {
    $('.filter-tabs .tab').removeClass('active');
    $(this).addClass('active');
  });

  /* ══ ESC Key to Close Modals ════════════════════════════════════ */

  $(document).on('keydown', function (e) {
    if (e.key === 'Escape') {
      ['#loginModal','#stallModal','#visitorLoginModal',
       '#stallProductModal','#myOrdersModal','#vendorOrdersModal','#productMgmtModal','#manageStallModal'
      ].forEach(closeModal);
    }
  });

});

/* ══════════════════════════════════════════════════════════════
   Stall List Render Section
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
  return $(`
    <div class="scroll-card" data-stall-id="${stall.stall_id}">
      <div class="stall-img">${emoji}</div>
      <div class="stall-name">${stall.stall_name}</div>
      <div class="stall-zone">${stall.zone_type || 'General Zone'}</div>
      <div class="queue-badge ${cls}">${dot} ${stall.queue_count} people・est ${stall.wait_minutes} min</div>
      <div style="display:flex; gap:8px; margin-top:auto;">
        <button class="btn btn-sm open-stall-btn" style="flex:1;">Products</button>
        <button class="btn btn-sm btn-outline draw-ticket-btn" data-stall-id="${stall.stall_id}" style="flex:1; padding:7px 0; justify-content:center;">🎫 Ticket</button>
      </div>
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
        <p class="zone">${stall.zone_type || 'General Zone'}</p>
        <div class="queue-badge ${cls}">${dot} ${stall.queue_count} waiting・est ${stall.wait_minutes} min</div>
      </div>
      <div style="display:flex; gap:8px; margin-top:10px;">
        <button class="btn btn-sm open-stall-btn" style="flex:1;">Products</button>
        <button class="btn btn-sm btn-outline draw-ticket-btn" data-stall-id="${stall.stall_id}" style="flex:1; padding:7px 0; justify-content:center;">🎫 Ticket</button>
      </div>
    </div>
  `);
}

function loadStallSections() {
  if (!$('#hotStallTrack').length) return;

  $.get('/stalls', function (data) {
    const stalls = data.stalls || [];

    const hot = stalls.filter(s => s.queue_count > 5).slice(0, 10);
    if (hot.length === 0) {
      $('#hotStallTrack').html('<p class="scroll-loading">No popular stalls currently</p>');
    } else {
      $('#hotStallTrack').empty();
      hot.forEach(s => $('#hotStallTrack').append(buildScrollCard(s)));
    }

    const few = stalls.filter(s => s.queue_count <= 5)
                      .sort((a, b) => a.queue_count - b.queue_count)
                      .slice(0, 10);
    if (few.length === 0) {
      $('#fewStallTrack').html('<p class="scroll-loading">No data currently</p>');
    } else {
      $('#fewStallTrack').empty();
      few.forEach(s => $('#fewStallTrack').append(buildScrollCard(s)));
    }

    renderAllStalls(stalls, 'all');
    $('#allStallGrid').data('stalls', stalls);

  }).fail(function () {
    ['#hotStallTrack', '#fewStallTrack'].forEach(id =>
      $(id).html('<p class="scroll-loading">Load failed, please refresh</p>')
    );
    $('#allStallGrid').html('<p class="stall-empty">Load failed, please refresh</p>');
  });
}

function renderAllStalls(stalls, filter) {
  const filtered = filter === 'all' ? stalls : stalls.filter(s => (s.zone_type || 'other') === filter);

  if (filtered.length === 0) {
    $('#allStallGrid').html('<p class="stall-empty">No stalls in this category currently</p>');
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

// Arrow Slide Binding
function bindArrows(trackId, leftId, rightId) {
  const STEP = 220;
  $(leftId).on('click',  () => $(trackId).animate({ scrollLeft: '-=' + STEP }, 200));
  $(rightId).on('click', () => $(trackId).animate({ scrollLeft: '+=' + STEP }, 200));
}
bindArrows('#hotStallTrack', '#hotArrowLeft',  '#hotArrowRight');
bindArrows('#fewStallTrack', '#fewArrowLeft',  '#fewArrowRight');

loadStallSections();

/* ══ Map Section View Functions ════════════════════════════════ */
function scrollToMap() {
  const $map = $('#mapSection');
  if ($map.length) {
    $('html, body').animate({ scrollTop: $map.offset().top - 50 }, 500);
  }
  $('#sidebar').removeClass('show');
  $("#overlaySideber").hide();
}

$(function() { 
  $(document).on('click', '.map-marker-area', function(e) {
    e.stopPropagation(); 
    
    const title = $(this).data('title');
    const desc = $(this).data('desc');
    const $card = $('#markerInfoCard');

    $card.find('.card-title').text(title);
    $card.find('.card-text').text(desc);

    const pos = $(this).position();
    const areaWidth = $(this).outerWidth();
    const areaHeight = $(this).outerHeight();
    const cardWidth = $card.outerWidth();

    const leftPos = pos.left + (areaWidth / 2) - (cardWidth / 2);
    const topPos = pos.top + areaHeight + 15;

    $card.css({
      top: topPos + 'px',
      left: leftPos + 'px',
      zIndex: 2500
    }).stop(true, true).fadeIn(200);
  });

  $(document).on('click', '.card-close', function(e) {
    e.preventDefault();
    e.stopPropagation();
    $('#markerInfoCard').fadeOut(200);
  });

  $(document).on('click', '#markerInfoCard', function(e) {
    e.stopPropagation();
  });

  $(document).on('click', '.map-view-area', function(e) {
    if (!$(e.target).closest('.map-marker-area, #markerInfoCard').length) {
      $('#markerInfoCard').fadeOut(200);
    }
  });

  $(document).on('click', '.map-full-btn', function() {
    $('#fullMapModal').addClass('open');
  });

  $(document).on('click', '#closeFullMap', function() {
    $('#fullMapModal').removeClass('open');
    $('#markerInfoCard').fadeOut(200); 
  });
});

/* ══ Hero Market Info Card ═══════════════════════════════════ */
(function initMarketCard() {
  let countdownInterval = null;

  function updateCountdown(targetDateStr) {
    if (countdownInterval) clearInterval(countdownInterval);

    function tick() {
      const diff = new Date(targetDateStr) - new Date();
      if (diff <= 0) {
        $('#countdownRow').html('<span style="color:var(--green);font-size:0.9rem">🎉 The market has started!</span>');
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
    if (data.active_event) {
      const e = data.active_event;
      $('#marketStatusLabel').text('Market in progress: ' + e.event_name);
      $('#marketStatusTime').text(e.start_date + ' ～ ' + e.end_date);
      $('.status-dot').removeClass('inactive').addClass('active');
      $('.market-next').hide();
    } else {
      $('#marketStatusLabel').text('No active market currently');
      $('#marketStatusTime').text('');
      $('.status-dot').removeClass('active').addClass('inactive');

      if (data.next_event) {
        const n = data.next_event;
        const d = n.start_date; 
        const formatted = d.replace(/-/g, ' / ');
        const weekDay = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][new Date(d).getDay()];

        $('#nextMarketDate').text(formatted + ' (' + weekDay + ')');
        updateCountdown(d + 'T00:00:00');
        $('.market-next').show();
      } else {
        $('.market-next').hide();
      }
    }

    const s = data.stats;
    $('#statStalls').text(s.stall_count);
    $('#statQueue').text(s.total_queue);
    $('#statOrders').text(s.today_orders);

  }).fail(function() {
    $('#marketStatusLabel').text('Failed to load data');
    $('.status-dot').removeClass('active').addClass('inactive');
  });

  $.get('/stalls', function(data) {
    const stalls = data.stalls || [];
    const top3   = stalls.slice(0, 3);

    if (top3.length === 0) {
      $('#miniStallList').html('<p style="font-size:0.8rem;color:var(--text-muted)">No stall data currently</p>');
      return;
    }
    $('#miniStallList').empty();
    top3.forEach(function(s, i) {
      const cls = s.queue_count <= 5 ? 'green' : s.queue_count <= 15 ? 'yellow' : 'red';
      const dot = s.queue_count <= 5 ? '🟢' : s.queue_count <= 15 ? '🟡' : '🔴';
      $('#miniStallList').append(`
        <div class="mini-stall-row">
          <span class="mini-stall-name">${i+1}. ${s.stall_name}</span>
          <span class="mini-stall-queue queue-badge ${cls}">${dot} ${s.queue_count} people</span>
        </div>
      `);
    });
  }).fail(function() {
    $('#miniStallList').html('<p style="font-size:0.8rem;color:var(--text-muted)">Failed to load data</p>');
  });

})();

/* ══ Event Management Modal ═══════════════════════════════════ */
$('#eventMgmtBtn').on('click', function () {
  openModal('#eventMgmtModal');
  loadEvents();
});

$('#closeEventMgmt').on('click', () => closeModal('#eventMgmtModal'));
$('#eventMgmtModal').on('click', function (e) {
  if ($(e.target).is('#eventMgmtModal')) closeModal('#eventMgmtModal');
});

function loadEvents() {
  $('#eventMgmtList').html('<p class="loading-text">Loading...</p>');
  const today = new Date().toISOString().slice(0, 10);

  $.get('/admin/events', function (data) {
    if (data.events.length === 0) {
      $('#eventMgmtList').html('<p class="loading-text">No events yet, please add</p>');
      return;
    }
    const $list = $('<div class="event-mgmt-list">');
    data.events.forEach(function (e) {
      let tag, cls;
      if (e.start_date <= today && today <= e.end_date) {
        tag = 'In Progress'; cls = 'active is-active';
      } else if (e.start_date > today) {
        tag = 'Starting Soon'; cls = 'next is-next';
      } else {
        tag = 'Ended'; cls = 'past';
      }

      $list.append(`
        <div class="event-mgmt-item ${cls}" data-event-id="${e.event_id}">
          <span class="event-name-badge">${e.event_name}</span>
          <span class="event-date-range">${e.start_date} ～ ${e.end_date}</span>
          <span class="event-tag ${cls.split(' ')[0]}">${tag}</span>
          <button class="btn-delete event-delete-btn" data-id="${e.event_id}">Delete</button>
        </div>
      `);
    });
    $('#eventMgmtList').html($list);

  }).fail(function () {
    $('#eventMgmtList').html('<p class="loading-text">Load failed</p>');
  });
}

$('#addEventBtn').on('click', function () {
  const name  = $('#newEventName').val().trim();
  const start = $('#newEventStart').val();
  const end   = $('#newEventEnd').val();
  $('#eventError').text('');

  if (!name)  { $('#eventError').text('Please enter event name'); return; }
  if (!start) { $('#eventError').text('Please select start date'); return; }
  if (!end)   { $('#eventError').text('Please select end date'); return; }

  $('#addEventBtn').text('Adding...').prop('disabled', true);
  $.ajax({
    url: '/admin/events', method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ event_name: name, start_date: start, end_date: end }),
    success: function (data) {
      if (data.success) {
        showToast('Event added!');
        $('#newEventName, #newEventStart, #newEventEnd').val('');
        loadEvents();
      } else {
        $('#eventError').text(data.message);
      }
      $('#addEventBtn').text('+ Add Event').prop('disabled', false);
    },
    error: function () {
      $('#eventError').text('Network error, please try again later');
      $('#addEventBtn').text('+ Add Event').prop('disabled', false);
    }
  });
});

$(document).on('click', '.event-delete-btn', function () {
  if (!confirm('Are you sure you want to delete this event?')) return;
  const id = $(this).data('id');
  $.ajax({
    url: '/admin/events/' + id, method: 'DELETE',
    success: function (data) {
      if (data.success) { showToast('Event deleted', 'info'); loadEvents(); }
      else showToast('Delete failed', 'error');
    }
  });
});

/* ══ Manage / Delete Stall Core Logic ═════════════════════════════ */

function checkVendorStallStatus() {
  $.get('/vendor/products', function (data) {
    if (data.has_stall) {
      $('#stallCardTitle').text('Manage Stall');
      $('#stallCardDesc').text('Modify basic stall information, or close business and delete.');
      $('#stallCardActionBtnContainer').html(
        '<button class="btn btn-primary btn-full" id="openManageStallBtn">Manage Stall</button>'
      );
    }
  });
}
if ($('.vendor-panel').length) checkVendorStallStatus();

$(document).on('click', '#openManageStallBtn', function () {
  openModal('#manageStallModal');
});

$(document).on('click', '#closeManageStall', function () {
  closeModal('#manageStallModal');
});

$(document).on('click', '#manageStallModal', function (e) {
  if ($(e.target).is('#manageStallModal')) closeModal('#manageStallModal');
});

$(document).on('click', '#deleteStallBtn', function () {
  if (confirm('⚠️ WARNING: Are you sure you want to delete your stall? This action will erase all stall information!')) {
    if (confirm("🛑 FINAL CONFIRMATION! Once deleted, your 'Product Data' will also disappear. Really delete?")) {
      $.ajax({
        url: '/vendor/stall',
        method: 'DELETE',
        success: function (data) {
          if (data.success) {
            closeModal('#manageStallModal'); 
            if (typeof showToast === "function") {
              showToast('Stall successfully deleted!', 'info');
            } else {
              alert('Stall successfully deleted!');
            }
            setTimeout(function() {
              window.location.reload(true);
            }, 500);
          } else {
            alert(data.message || 'Delete failed, please try again later');
          }
        },
        error: function (xhr, status, error) {
          console.error("🚨 Delete request failed:", error);
          alert("Server error, please check console");
        }
      });
    }
  }
});

/* /* ══ Real-time Info & Ticket System ═══════════════════════════════ */

// 1. 綁定「抽號碼牌」按鈕，並檢查是否已登入
$(document).on('click', '.draw-ticket-btn', function (e) {
    e.stopPropagation(); // 防止點擊事件衝突
    const stallId = $(this).data('stall-id');
    
    $.get('/visitor/session', function (data) {
      if (data.logged_in) {
         executeDrawTicket(stallId);
      } else {
         openModal('#visitorLoginModal');
         $('#vLoginAccount').trigger('focus');
      }
    });
});

// 2. 實際發送抽號碼牌請求
function executeDrawTicket(stallId) {
    fetch('/ticket/draw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stall_id: stallId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('🎟 Ticket drawn! Your number is #' + data.ticket.ticket_number + ' (Est. wait: ' + data.ticket.expected_wait_time + ' min)');
            
            silentUpdateStalls(); // 抽完立刻刷新紅綠燈
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => console.error('Error drawing ticket:', error));
}

// 3. 更新上方統計看板
function fetchMarketInfo() {
    fetch('/market/info')
        .then(res => res.json())
        .then(data => {
            if (data.stats) {
                $('#statStalls').text(data.stats.stall_count);
                $('#statQueue').text(data.stats.total_queue);
                $('#statOrders').text(data.stats.today_orders);
            }
        })
        .catch(error => { /* 遇到網路錯誤時安靜地忽略，避免洗頻 Console */ });
}

// 4. 無痕更新攤位紅綠燈 (不會破壞 UI 與分類標籤)
function silentUpdateStalls() {
  $.get('/stalls', function (data) {
    if (!data.stalls) return;
    
    data.stalls.forEach(s => {
      const cls = s.queue_count <= 5 ? 'green' : s.queue_count <= 15 ? 'yellow' : 'red';
      const dot = s.queue_count <= 5 ? '🟢' : s.queue_count <= 15 ? '🟡' : '🔴';
      
      // 找出畫面上所有屬於這個攤位的卡片
      const $cards = $(`[data-stall-id="${s.stall_id}"]`);
      if ($cards.length > 0) {
        const $badge = $cards.find('.queue-badge');
        // 抽換顏色與文字
        $badge.removeClass('green yellow red').addClass(cls);
        $cards.each(function() {
           if ($(this).hasClass('scroll-card')) {
             $(this).find('.queue-badge').text(`${dot} ${s.queue_count} people・est ${s.wait_minutes} min`);
           } else {
             $(this).find('.queue-badge').text(`${dot} ${s.queue_count} waiting・est ${s.wait_minutes} min`);
           }
        });
      }
    });
  });
}

// 5. 啟動計時器：每 5 秒背景自動同步
document.addEventListener('DOMContentLoaded', () => {
    fetchMarketInfo();
    setInterval(fetchMarketInfo, 5000);
    setInterval(silentUpdateStalls, 5000);
});