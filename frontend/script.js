const API = 'http://127.0.0.1:8000';

const $ = (sel) => document.querySelector(sel);
const intentsList = $('#intents-list');
const chainView = $('#chain-view');
const settlementsList = $('#settlements');
const settleBtn = $('#settle-btn');

let proposedChain = null; // store chain of IDs

async function fetchJSON(url, opts={}){
  const res = await fetch(url, Object.assign({ headers: { 'Content-Type': 'application/json' }}, opts));
  if(!res.ok){
    const msg = await res.text();
    throw new Error(msg || res.status);
  }
  return res.json();
}

async function loadIntents(){
  intentsList.innerHTML = '<div class="meta">Loading…</div>';
  const data = await fetchJSON(`${API}/intents`);
  if(!data.length){
    intentsList.innerHTML = '<div class="meta">No open intents yet. Create one above.</div>';
    return;
  }
  intentsList.innerHTML = '';
  data.forEach(row => {
    const div = document.createElement('div');
    div.className = 'item';
    div.innerHTML = `
      <div><strong>#${row.id}</strong> ${row.actor} offers <strong>${row.offer}</strong> wants <strong>${row.want}</strong></div>
      <div class="meta">${row.deadline ? 'Deadline: ' + row.deadline + ' · ' : ''}${row.is_open ? 'Open' : 'Closed'}</div>
      <div class="actions">
        <button data-solve="${row.id}">Find Match</button>
        <button data-cancel="${row.id}" style="background:#ef4444;color:#fff">Cancel</button>
      </div>
    `;
    intentsList.appendChild(div);
  });
}

async function loadSettlements(){
  const data = await fetchJSON(`${API}/settlements`);
  if(!data.length){
    settlementsList.innerHTML = '<div class="meta">No settlements yet.</div>';
    return;
  }
  settlementsList.innerHTML = '';
  data.forEach(row => {
    const div = document.createElement('div');
    div.className = 'item';
    div.innerHTML = `<div><strong>Settlement #${row.id}</strong> → Chain: [${row.chain}]</div>`;
    settlementsList.appendChild(div);
  });
}

document.addEventListener('click', async (e) => {
  const solveId = e.target.getAttribute('data-solve');
  const cancelId = e.target.getAttribute('data-cancel');
  if(solveId){
    try{
      const res = await fetchJSON(`${API}/solve/${solveId}`, { method: 'POST' });
      proposedChain = res.chain;
      renderChain(proposedChain);
      settleBtn.disabled = false;
    }catch(err){
      alert('No chain found for this intent (try adding more intents).');
    }
  }
  if(cancelId){
    if(confirm('Cancel this intent?')){
      await fetchJSON(`${API}/intents/${cancelId}`, { method:'DELETE' });
      await loadIntents();
    }
  }
});

function renderChain(chain){
  chainView.innerHTML = '';
  if(!chain || !chain.length){
    chainView.innerHTML = '<div class="meta">No proposed chain yet.</div>';
    return;
  }
  chain.forEach((id, idx) => {
    const step = document.createElement('div');
    step.className = 'step';
    step.textContent = `Step ${idx+1}: Intent #${id}`;
    chainView.appendChild(step);
  });
}

$('#intent-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    actor: $('#actor').value.trim(),
    offer: $('#offer').value.trim(),
    want: $('#want').value.trim(),
    deadline: $('#deadline').value.trim() || null
  };
  if(!payload.actor || !payload.offer || !payload.want){
    alert('Please fill all required fields.');
    return;
  }
  await fetchJSON(`${API}/intents`, { method:'POST', body: JSON.stringify(payload) });
  e.target.reset();
  await loadIntents();
});

settleBtn.addEventListener('click', async () => {
  if(!proposedChain) return;
  try{
    await fetchJSON(`${API}/settle`, { method:'POST', body: JSON.stringify({ chain: proposedChain }) });
    alert('Settlement complete!');
    proposedChain = null;
    renderChain(null);
    settleBtn.disabled = true;
    await loadIntents();
    await loadSettlements();
  }catch(err){
    alert('Settlement failed: chain may be stale. Try solving again.');
  }
});

// Initial load
loadIntents();
loadSettlements();
renderChain(null);
