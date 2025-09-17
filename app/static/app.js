const api = {
  list: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return fetch(`/api/items?${qs}`).then(r => r.json());
  },
  add: (payload) => fetch('/api/items', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)}).then(r => r.json()),
  adjust: (id, delta) => fetch(`/api/items/${id}/adjust?delta=${delta}`, { method: 'PATCH'}).then(r => r.json()),
  update: (id, payload) => fetch(`/api/items/${id}`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)}).then(r => r.json()),
  delete: (id) => fetch(`/api/items/${id}`, { method: 'DELETE'}).then(r => r.json()),
  exportCsv: () => window.location.href = '/api/export/csv'
};

const state = { items: [], q: '', low: false, order_by: 'name', order: 'asc' };

const $ = (sel) => document.querySelector(sel);
const tbody = $('#tbody');

function fmtQty(it){
  const badge = (it.quantity <= it.min_qty) ? 'low' : 'ok';
  return `<span class="qty ${badge}">${it.quantity}</span>`;
}

function render(){
  if(!state.items.length){
    tbody.innerHTML = `<tr><td colspan="6" class="muted">Sem itens. Adicione o primeiro acima 👆</td></tr>`;
    return;
  }
  tbody.innerHTML = state.items.map(it => `
    <tr>
      <td>${it.name}</td>
      <td>${it.unit}</td>
      <td>${fmtQty(it)}</td>
      <td>
        <input class="inline-input" type="number" min="0" value="${it.min_qty}" 
          onblur="onUpdateMin(${it.id}, this.value)"/>
      </td>
      <td>${it.category || '-'}</td>
      <td>
        <div class="actions-row">
          <button class="ghost" onclick="onAdjust(${it.id}, 1)">+1</button>
          <button class="ghost" onclick="onAdjust(${it.id}, -1)">-1</button>
          <button class="ghost" onclick="onAdjust(${it.id}, 10)">+10</button>
          <button class="ghost" onclick="onAdjust(${it.id}, -10)">-10</button>
          <button class="danger" onclick="onDelete(${it.id})">Excluir</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function load(){
  api.list({
    q: state.q,
    low_stock: state.low,
    order_by: state.order_by,
    order: state.order
  }).then(data => {
    state.items = data;
    render();
  }).catch(err => {
    console.error(err);
    tbody.innerHTML = `<tr><td colspan="6" class="muted">Erro ao carregar.</td></tr>`;
  });
}

function onAdjust(id, delta){ api.adjust(id, delta).then(load); }
function onDelete(id){ if(confirm('Excluir este item?')) api.delete(id).then(load); }
function onUpdateMin(id, value){ api.update(id, { min_qty: parseInt(value || 0, 10) }).then(load); }

// Form add
$('#form-add').addEventListener('submit', (e) => {
  e.preventDefault();
  const payload = {
    name: $('#name').value.trim(),
    unit: $('#unit').value.trim() || 'unid',
    quantity: parseInt($('#quantity').value || '0', 10),
    min_qty: parseInt($('#min_qty').value || '0', 10),
    category: $('#category').value.trim() || null,
  };
  api.add(payload).then(() => {
    $('#form-add').reset();
    $('#unit').value = 'unid';
    $('#quantity').value = 1;
    $('#min_qty').value = 0;
    load();
  });
});

// Toolbar
$('#btn-export').addEventListener('click', () => api.exportCsv());
$('#btn-reload').addEventListener('click', load);
$('#chk-low').addEventListener('change', (e) => { state.low = e.target.checked; load(); });
$('#search').addEventListener('input', (e) => { state.q = e.target.value; load(); });
$('#order-by').addEventListener('change', (e) => { state.order_by = e.target.value; load(); });
$('#order').addEventListener('change', (e) => { state.order = e.target.value; load(); });

// First load
load();
