/**
 * compiler.js — W3Schools-style output + structured AI (CONCEPT/EXPLANATION/ERROR/FIX)
 */

let _pendingLanguage = "";

document.addEventListener("DOMContentLoaded", () => {
  loadLanguages();
  ensureCompilerAiBox();
});

// ── AI box injected below #compilerOutput ─────────────────────────────────────
function ensureCompilerAiBox() {
  if (document.getElementById("compilerAiResponse")) return;
  const outputBox = document.getElementById("compilerOutput");
  if (!outputBox || !outputBox.parentNode) return;

  const box = document.createElement("div");
  box.id = "compilerAiResponse";
  box.style.cssText = "display:none;margin-top:14px;";

  outputBox.parentNode.insertBefore(box, outputBox.nextSibling);
}

function showCompilerAi(html) {
  const box = document.getElementById("compilerAiResponse");
  if (!box) return;
  box.innerHTML    = html;
  box.style.display = "block";
}

function clearCompilerAi() {
  const box = document.getElementById("compilerAiResponse");
  if (box) { box.innerHTML = ""; box.style.display = "none"; }
}

// ── Languages ─────────────────────────────────────────────────────────────────
async function loadLanguages() {
  try {
    const res  = await fetch("/compiler/languages");
    const data = await res.json();
    populateLanguageDropdowns(
      data.compiler_languages   || [],
      data.conversion_languages || []
    );
  } catch (err) { console.error("Language load failed:", err); }
}

function populateLanguageDropdowns(compilerLangs, conversionLangs) {
  _populateSelect("languageSelect",  compilerLangs);
  _populateSelect("convertFromLang", conversionLangs);
  _populateSelect("convertToLang",   conversionLangs, 1);
}

function _populateSelect(id, items, defaultIndex = 0) {
  const el = document.getElementById(id);
  if (!el || !items.length) return;
  el.innerHTML = "";
  items.forEach(lang => {
    const opt = document.createElement("option");
    opt.value = lang.value; opt.textContent = lang.label;
    el.appendChild(opt);
  });
  if (el.options.length > defaultIndex) el.selectedIndex = defaultIndex;
}

// ── Run entry point ───────────────────────────────────────────────────────────
function runCompiler() {
  const code1    = (document.getElementById("compilerCode")?.value  || "").trim();
  const code2    = (document.getElementById("compilerCode2")?.value || "").trim();
  const language = document.getElementById("languageSelect")?.value || "python";

  if (!code1 && !code2) {
    showW3Output(null, null, "⚠️ Please write or paste some code first.", false);
    return;
  }
  if (code1 && code2) { _pendingLanguage = language; openModal(); return; }

  const code    = code1 || code2;
  const slotNum = code1 ? 1 : 2;
  _highlightSlot(slotNum);
  _execute(code, language, slotNum);
}

// ── Modal ─────────────────────────────────────────────────────────────────────
function openModal() {
  const m = document.getElementById("codeChoiceModal");
  if (m) m.style.display = "flex";
}
function closeModal() {
  const m = document.getElementById("codeChoiceModal");
  if (m) m.style.display = "none";
}
function executeChoice(slotNum) {
  closeModal();
  const id   = slotNum === 1 ? "compilerCode" : "compilerCode2";
  const code = (document.getElementById(id)?.value || "").trim();
  if (!code) { showW3Output(null, null, `⚠️ Code ${slotNum} is empty.`, false); return; }
  _highlightSlot(slotNum);
  _execute(code, _pendingLanguage, slotNum);
}
document.addEventListener("click", e => {
  const m = document.getElementById("codeChoiceModal");
  if (m && e.target === m) closeModal();
});

// ── Core execution ────────────────────────────────────────────────────────────
async function _execute(code, language, slotNum) {
  // Show W3-style loading panel
  showW3Output(slotNum, null, null, null, true);
  clearCompilerAi();

  try {
    const res  = await fetch("/compiler/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language, stdin: "" }),
    });
    const data = await res.json();

    const isSuccess = data.is_accepted === true;
    showW3Output(slotNum, data, null, isSuccess, false);

    if (data.ai_analysis && data.ai_analysis.trim()) {
      showCompilerAi(buildAiPanel(data.ai_analysis, isSuccess));
    } else if (isSuccess) {
      showCompilerAi(buildAiPanel(
        "CONCEPT:\nCode ran successfully.\n\nEXPLANATION:\n1. Your code executed without any errors.\n\nOUTPUT MEANING:\nThe output above is what your program produced.\n\nNEXT STEPS:\nTry modifying the code and run it again to experiment!",
        true
      ));
    }
  } catch (err) {
    showW3Output(null, null, "❌ Could not connect to compiler service.", false);
  }
}

// ── W3Schools-style output panel ──────────────────────────────────────────────
function showW3Output(slotNum, data, message, isSuccess, loading = false) {
  const outputBox = document.getElementById("compilerOutput");
  if (!outputBox) return;

  if (loading) {
    outputBox.innerHTML = `
      <div class="w3-output-panel">
        <div class="w3-output-header w3-loading-header">
          <span class="w3-header-dot"></span>
          <span class="w3-header-dot"></span>
          <span class="w3-header-dot"></span>
          <span class="w3-header-title">Running Code ${slotNum || ""}...</span>
        </div>
        <div class="w3-output-body w3-output-loading">
          <span class="loading-pulse">⏳ Executing your code...</span>
        </div>
      </div>`;
    return;
  }

  if (message && data === null) {
    outputBox.innerHTML = `
      <div class="w3-output-panel">
        <div class="w3-output-header w3-error-header">
          <span class="w3-header-dot"></span><span class="w3-header-dot"></span><span class="w3-header-dot"></span>
          <span class="w3-header-title">Message</span>
        </div>
        <div class="w3-output-body"><span style="color:#ffcc00">${escapeHtml(message)}</span></div>
      </div>`;
    return;
  }

  const stdout    = (data.stdout    || "").trim();
  const stderr    = (data.stderr    || "").trim();
  const exception = (data.exception || "").trim();
  const compOut   = (data.compile_output || "").trim();
  const timeInfo  = data.time   ? ` ⏱ ${data.time}ms` : "";
  const memInfo   = data.memory ? ` 💾 ${data.memory}KB` : "";

  const headerClass = isSuccess ? "w3-success-header" : "w3-error-header";
  const statusText  = isSuccess
    ? `✅ Code ${slotNum} — Success${timeInfo}${memInfo}`
    : `❌ Code ${slotNum} — ${escapeHtml(data.status || "Error")}${timeInfo}`;

  let bodyHtml = "";

  if (stdout) {
    bodyHtml += `<div class="w3-output-label">Output</div><pre class="w3-output-pre w3-output-stdout">${escapeHtml(stdout)}</pre>`;
  }
  if (compOut) {
    bodyHtml += `<div class="w3-output-label w3-label-error">Compilation Error</div><pre class="w3-output-pre w3-output-error">${escapeHtml(compOut)}</pre>`;
  }
  if (exception) {
    bodyHtml += `<div class="w3-output-label w3-label-error">Exception</div><pre class="w3-output-pre w3-output-error">${escapeHtml(exception)}</pre>`;
  }
  if (stderr) {
    bodyHtml += `<div class="w3-output-label w3-label-warn">Stderr</div><pre class="w3-output-pre w3-output-warn">${escapeHtml(stderr)}</pre>`;
  }
  if (!stdout && !compOut && !exception && !stderr) {
    if (isSuccess) {
      bodyHtml = `<span class="w3-no-output">Program ran with no console output.</span>`;
    } else {
      bodyHtml = `<span class="w3-no-output w3-no-output-err">Execution failed with no output. See AI Analysis below.</span>`;
    }
  }

  outputBox.innerHTML = `
    <div class="w3-output-panel">
      <div class="w3-output-header ${headerClass}">
        <span class="w3-header-dot"></span><span class="w3-header-dot"></span><span class="w3-header-dot"></span>
        <span class="w3-header-title">${statusText}</span>
      </div>
      <div class="w3-output-body">${bodyHtml}</div>
    </div>`;
}

// ── Structured AI panel (CONCEPT / EXPLANATION / ERROR / FIX) ─────────────────
function buildAiPanel(text, isSuccess) {
  if (!text) return "";

  // Parse sections
  const sections = {
    "CONCEPT":               { icon: "📘", color: "#4fc3f7",  label: "Concept"              },
    "EXPLANATION":           { icon: "📋", color: "#81c784",  label: "Explanation"           },
    "ERROR FOUND":           { icon: "🔴", color: "#ef5350",  label: "Error Found"           },
    "FIXED CODE":            { icon: "🔧", color: "#ffb74d",  label: "Fixed Code"            },
    "FIXED CODE EXPLANATION":{ icon: "💡", color: "#ce93d8",  label: "Fixed Code Explanation"},
    "OUTPUT MEANING":        { icon: "📤", color: "#80cbc4",  label: "Output Meaning"        },
    "NEXT STEPS":            { icon: "🚀", color: "#fff176",  label: "Next Steps"            },
  };

  // Split text into sections
  const allKeys   = Object.keys(sections);
  const keyPattern = new RegExp(`(${allKeys.map(k => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")}):`, "g");

  let parts = [];
  let lastIndex = 0;
  let lastKey   = null;
  let match;

  const regex = new RegExp(`(${allKeys.map(k => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")}):`, "g");

  while ((match = regex.exec(text)) !== null) {
    if (lastKey !== null) {
      parts.push({ key: lastKey, content: text.slice(lastIndex, match.index).trim() });
    }
    lastKey   = match[1];
    lastIndex = match.index + match[0].length;
  }
  if (lastKey !== null) {
    parts.push({ key: lastKey, content: text.slice(lastIndex).trim() });
  }

  // If no sections found, show raw
  if (parts.length === 0) {
    const color = isSuccess ? "#81c784" : "#ef9a9a";
    return `<div class="ai-panel"><div class="ai-section-body" style="color:${color}">${escapeHtml(text).replace(/\n/g,"<br>")}</div></div>`;
  }

  const headerBg    = isSuccess ? "linear-gradient(to right,#1b5e20,#0d47a1)" : "linear-gradient(to right,#b71c1c,#4a148c)";
  const headerTitle = isSuccess ? "💡 AI Feedback — Code Analysis" : "🔍 AI Error Analysis";

  let html = `<div class="ai-panel">`;
  html    += `<div class="ai-panel-header" style="background:${headerBg}">${headerTitle}</div>`;

  for (const part of parts) {
    const meta    = sections[part.key] || { icon:"📌", color:"#aaa", label: part.key };
    const isCode  = part.key === "FIXED CODE";
    const content = isCode
      ? `<pre class="ai-code-block">${escapeHtml(part.content)}</pre>`
      : `<div class="ai-section-body">${escapeHtml(part.content).replace(/\n/g,"<br>")}</div>`;

    html += `
      <div class="ai-section">
        <div class="ai-section-header" style="border-left:4px solid ${meta.color}; color:${meta.color}">
          ${meta.icon} ${meta.label}
        </div>
        ${content}
      </div>`;
  }

  html += `</div>`;
  return html;
}

// ── Convert Code ──────────────────────────────────────────────────────────────
async function convertCode() {
  const codeEl   = document.getElementById("compilerCode");
  const fromLang = document.getElementById("convertFromLang")?.value;
  const toLang   = document.getElementById("convertToLang")?.value;
  const code     = codeEl ? codeEl.value.trim() : "";

  if (!code) { showW3Output(null, null, "⚠️ Write code in Code 1 before converting.", false); return; }
  if (fromLang === toLang) { showW3Output(null, null, "⚠️ Select two different languages.", false); return; }

  showW3Output(null, null, "🔄 Converting code with AI...", false);
  clearCompilerAi();
  codeEl.disabled = true;

  try {
    const res  = await fetch("/compiler/convert", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, from_lang: fromLang, to_lang: toLang }),
    });
    const data = await res.json();

    if (data.error) {
      showW3Output(null, null, `❌ Conversion failed: ${data.message}`, false);
      codeEl.disabled = false;
      return;
    }

    codeEl.value    = data.converted_code || "";
    codeEl.disabled = false;

    const langSelect = document.getElementById("languageSelect");
    if (langSelect) {
      for (let opt of langSelect.options) {
        if (opt.value === toLang) { langSelect.value = toLang; break; }
      }
    }
    const fromSelect = document.getElementById("convertFromLang");
    if (fromSelect) fromSelect.value = toLang;

    const outputBox = document.getElementById("compilerOutput");
    if (outputBox) {
      outputBox.innerHTML = `
        <div class="w3-output-panel">
          <div class="w3-output-header w3-success-header">
            <span class="w3-header-dot"></span><span class="w3-header-dot"></span><span class="w3-header-dot"></span>
            <span class="w3-header-title">✅ Converted ${escapeHtml(fromLang)} → ${escapeHtml(toLang)} — placed in Code 1</span>
          </div>
          ${data.notes ? `<div class="w3-output-body"><div class="w3-output-label">Notes</div><div style="color:#ccddff;font-size:13px">${escapeHtml(data.notes)}</div></div>` : ""}
        </div>`;
    }
  } catch (err) {
    codeEl.disabled = false;
    showW3Output(null, null, "❌ Conversion service failed. Try again.", false);
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function _highlightSlot(slotNum) {
  const id = slotNum === 1 ? "compilerCode" : "compilerCode2";
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.add("slot-active");
  setTimeout(() => el.classList.remove("slot-active"), 2000);
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
}