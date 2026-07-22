import { app } from "../../scripts/app.js";
import {
  parseConfiguration,
  promptArchitectModes,
  promptArchitectProfiles,
  serializeConfiguration,
  updateConfiguration,
} from "./prompt_architect_state.js";

const NODE_ID = "PromptArchitect_PromptArchitect";
const STYLE_ID = "prompt-architect-styles";

function widget(node, name) {
  return node.widgets?.find((item) => item.name === name);
}

function setWidget(node, name, value) {
  const target = widget(node, name);
  if (target) target.value = value;
}

function markDirty(node) {
  node.graph?.setDirtyCanvas?.(true, true);
  node.graph?.change?.();
}

function optionMarkup(options, selected) {
  return options.map((value) => `<option value="${value}"${value === selected ? " selected" : ""}>${value}</option>`).join("");
}

function openArchitect(node) {
  if (document.querySelector("[data-pa-dialog]")) return;
  const profileWidget = widget(node, "profile");
  const configWidget = widget(node, "configuration_json");
  try {
    const configuration = parseConfiguration(String(configWidget?.value ?? "{}"), String(profileWidget?.value ?? "portrait"));
    const overrides = configuration.overrides;
    const overlay = document.createElement("div");
    overlay.className = "pa-overlay";
    overlay.dataset.paDialog = "true";
    overlay.innerHTML = `
      <section class="pa-dialog" role="dialog" aria-modal="true" aria-labelledby="pa-title">
        <header class="pa-header"><div><p class="pa-eyebrow">PROMPT ARCHITECT</p><h2 id="pa-title">Structured prompt editor</h2></div><button type="button" class="pa-icon" data-pa-close aria-label="Close Prompt Architect">×</button></header>
        <form data-pa-form>
          <div class="pa-grid">
            <label>Profile<select name="profile">${optionMarkup(promptArchitectProfiles, configuration.profile_id)}</select></label>
            <label>Generation mode<select name="mode">${optionMarkup(promptArchitectModes, configuration.mode)}</select></label>
            <label>Master seed<input name="seed" type="number" min="0" step="1" value="${configuration.master_seed}"></label>
            <label>Batch index<input name="batchIndex" type="number" min="0" step="1" value="${configuration.batch_index}"></label>
          </div>
          <label class="pa-check"><input name="identityLock" type="checkbox"${configuration.groups.identity.locked ? " checked" : ""}> Keep identity group locked</label>
          <div class="pa-grid pa-overrides">
            <label>Positive prefix<textarea name="positivePrefix" rows="2"></textarea></label>
            <label>Positive suffix<textarea name="positiveSuffix" rows="2"></textarea></label>
            <label>Negative prefix<textarea name="negativePrefix" rows="2"></textarea></label>
            <label>Negative suffix<textarea name="negativeSuffix" rows="2"></textarea></label>
          </div>
          <div class="pa-preview" aria-live="polite" data-pa-preview><strong>Preview</strong><span>Choose settings, then save them to the workflow.</span></div>
          <p class="pa-error" role="alert" data-pa-error hidden></p>
          <footer class="pa-actions"><button type="button" class="pa-secondary" data-pa-cancel>Cancel</button><button type="submit" class="pa-primary">Save configuration</button></footer>
        </form>
      </section>`;
    document.body.append(overlay);
    const form = overlay.querySelector("[data-pa-form]");
    for (const key of ["positivePrefix", "positiveSuffix", "negativePrefix", "negativeSuffix"]) {
      form.elements[key].value = overrides[key.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)] ?? "";
    }
    const close = () => overlay.remove();
    overlay.querySelector("[data-pa-close]").addEventListener("click", close);
    overlay.querySelector("[data-pa-cancel]").addEventListener("click", close);
    overlay.addEventListener("click", (event) => { if (event.target === overlay) close(); });
    overlay.addEventListener("keydown", (event) => { if (event.key === "Escape") close(); });
    form.addEventListener("input", () => {
      overlay.querySelector("[data-pa-preview] span").textContent = `${form.elements.profile.value} · ${form.elements.mode.value} · seed ${form.elements.seed.value || "0"}`;
    });
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const error = overlay.querySelector("[data-pa-error]");
      try {
        const values = {
          profile: form.elements.profile.value,
          mode: form.elements.mode.value,
          seed: Number(form.elements.seed.value),
          batchIndex: Number(form.elements.batchIndex.value),
          identityLock: form.elements.identityLock.checked,
          positivePrefix: form.elements.positivePrefix.value,
          positiveSuffix: form.elements.positiveSuffix.value,
          negativePrefix: form.elements.negativePrefix.value,
          negativeSuffix: form.elements.negativeSuffix.value,
        };
        const updated = updateConfiguration(configuration, values);
        const serialized = serializeConfiguration(updated);
        setWidget(node, "configuration_json", serialized);
        setWidget(node, "profile", values.profile);
        setWidget(node, "generation_mode", values.mode);
        setWidget(node, "seed", values.seed);
        setWidget(node, "batch_index", values.batchIndex);
        setWidget(node, "identity_lock", values.identityLock);
        setWidget(node, "positive_prefix", values.positivePrefix);
        setWidget(node, "positive_suffix", values.positiveSuffix);
        setWidget(node, "negative_prefix", values.negativePrefix);
        setWidget(node, "negative_suffix", values.negativeSuffix);
        markDirty(node);
        close();
      } catch (exception) {
        error.textContent = exception.message;
        error.hidden = false;
      }
    });
    form.elements.profile.focus();
  } catch (exception) {
    window.alert(`Prompt Architect: ${exception.message}`);
  }
}

function installStyles() {
  if (document.getElementById(STYLE_ID)) return;
  const link = document.createElement("link");
  link.id = STYLE_ID;
  link.rel = "stylesheet";
  link.href = new URL("./prompt_architect.css", import.meta.url).href;
  document.head.append(link);
}

app.registerExtension({
  name: "prompt-architect.editor",
  setup() { installStyles(); },
  async nodeCreated(node) {
    if (node.comfyClass !== NODE_ID && node.type !== NODE_ID) return;
    if (node.widgets?.some((item) => item.name === "Open Architect")) return;
    node.addWidget("button", "Open Architect", null, () => openArchitect(node), { serialize: false });
  },
});
