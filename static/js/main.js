// PRAVAAH - Main JS

document.addEventListener('DOMContentLoaded', function () {

  // Sidebar Toggle
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarClose = document.getElementById('sidebarClose');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  function openSidebar() {
    if (sidebar) sidebar.classList.add('open');
    if (sidebarOverlay) sidebarOverlay.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    if (sidebarOverlay) sidebarOverlay.classList.remove('show');
    document.body.style.overflow = '';
  }

  if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
  if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
  if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

  // Live Clock
  const timeEl = document.getElementById('navbarTime');
  if (timeEl) {
    function updateTime() {
      const now = new Date();
      timeEl.textContent = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    }
    updateTime();
    setInterval(updateTime, 1000);
  }

  // Auto-dismiss alerts
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });

  // Photo preview on upload
  const photoInput = document.getElementById('id_photo');
  if (photoInput) {
    photoInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          let preview = document.getElementById('photoPreview');
          if (!preview) {
            preview = document.createElement('img');
            preview.id = 'photoPreview';
            preview.style.cssText = 'width:80px;height:80px;border-radius:50%;object-fit:cover;margin-top:8px;border:3px solid #4361ee;';
            photoInput.parentNode.insertBefore(preview, photoInput.nextSibling);
          }
          preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Add active class to nav items
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.landing-nav .nav-link');
  navLinks.forEach(link => {
    if (link.getAttribute('href') && link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

});
