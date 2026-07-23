import { app } from "../../scripts/app.js";
import {
  createSetupEntry,
  parseSetupLibrary,
  serializeSetupLibrary,
} from "./setup_library_state.js";

const NODE_ID = "PromptArchitect_SetupLibrary";
const STYLE_ID = "prompt-architect-setup-library-styles";
const STORAGE_KEY = "setup_library_json";

const escapeHtml = (value) => String(value).replace(/[&<>\"]/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;",
})[character]);

function ensureProperties(node) {
  if (!node.properties || typeof node.properties !== "object") {
    node.properties = {};
  }
  if (typeof node.properties[STORAGE_KEY] !== "string") {
    node.properties[STORAGE_KEY] = "[]";
  }
}

function markDirty(node) {
  node.graph?.setDirtyCanvas?.(true, true);
  node.graph?.change?.();
}

function readSetupLibrary(node) {
  ensureProperties(node);
  return parseSetupLibrary(node.properties[STORAGE_KEY]);
}

function writeSetupLibrary(node, entries) {
  ensureProperties(node);
  node.properties[STORAGE_KEY] = serializeSetupLibrary(entries);
  markDirty(node);
}

async function copyText(value) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }
  const area = document.createElement("textarea");
  area.value = value;
  area.setAttribute("readonly", "true");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.append(area);
  area.select();
  document.execCommand("copy");
  area.remove();
}

function renderSetups(container, entries) {
  if (!entries.length) {
    container.innerHTML = '<div class="pas-empty">No setups saved yet. Select <strong>Add setup</strong> to store your first JSON configuration.</div>';
    return;
  }
  container.innerHTML = entries.map((entry, index) => `
    <article class="pas-card" data-setup-index="${index}">
      <header class="pas-card-header">
        <h3 class="pas-card-title">Setup ${index + 1}</h3>
        <div class="pas-card-actions">
          <button type="button" class="pas-button" data-action="copy">Copy setup</button>
          <button type="button" class="pas-button" data-action="remove">Delete</button>
        </div>
      </header>
      <div class="pas-grid">
        <div class="pas-field">
          <label>Name</label>
          <input class="pas-input" data-role="title" value="${escapeHtml(entry.title)}" placeholder="Portrait test setup">
        </div>
        <div class="pas-field">
          <label>Description</label>
          <input class="pas-input" data-role="description" value="${escapeHtml(entry.description)}" placeholder="What this setup is for">
        </div>
      </div>
      <div class="pas-field">
        <label>Setup JSON</label>
        <textarea class="pas-textarea" data-role="setup_json" spellcheck="false">${escapeHtml(entry.setup_json)}</textarea>
      </div>
    </article>
  `).join("");
}

async function openSetupLibrary(node, options = {}) {
  if (document.querySelector("[data-pas-dialog]")) return;
  let entries;
  let startupError = "";
  try {
    entries = readSetupLibrary(node);
  } catch (error) {
    entries = [];
    startupError = error.message ?? String(error);
  }
  if (options.addSetup || !entries.length) {
    entries.push(createSetupEntry(entries.length));
  }

  const overlay = document.createElement("div");
  overlay.className = "pas-overlay";
  overlay.dataset.pasDialog = "true";
  overlay.innerHTML = `<section class="pas-dialog" role="dialog" aria-modal="true" aria-labelledby="pas-title">
    <header class="pas-header">
      <div>
        <p class="pas-eyebrow">PROMPT ARCHITECT</p>
        <h2 id="pas-title">Setup Library</h2>
      </div>
      <button type="button" class="pas-close" data-pas-close aria-label="Close setup library">×</button>
    </header>
    <div class="pas-body">
      <div class="pas-toolbar">
        <p>Save reusable setup JSON directly in this workflow. No external editor needed.</p>
        <button type="button" class="pas-button pas-button-primary" data-action="add">Add setup</button>
      </div>
      <div class="pas-list" data-pas-list></div>
      <p class="pas-error" data-pas-error hidden></p>
      <footer class="pas-footer">
        <button type="button" class="pas-button" data-action="cancel">Cancel</button>
        <button type="button" class="pas-button pas-button-primary" data-action="save">Save library</button>
      </footer>
    </div>
  </section>`;
  document.body.append(overlay);

  const list = overlay.querySelector("[data-pas-list]");
  const errorBox = overlay.querySelector("[data-pas-error]");
  let backdropPointerDown = false;

  const showError = (message) => {
    errorBox.hidden = false;
    errorBox.textContent = message;
  };
  const clearError = () => {
    errorBox.hidden = true;
    errorBox.textContent = "";
  };
  const close = () => overlay.remove();
  const refresh = () => renderSetups(list, entries);

  const syncEntry = (card) => {
    const index = Number(card.dataset.setupIndex);
    if (!Number.isInteger(index) || !entries[index]) return;
    entries[index] = {
      ...entries[index],
      title: card.querySelector('[data-role="title"]').value,
      description: card.querySelector('[data-role="description"]').value,
      setup_json: card.querySelector('[data-role="setup_json"]').value,
    };
  };

  refresh();
  if (startupError) showError(`Stored setup library is invalid: ${startupError}`);

  overlay.querySelector("[data-pas-close]").addEventListener("click", close);
  overlay.addEventListener("pointerdown", (event) => { backdropPointerDown = event.target === overlay; });
  overlay.addEventListener("click", (event) => {
    const shouldClose = event.target === overlay && backdropPointerDown;
    backdropPointerDown = false;
    if (shouldClose) close();
  });
  overlay.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close();
  });

  list.addEventListener("input", (event) => {
    const card = event.target.closest("[data-setup-index]");
    if (!card) return;
    syncEntry(card);
    clearError();
  });

  list.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const card = button.closest("[data-setup-index]");
    if (!card) return;
    syncEntry(card);
    const index = Number(card.dataset.setupIndex);
    if (!Number.isInteger(index) || !entries[index]) return;

    if (button.dataset.action === "remove") {
      entries.splice(index, 1);
      refresh();
      clearError();
      return;
    }
    if (button.dataset.action === "copy") {
      try {
        await copyText(entries[index].setup_json);
      } catch (error) {
        showError(error.message ?? String(error));
      }
    }
  });

  overlay.querySelector('[data-action="add"]').addEventListener("click", () => {
    entries.push(createSetupEntry(entries.length));
    refresh();
    clearError();
  });

  overlay.querySelector('[data-action="cancel"]').addEventListener("click", close);

  overlay.querySelector('[data-action="save"]').addEventListener("click", () => {
    try {
      const normalized = parseSetupLibrary(serializeSetupLibrary(entries));
      writeSetupLibrary(node, normalized);
      close();
    } catch (error) {
      showError(error.message ?? String(error));
    }
  });
}

function installStyles() {
  if (document.getElementById(STYLE_ID)) return;
  const link = document.createElement("link");
  link.id = STYLE_ID;
  link.rel = "stylesheet";
  link.href = new URL("./setup_library.css", import.meta.url).href;
  document.head.append(link);
}

app.registerExtension({
  name: "prompt-architect.setup-library",
  setup() {
    installStyles();
  },
  async nodeCreated(node) {
    if (node.comfyClass !== NODE_ID && node.type !== NODE_ID) return;
    ensureProperties(node);
    if (node.widgets?.some((item) => item.name === "Open Setup Library")) return;
    node.addWidget(
      "button",
      "Open Setup Library",
      null,
      () => openSetupLibrary(node),
      { serialize: false }
    );
    node.addWidget(
      "button",
      "Add Setup",
      null,
      () => openSetupLibrary(node, { addSetup: true }),
      { serialize: false }
    );
  },
});
