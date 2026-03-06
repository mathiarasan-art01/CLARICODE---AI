/**
 * script.js
 * Handles:
 *   - analyzeCode()  → POST /analyze/ → renders CONCEPT/EXPLANATION/ERROR/FIX in #codeResponse
 *   - sendChat()     → POST /chat/    → renders reply in #chatResponse
 *   - handleChat()   → Enter key support
 *   - fileUpload     → reads file into #codeInput
 */

// ─── Analyze Code ─────────────────────────────────────────────────────────────
async function analyzeCode() {
  const codeInput  = document.getElementById("codeInput");
  const responseBox = document.getElementById("codeResponse");
  const code = (codeInput?.value || "").trim();

  if (!code) {
    responseBox.innerHTML = '<span style="color:#ffcc00">⚠️ Please paste some code first.</span>';
    return;
  }

  responseBox.innerHTML = '<span class="loading-pulse">🤖 Analyzing your code...</span>';

  try {
    const res  = await fetch("/analyze/", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ code }),
    });
    const data = await res.json();

    if (data.error && data.message) {
      responseBox.innerHTML = `<span style="color:#ff6666">❌ ${escHtml(data.message)}</span>`;
      return;
    }

    responseBox.innerHTML = buildAnalysisPanel(data);

  } catch (err) {
    responseBox.innerHTML = '<span style="color:#ff6666">❌ Failed to connect to the server.</span>';
  }
}

// ─── Build structured analysis panel ─────────────────────────────────────────
function buildAnalysisPanel(d) {
  let html = '<div class="analysis-panel">';

  // ── CONCEPT ──────────────────────────────────────────────────────────────
  if (d.concept) {
    html += section("📘", "#4fc3f7", "Concept", textBody(d.concept));
  }

  // ── EXPLANATION ──────────────────────────────────────────────────────────
  if (d.explanation) {
    html += section("📋", "#81c784", "Explanation", textBody(d.explanation));
  }

  // ── ERROR FOUND (only if has_error is true) ───────────────────────────────
  if (d.has_error) {
    let errorBody = "";

    if (d.error_type) {
      errorBody += `<div class="analysis-badge badge-error">${escHtml(d.error_type)}</div>`;
    }

    if (d.error_line_number && d.error_line_number > 0) {
      errorBody += `
        <div class="error-line-block">
          <span class="error-line-label">📍 Line ${escHtml(String(d.error_line_number))}:</span>
          <code class="error-line-code">${escHtml(d.error_line || "")}</code>
        </div>`;
    }

    if (d.error_description) {
      errorBody += `<div class="analysis-text">${escHtml(d.error_description).replace(/\n/g,"<br>")}</div>`;
    }

    if (d.hint) {
      errorBody += `<div class="hint-box">💡 <strong>Hint:</strong> ${escHtml(d.hint)}</div>`;
    }

    html += section("🔴", "#ef5350", "Error Found", errorBody);

    // ── FIXED CODE ──────────────────────────────────────────────────────────
    if (d.fix_code && d.fix_code !== "Code is correct.") {
      html += section("🔧", "#ffb74d", "Fixed Code",
        `<pre class="analysis-code-block">${escHtml(d.fix_code)}</pre>`
      );
    }

    // ── FIX EXPLANATION ─────────────────────────────────────────────────────
    if (d.fix_explanation && d.fix_explanation !== "No fix needed.") {
      html += section("💡", "#ce93d8", "Fix Explanation", textBody(d.fix_explanation));
    }

  } else {
    // ── NO ERROR — show success badge ────────────────────────────────────────
    let successBody = `<div class="analysis-badge badge-success">✅ No Errors Found</div>`;
    if (d.what_you_did_right) {
      successBody += `<div class="analysis-text" style="color:#a5d6a7;margin-top:8px">${escHtml(d.what_you_did_right)}</div>`;
    }
    html += section("✅", "#66bb6a", "Code Status", successBody);
  }

  html += "</div>";
  return html;
}

function section(icon, color, title, bodyHtml) {
  return `
    <div class="analysis-section">
      <div class="analysis-section-header" style="border-left:4px solid ${color};color:${color}">
        ${icon} ${title}
      </div>
      <div class="analysis-section-body">${bodyHtml}</div>
    </div>`;
}

function textBody(text) {
  return `<div class="analysis-text">${escHtml(text).replace(/\n/g,"<br>")}</div>`;
}

// ─── Ask AI / Chat ────────────────────────────────────────────────────────────
async function sendChat() {
  const input    = document.getElementById("chatInput");
  const chatBox  = document.getElementById("chatResponse");
  const message  = (input?.value || "").trim();

  if (!message) return;

  chatBox.innerHTML = '<span class="loading-pulse">💬 Thinking...</span>';

  try {
    const res  = await fetch("/chat/", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ message }),
    });
    const data = await res.json();
    chatBox.innerHTML = escHtml(data.reply || "No response.").replace(/\n/g, "<br>");
  } catch (err) {
    chatBox.innerHTML = '<span style="color:#ff6666">❌ Chat failed. Please try again.</span>';
  }
}

function handleChat(event) {
  if (event.key === "Enter") sendChat();
}

// ─── File Upload ──────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("fileUpload");
  if (!fileInput) return;

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const codeInput = document.getElementById("codeInput");
      if (codeInput) codeInput.value = e.target.result;
    };
    reader.readAsText(file);
  });
});

// ─── HTML escape helper ───────────────────────────────────────────────────────
function escHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
}