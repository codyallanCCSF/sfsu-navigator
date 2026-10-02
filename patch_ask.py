import re,sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()

form = '''  <form id="askForm" class="header" style="gap:8px">
    <input id="askInput" placeholder="Ask about campus, e.g. where can I study quietly?" aria-label="Ask a question about campus" maxlength="300" style="flex:1;width:auto;font-size:14px;padding:10px">
    <button id="askBtn" type="submit">Ask</button>
  </form>

  <div class="layout">'''
assert s.count('  <div class="layout">') == 1
s = s.replace('  <div class="layout">', form, 1)

ans = '''      <p id="selectedInfo">'''
assert s.count(ans) == 1
s = s.replace('<div id="buildingDetails" class="building-details" hidden></div>',
              '<div id="askAnswer" class="stat" aria-live="polite" hidden></div>\n      <div id="buildingDetails" class="building-details" hidden></div>', 1)

js = '''
// ---- Ask Gemini: question in, highlighted building out ----
const askForm = document.getElementById('askForm');
const askInput = document.getElementById('askInput');
const askBtn = document.getElementById('askBtn');
const askAnswer = document.getElementById('askAnswer');
askForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const q = askInput.value.trim();
  if (!q) return;
  askBtn.disabled = true; askBtn.textContent = 'Asking...';
  askAnswer.hidden = false; askAnswer.textContent = 'Thinking...';
  try {
    const res = await fetch('/api/ask', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question: q})});
    const data = await res.json();
    if (!res.ok) { askAnswer.textContent = data.error || 'Something went wrong.'; return; }
    askAnswer.textContent = data.answer;
    const names = data.buildings.map(n => n.toLowerCase());
    document.querySelectorAll('.hotspot').forEach(el =>
      el.classList.toggle('dim', names.length > 0 && !names.includes(el.dataset.name)));
    const first = items.findIndex(it => it.r.name.toLowerCase() === names[0]);
    if (first >= 0) {
      selectBuilding(first, false);
      const fs = document.getElementById('floorSelect');
      if (data.floor && fs && [...fs.options].some(o => o.value == data.floor)) {
        fs.value = data.floor; fs.dispatchEvent(new Event('change'));
      }
    }
  } catch (err) {
    askAnswer.textContent = 'Could not reach the server.';
  } finally {
    askBtn.disabled = false; askBtn.textContent = 'Ask';
  }
});
'''
marker = "  renderDirectory(q);\n});\n</script>"
assert s.count(marker) == 1, "could not find end of the page script"
s = s.replace(marker, "  renderDirectory(q);\n});\n" + js + "</script>", 1)
open(p, "w", encoding="utf-8").write(s)
print("patched", p)
