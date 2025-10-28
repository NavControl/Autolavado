document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-input');
  const usersTbody = document.getElementById('users-tbody');
  const noResultsRow = document.getElementById('no-results-row');
  const tableCount = document.getElementById('table-count');
  const originalCount = parseInt(tableCount.dataset.total);

  function filterUsers() {
    const term = searchInput.value.toLowerCase().trim();
    const rows = usersTbody.querySelectorAll('tr');
    let visible = 0;

    if (noResultsRow) noResultsRow.style.display = 'none';

    if (term === '') {
      rows.forEach(row => {
        if (row.id !== 'no-results-row') row.style.display = '';
        visible++;
      });
      tableCount.textContent = originalCount + ' usuarios registrados';
      return;
    }

    rows.forEach(row => {
      if (row.id === 'no-results-row') return;
      const text = row.textContent.toLowerCase();
      if (text.includes(term)) {
        row.style.display = '';
        visible++;
      } else {
        row.style.display = 'none';
      }
    });

    if (visible === 0 && noResultsRow) noResultsRow.style.display = '';
    tableCount.textContent = visible + ' usuarios encontrados';
  }

  searchInput.addEventListener('input', filterUsers);

  window.eliminar_usuario = async id_usuario => {
    if (!confirm('¿Seguro que deseas eliminar este usuario?')) return;
    try {
      const res = await fetch('/users/eliminar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_usuario })
      });
      const data = await res.json();
      if (res.ok && data.message) {
        alert('✅ ' + data.message);
        document.querySelector(`button[onclick="eliminar_usuario('${id_usuario}')"]`)
          ?.closest('tr')
          ?.remove();
        filterUsers();
      } else {
        alert('⚠️ Error: ' + (data.error || data.message));
      }
    } catch (err) {
      console.error('Error:', err);
      alert('❌ No se pudo eliminar el usuario.');
    }
  };
});
