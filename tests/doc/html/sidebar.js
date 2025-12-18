// Sidebar collapsible sections
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.nav-section-header').forEach(function(header) {
    header.addEventListener('click', function() {
      const section = this.parentElement;
      section.classList.toggle('collapsed');
      const sectionId = section.dataset.section;
      if (sectionId) {
        const collapsed = section.classList.contains('collapsed');
        localStorage.setItem('sidebar-' + sectionId, collapsed ? 'collapsed' : 'expanded');
      }
    });
  });

  document.querySelectorAll('.nav-section[data-section]').forEach(function(section) {
    const sectionId = section.dataset.section;
    const savedState = localStorage.getItem('sidebar-' + sectionId);
    if (savedState === 'collapsed') section.classList.add('collapsed');
  });

  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-section a').forEach(function(link) {
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('active');
      const section = link.closest('.nav-section');
      if (section) section.classList.remove('collapsed');
    }
  });
});
