import API_CONFIG from "./config.js";

// State
let calculators = {};
let currentCalculator = null;
let currentSpec = null;

// Initialize app
document.addEventListener("DOMContentLoaded", async () => {
  await loadCalculators();
  renderCalculatorList();
  updateCalculatorCount();
  // Hide output card on load (by id)
  const outputCard = document.getElementById("output-card");
  if (outputCard) outputCard.classList.add("hidden");
});

// Navigation functions
window.showHome = () => {
  document.getElementById("home-view").classList.remove("hidden");
  document.getElementById("doc-view").classList.add("hidden");
  document.getElementById("form-container").innerHTML = "";
};

window.showDocumentation = async () => {
  document.getElementById("home-view").classList.add("hidden");
  document.getElementById("doc-view").classList.remove("hidden");

  const docContent = document.getElementById("doc-content");
  docContent.innerHTML =
    '<div class="flex justify-center p-8"><span class="loading loading-spinner loading-lg text-primary"></span></div>';

  try {
    // Fetch README.md from the API or GitHub
    const response = await fetch(
      "https://raw.githubusercontent.com/rcpch/clinical-calculators/live/README.md",
    );
    if (!response.ok) throw new Error("Failed to fetch documentation");

    const markdown = await response.text();
    // Simple markdown rendering (for a full solution, consider marked.js library)
    const html = simpleMarkdownToHTML(markdown);
    docContent.innerHTML = html;
  } catch (error) {
    docContent.innerHTML =
      '<div class="alert alert-error">Failed to load documentation</div>';
    console.error(error);
  }
};

// Simple markdown to HTML converter
function simpleMarkdownToHTML(markdown) {
  return (
    markdown
      // Headers
      .replace(/^### (.*$)/gim, "<h3>$1</h3>")
      .replace(/^## (.*$)/gim, "<h2>$1</h2>")
      .replace(/^# (.*$)/gim, "<h1>$1</h1>")
      // Bold
      .replace(/\*\*(.*)\*\*/gim, "<strong>$1</strong>")
      // Italic
      .replace(/\*(.*)\*/gim, "<em>$1</em>")
      // Links
      .replace(
        /\[([^\]]+)\]\(([^\)]+)\)/gim,
        '<a href="$2" class="link link-primary" target="_blank">$1</a>',
      )
      // Code blocks
      .replace(/```([^`]+)```/gim, "<pre><code>$1</code></pre>")
      // Inline code
      .replace(/`([^`]+)`/gim, "<code>$1</code>")
      // Line breaks
      .replace(/\n\n/gim, "</p><p>")
      // Wrap in paragraph
      .replace(/^(.+)$/gim, "<p>$1</p>")
      // Lists
      .replace(/<p>- (.*?)<\/p>/gim, "<li>$1</li>")
      .replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>")
  );
}

// Update calculator count
function updateCalculatorCount() {
  const count = Object.keys(calculators).length;
  document.getElementById("calculator-count").textContent = count || "?";
}

// Strip markdown from text
function stripMarkdown(text) {
  return text
    .replace(/^#{1,6}\s+/gm, "") // Remove headers
    .replace(/\*\*(.*?)\*\*/g, "$1") // Remove bold
    .replace(/\*(.*?)\*/g, "$1") // Remove italic
    .replace(/`([^`]+)`/g, "$1") // Remove inline code
    .replace(/\[([^\]]+)\]\([^\)]+\)/g, "$1") // Remove links, keep text
    .trim();
}

// Fetch available calculators
async function loadCalculators() {
  try {
    const response = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.calculators}`,
    );
    if (!response.ok) throw new Error("Failed to fetch calculators");
    calculators = await response.json();
  } catch (error) {
    showError("Failed to load calculators. Please check the API is running.");
    console.error(error);
  }
}

// Refresh calculators from API
async function refreshCalculators() {
  const btn = document.getElementById("refresh-calculators-btn");
  if (btn) {
    btn.disabled = true;
    btn.classList.add("loading");
  }

  await loadCalculators();
  renderCalculatorList();
  updateCalculatorCount();

  if (btn) {
    btn.disabled = false;
    btn.classList.remove("loading");
  }
}

// Render calculator list
function renderCalculatorList() {
  const container = document.getElementById("calculator-list");
  if (!calculators || Object.keys(calculators).length === 0) {
    container.innerHTML =
      '<div class="alert alert-warning">No calculators available</div>';
    return;
  }

  container.innerHTML = Object.entries(calculators)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(
      ([name, title]) => `
      <div class="flex items-center justify-between p-4 hover:bg-base-200 transition-colors group">
        <div class="flex-1 min-w-0 mr-4">
          <h3 class="text-lg font-semibold text-rcpch-dark-blue mb-1 group-hover:text-rcpch-bright-blue">${stripMarkdown(
            title,
          )}</h3>
          <p class="text-sm text-gray-500 font-mono truncate">api.rcpch.ac.uk/clinical-calculators/${name}</p>
        </div>
        <div class="flex-shrink-0">
          <button class="btn btn-sm btn-primary" onclick="selectCalculator('${name}')">
            Use Calculator
          </button>
        </div>
      </div>
    `,
    )
    .join("");
}

// Select and load calculator
window.selectCalculator = async (name) => {
  currentCalculator = name;

  // Show loading
  document.getElementById("form-container").innerHTML = `
    <div class="flex justify-center p-8">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>
  `;

  try {
    // Fetch calculator spec
    const response = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.calculatorDoc(name)}`,
    );
    if (!response.ok) throw new Error("Failed to fetch calculator spec");
    const data = await response.json();
    currentSpec = data;

    // Render form
    renderCalculatorForm(name, data);
  } catch (error) {
    showError(`Failed to load calculator: ${name}`);
    console.error(error);
  }
};

// Parse inputs from docstring
function parseInputsFromDoc(docString) {
  if (!docString) return [];

  const lines = docString.split("\n");
  const inputs = [];
  let inInputsSection = false;
  let currentInput = null;

  for (const line of lines) {
    const trimmed = line.trim();

    if (trimmed === "[inputs]") {
      inInputsSection = true;
      continue;
    }

    if (inInputsSection && trimmed.startsWith("[") && trimmed.endsWith("]")) {
      break; // Next section
    }

    if (inInputsSection) {
      const nameMatch = trimmed.match(/^-\s*name:\s*(.+)$/);
      if (nameMatch) {
        if (currentInput) inputs.push(currentInput);
        currentInput = { name: nameMatch[1].trim() };
        continue;
      }

      if (currentInput) {
        const kvMatch = trimmed.match(/^([a-z_]+):\s*(.+)$/i);
        if (kvMatch) {
          const [, key, value] = kvMatch;
          currentInput[key.toLowerCase()] = parseValue(value);
        }
      }
    }
  }

  if (currentInput) inputs.push(currentInput);
  return inputs;
}

function parseValue(str) {
  const trimmed = str.trim();
  if (trimmed === "true") return true;
  if (trimmed === "false") return false;
  if (trimmed.startsWith("[") && trimmed.endsWith("]")) {
    return trimmed
      .slice(1, -1)
      .split(",")
      .map((s) => s.trim().replace(/['"]/g, ""));
  }
  if (!isNaN(trimmed) && trimmed !== "") {
    return trimmed.includes(".") ? parseFloat(trimmed) : parseInt(trimmed);
  }
  return trimmed;
}

// Render calculator form
function renderCalculatorForm(name, spec) {
  const inputs = parseInputsFromDoc(spec.doc);
  const title = calculators[name] || name;

  const formHtml = `
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <div class="flex items-center justify-between mb-4">
          <h2 class="card-title text-2xl text-rcpch-dark-blue">${title}</h2>
          <button class="btn btn-ghost btn-sm" onclick="backToList()">
            ← Back to List
          </button>
        </div>
        
        <form id="calculator-form" class="space-y-4">
          ${inputs.map((input) => renderInputField(input)).join("")}
          
          <div class="card-actions justify-end mt-6">
            <button type="submit" class="btn btn-primary btn-lg">
              Calculate
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <div id="result-container" class="hidden mt-6"></div>
  `;

  document.getElementById("form-container").innerHTML = formHtml;
  document
    .getElementById("calculator-form")
    .addEventListener("submit", handleSubmit);
  // Setup conditional validation rules (e.g. unit-dependent ranges)
  setupConditionalValidation(inputs, name);
}

// Make validation conditional on selection for inputs like HbA1c unit
function setupConditionalValidation(inputs, calculatorName) {
  // Find unit selector (first enum/select input)
  const unitInputSpec = inputs.find(
    (i) => Array.isArray(i.enum) && i.enum.length,
  );
  if (!unitInputSpec) return;

  const unitSelect = document.querySelector(
    `select[name="${unitInputSpec.name}"]`,
  );
  if (!unitSelect) return;

  // Identify numeric inputs to defer validation for until unit selected
  const numericInputs = inputs.filter((i) =>
    ["number", "float", "int"].includes((i.type || "").toLowerCase()),
  );

  // Remove static min/max attributes initially so client won't validate prematurely
  numericInputs.forEach((field) => {
    const el = document.querySelector(`input[name="${field.name}"]`);
    if (el) {
      el.removeAttribute("min");
      el.removeAttribute("max");
    }
  });

  // Parse validation rules block from docstring to find alternate ranges
  const doc = currentSpec && currentSpec.doc ? currentSpec.doc : "";
  const validationBlockMatch = doc.match(
    /##\s*📂\s*Validation Rules([\s\S]*?)(?:\n##|$)/i,
  );
  const validationBlock = validationBlockMatch ? validationBlockMatch[1] : "";

  // Helper: try to extract alternate max for a field from validation text
  function extractAlternates(field) {
    const name = field.name;
    const alternates = {};
    // Look for lines mentioning the field name or common words (height/weight/value)
    const lines = validationBlock.split(/\n/).map((l) => l.trim());
    for (const line of lines) {
      if (!line) continue;
      if (
        line.toLowerCase().includes(name.replace(/_/g, " ")) ||
        (name === "value" && /value/i.test(line)) ||
        (name === "height" && /height/i.test(line)) ||
        (name === "weight" && /weight/i.test(line))
      ) {
        // Look for patterns like "≤ 3 m (or 118 in)" or "≤ 200 for mmol/mol"
        const parenMatch = line.match(
          /≤\s*([0-9.]+)\s*[^\s\(]+\s*\(or\s*([0-9.]+)\s*([^\)]+)\)/i,
        );
        if (parenMatch) {
          alternates.primary = parseFloat(parenMatch[1]);
          alternates.secondary = parseFloat(parenMatch[2]);
          alternates.secondaryUnit = parenMatch[3].trim();
        } else {
          // Match single numeric max (e.g., "≤ 200 for mmol/mol")
          const singleMatch = line.match(/≤\s*([0-9.]+)/);
          if (singleMatch) {
            alternates.primary = parseFloat(singleMatch[1]);
            // Try to detect which unit this primary value applies to
            if (/mmol/i.test(line)) alternates.primaryUnit = "mmol_mol";
            else if (/percent|%/i.test(line)) alternates.primaryUnit = "percent";
            else if (/kg|lb|pound|lb\b/i.test(line)) alternates.primaryUnit = "weight";
            else if (/m\b|in\b|inch/i.test(line)) alternates.primaryUnit = "height";
          }
        }
      }
    }
    return alternates;
  }

  // Build a map of per-field alternates
  const fieldAlternates = {};
  numericInputs.forEach((field) => {
    fieldAlternates[field.name] = extractAlternates(field);
  });

  // Build unit mapping from input 'unit' strings where available
  const unitMap = {};
  numericInputs.forEach((field) => {
    if (
      field.unit &&
      typeof field.unit === "string" &&
      field.unit.includes("|")
    ) {
      const parts = field.unit.split("|").map((p) => p.trim());
      // map to simple tokens like 'metric'/'imperial' if possible by presence of units
      unitMap[field.name] = parts; // e.g. ["m (UCUM: m)", "in (UCUM: [in_i])"]
    }
  });

  // When unit changes, apply appropriate rules; when blank, remove ranges
  function applyForSelected() {
    const val = unitSelect.value;
    if (!val) {
      numericInputs.forEach((field) => {
        const el = document.querySelector(`input[name="${field.name}"]`);
        if (el) {
          el.removeAttribute("min");
          el.removeAttribute("max");
        }
      });
      return;
    }

    // Determine index among real options (skip empty placeholder)
    const realOptions = Array.from(unitSelect.options).filter((o) => o.value !== "");
    const selectedRealIndex = realOptions.findIndex((o) => o.value === val);

    // Apply rules heuristically: prefer explicit alternates parsed from Validation Rules.
    numericInputs.forEach((field) => {
      const el = document.querySelector(`input[name="${field.name}"]`);
      if (!el) return;
      const alternates = fieldAlternates[field.name] || {};
      if (alternates.secondary && realOptions.length >= 2) {
        if (selectedRealIndex === 0) {
          if (alternates.primary) el.setAttribute("max", String(alternates.primary));
        } else if (selectedRealIndex === 1) {
          el.setAttribute("max", String(alternates.secondary));
        }
      } else if (alternates.primary && alternates.primaryUnit) {
        // If alternates.primaryUnit matches the selected unit, apply it
        const normalizedSelected = val.replace(/\//g, "_").toLowerCase();
        if (normalizedSelected === String(alternates.primaryUnit).toLowerCase()) {
          el.setAttribute("max", String(alternates.primary));
        } else {
          if (field.min != null) el.setAttribute("min", String(field.min));
          if (field.max != null) el.setAttribute("max", String(field.max));
        }
      } else {
        // Fallback: use the min/max specified in the inputs section (if present)
        if (field.min != null) el.setAttribute("min", String(field.min));
        if (field.max != null) el.setAttribute("max", String(field.max));
      }
    });
  }

  // Apply immediately in case a unit is pre-selected
  applyForSelected();

  unitSelect.addEventListener("change", applyForSelected);
}

// Render individual input field
function renderInputField(input) {
  const {
    name,
    type,
    description,
    required,
    min,
    max,
    unit,
    enum: enumValues,
  } = input;
  const label = description || name;
  const requiredMark = required ? '<span class="text-error">*</span>' : "";
  const unitLabel = unit
    ? `<span class="text-sm text-gray-500">(${unit})</span>`
    : "";

  if (enumValues && Array.isArray(enumValues)) {
    return `
      <div class="form-control">
        <label class="label">
          <span class="label-text font-semibold">${label} ${requiredMark} ${unitLabel}</span>
        </label>
        <select name="${name}" class="select select-bordered w-full" ${
          required ? "required" : ""
        }>
          <option value="">Select ${label}</option>
          ${enumValues
            .map((val) => `<option value="${val}">${val}</option>`)
            .join("")}
        </select>
      </div>
    `;
  }

  const inputType = (type || "string").toLowerCase();
  const htmlInputType = ["number", "float", "int"].includes(inputType)
    ? "number"
    : "text";
  const stepAttr =
    inputType === "number" || inputType === "float" ? 'step="any"' : "";
  const minAttr = min != null ? `min="${min}"` : "";
  const maxAttr = max != null ? `max="${max}"` : "";

  return `
    <div class="form-control">
      <label class="label">
        <span class="label-text font-semibold">${label} ${requiredMark} ${unitLabel}</span>
      </label>
      <input 
        type="${htmlInputType}" 
        name="${name}" 
        class="input input-bordered w-full" 
        placeholder="${label}"
        ${required ? "required" : ""}
        ${stepAttr}
        ${minAttr}
        ${maxAttr}
      />
    </div>
  `;
}

// Handle form submission
async function handleSubmit(e) {
  e.preventDefault();

  const formData = new FormData(e.target);
  const params = {};

  // Parse inputs to correct types
  const inputs = parseInputsFromDoc(currentSpec.doc);
  const numericFields = new Set(
    inputs
      .filter((i) =>
        ["number", "float", "int"].includes((i.type || "").toLowerCase()),
      )
      .map((i) => i.name),
  );

  for (const [key, value] of formData.entries()) {
    params[key] = numericFields.has(key) ? parseFloat(value) : value;
  }

  // Show loading
  const submitBtn = e.target.querySelector('button[type="submit"]');
  submitBtn.classList.add("loading");
  submitBtn.disabled = true;

  try {
    const response = await fetch(
      `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.calculate}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          calculator: currentCalculator,
          params: params,
        }),
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Calculation failed");
    }

    const result = await response.json();
    displayResult(result);
  } catch (error) {
    showError(error.message);
  } finally {
    submitBtn.classList.remove("loading");
    submitBtn.disabled = false;
  }
}

// Display calculation result
function displayResult(result) {
  // Show output card, hide manual/AI entry cards
  const outputCard = document.getElementById("output-card");
  if (outputCard) outputCard.classList.remove("hidden");
  const manualPanel = document.getElementById("manual-form-panel");
  const aiPanel = document.getElementById("ai-assistant-panel");
  if (manualPanel) manualPanel.classList.add("hidden");
  if (aiPanel) aiPanel.classList.add("hidden");

  const container = document.getElementById("result-container");
  container.classList.remove("hidden");

  // Extract main result and metadata
  const { metadata, ...mainData } = result;

  container.innerHTML = `
    <div class="card bg-base-100 shadow-xl border-2 border-rcpch-strong-green">
      <div class="card-body">
        <h3 class="card-title text-rcpch-strong-green">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Result
        </h3>
        
        <div class="space-y-3">
          ${Object.entries(mainData)
            .map(([key, value]) => {
              if (key === "result" || key === "interpretation") {
                return `
                <div class="alert alert-success">
                  <div>
                    <div class="font-bold text-lg">${formatLabel(key)}</div>
                    <div class="text-xl">${formatValue(value, mainData)}</div>
                  </div>
                </div>
              `;
              }
              return `
              <div class="flex justify-between items-center p-3 bg-base-200 rounded-lg">
                <span class="font-semibold text-gray-700">${formatLabel(
                  key,
                )}:</span>
                <span class="text-gray-900">${formatValue(
                  value,
                  mainData,
                )}</span>
              </div>
            `;
            })
            .join("")}
        </div>
        
        ${
          metadata
            ? `
          <div class="divider"></div>
          <div class="text-xs text-gray-500">
            <p><strong>Calculator:</strong> ${metadata.calculator_name}</p>
            <p><strong>Version:</strong> ${metadata.version}</p>
            <p><strong>Timestamp:</strong> ${new Date(
              metadata.timestamp,
            ).toLocaleString()}</p>
          </div>
        `
            : ""
        }
      </div>
    </div>
  `;

  // Scroll to result
  container.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// Reset output and show entry cards again
window.resetOutput = function () {
  // Hide output card
  const outputCard = document.getElementById("output-card");
  if (outputCard) outputCard.classList.add("hidden");
  // Show manual/AI entry cards
  const manualPanel = document.getElementById("manual-form-panel");
  const aiPanel = document.getElementById("ai-assistant-panel");
  if (manualPanel) manualPanel.classList.remove("hidden");
  if (aiPanel) aiPanel.classList.remove("hidden");
  // Optionally clear output content
  const container = document.getElementById("result-container");
  if (container) container.innerHTML = "";
  // Optionally clear manual form fields (reset form)
  const form = document.getElementById("calculatorForm");
  if (form) form.reset();
  // Optionally clear AI chat
  const chat = document.getElementById("chatMessages");
  if (chat) chat.innerHTML = "";
};

function formatLabel(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
}

function formatValue(value, context) {
  if (typeof value === "number") {
    const unit = context.result_unit || "";
    return `${value} ${unit}`.trim();
  }
  if (typeof value === "object") {
    return `<pre class="text-xs">${JSON.stringify(value, null, 2)}</pre>`;
  }
  return value;
}

// Show error message
function showError(message) {
  const toast = document.getElementById("toast-container");
  toast.innerHTML = `
    <div class="alert alert-error shadow-lg">
      <div>
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>${message}</span>
      </div>
    </div>
  `;

  setTimeout(() => {
    toast.innerHTML = "";
  }, 5000);
}

// Back to calculator list
window.backToList = () => {
  document.getElementById("form-container").innerHTML = "";
  document
    .getElementById("calculator-list")
    .scrollIntoView({ behavior: "smooth" });
};
