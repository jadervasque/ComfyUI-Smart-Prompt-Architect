import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";
import {
  defaultConfiguration,
  parseConfiguration,
  promptArchitectFieldModes,
  promptArchitectModes,
  promptArchitectProfiles,
  serializeConfiguration,
  setFieldConfiguration,
  setGroupConfiguration,
  synchronizeIdentityLock,
  updateConfiguration,
} from "./prompt_architect_state.js";

const NODE_ID = "PromptArchitect_PromptArchitect";
const STYLE_ID = "prompt-architect-styles";

const escapeHtml = (value) => String(value).replace(/[&<>"]/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;",
})[character]);

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

function optionsMarkup(options, selected, label = (value) => value) {
  return options.map((value) => `<option value="${escapeHtml(value)}"${value === selected ? " selected" : ""}>${escapeHtml(label(value))}</option>`).join("");
}

async function fetchData(path, options) {
  const response = await api.fetchApi(path, options);
  const payload = await response.json();
  if (!response.ok || !payload.ok) throw new Error(payload.error?.message ?? `Request failed (${response.status})`);
  return payload.data;
}

function readBasics(state, form) {
  return updateConfiguration(state, {
    profile: form.elements.profile.value,
    mode: form.elements.mode.value,
    seed: Number(form.elements.seed.value),
    batchIndex: Number(form.elements.batchIndex.value),
    identityLock: form.elements.identityLock.checked,
    positivePrefix: form.elements.positivePrefix.value,
    positiveSuffix: form.elements.positiveSuffix.value,
    negativePrefix: form.elements.negativePrefix.value,
    negativeSuffix: form.elements.negativeSuffix.value,
  });
}

function applyNodeState(node, configuration) {
  const overrides = configuration.overrides;
  setWidget(node, "configuration_json", serializeConfiguration(configuration));
  setWidget(node, "profile", configuration.profile_id);
  setWidget(node, "generation_mode", configuration.mode);
  setWidget(node, "seed", configuration.master_seed);
  setWidget(node, "batch_index", configuration.batch_index);
  setWidget(node, "identity_lock", configuration.groups.identity?.locked ?? false);
  for (const name of ["positive_prefix", "positive_suffix", "negative_prefix", "negative_suffix"]) setWidget(node, name, overrides[name] ?? "");
  markDirty(node);
}

function fieldMarkup(section, configured) {
  const mode = configured?.mode ?? "inherit";
  const value = configured?.value ?? section.default ?? section.options[0]?.id ?? "";
  const customText = mode === "custom" ? configured?.value ?? "" : "";
  return `<article class="pa-field" data-field-id="${escapeHtml(section.id)}">
    <div><strong>${escapeHtml(section.id)}</strong><small>${escapeHtml(section.group)} · ${section.required ? "required" : "optional"}</small></div>
    <label>Mode<select data-field-mode>${optionsMarkup(promptArchitectFieldModes, mode)}</select></label>
    <label data-fixed-control${mode === "fixed" ? "" : " hidden"}>Value<select data-field-value${mode === "fixed" ? "" : " disabled"}>${optionsMarkup(section.options.map((option) => option.id), value, (id) => section.options.find((option) => option.id === id)?.text ?? id)}</select></label>
    <label data-custom-control${mode === "custom" ? "" : " hidden"}>Custom text<textarea data-field-custom rows="2" maxlength="4096" placeholder="Describe exactly what this field should add to the prompt"${mode === "custom" ? "" : " disabled"}>${escapeHtml(customText)}</textarea></label>
    <label>Include tags<input data-include-tags value="${escapeHtml((configured?.include_tags ?? []).join(", "))}" placeholder="portrait, studio"></label>
    <label>Exclude tags<input data-exclude-tags value="${escapeHtml((configured?.exclude_tags ?? []).join(", "))}" placeholder="experimental"></label>
  </article>`;
}

function syncFieldControls(card) {
  const mode = card.querySelector("[data-field-mode]").value;
  const fixedControl = card.querySelector("[data-fixed-control]");
  const customControl = card.querySelector("[data-custom-control]");
  fixedControl.hidden = mode !== "fixed";
  customControl.hidden = mode !== "custom";
  card.querySelector("[data-field-value]").disabled = mode !== "fixed";
  card.querySelector("[data-field-custom]").disabled = mode !== "custom";
}

function groupMarkup(groupId, configured) {
  return `<article class="pa-group" data-group-id="${escapeHtml(groupId)}"><div><strong>${escapeHtml(groupId)}</strong><small>Independent deterministic group</small></div><label class="pa-check"><input data-group-lock type="checkbox"${configured?.locked ? " checked" : ""}> Lock group</label><label>Explicit seed<input data-group-seed type="number" min="0" step="1" value="${configured?.seed ?? ""}" placeholder="derived automatically"></label></article>`;
}

async function openArchitect(node) {
  if (document.querySelector("[data-pa-dialog]")) return;
  const profileWidget = widget(node, "profile");
  const configWidget = widget(node, "configuration_json");
  let state;
  try {
    state = parseConfiguration(String(configWidget?.value ?? "{}"), String(profileWidget?.value ?? "portrait-core"));
    const identityLockWidget = widget(node, "identity_lock");
    if (typeof identityLockWidget?.value === "boolean") {
      state = synchronizeIdentityLock(state, identityLockWidget.value);
    }
  } catch (exception) {
    window.alert(`Prompt Architect: ${exception.message}`);
    return;
  }
  const overlay = document.createElement("div");
  overlay.className = "pa-overlay";
  overlay.dataset.paDialog = "true";
  overlay.innerHTML = `<section class="pa-dialog" role="dialog" aria-modal="true" aria-labelledby="pa-title">
    <header class="pa-header"><div><p class="pa-eyebrow">PROMPT ARCHITECT</p><h2 id="pa-title">Structured prompt editor</h2></div><button type="button" class="pa-icon" data-pa-close aria-label="Close Prompt Architect">×</button></header>
    <form data-pa-form>
      <nav class="pa-tabs" role="tablist" aria-label="Editor sections">
        <button type="button" role="tab" aria-selected="true" data-tab="basic">Basic</button><button type="button" role="tab" aria-selected="false" data-tab="fields">Fields</button><button type="button" role="tab" aria-selected="false" data-tab="groups">Groups</button><button type="button" role="tab" aria-selected="false" data-tab="preview">Preview & JSON</button>
      </nav>
      <section class="pa-pane" data-pane="basic" role="tabpanel"><div class="pa-grid">
        <label>Profile<select name="profile">${optionsMarkup(promptArchitectProfiles, state.profile_id)}</select></label>
        <label>Generation mode<select name="mode">${optionsMarkup(promptArchitectModes, state.mode)}</select></label>
        <label>Master seed<input name="seed" type="number" min="0" step="1" value="${state.master_seed}"></label>
        <label>Batch index<input name="batchIndex" type="number" min="0" step="1" value="${state.batch_index}"></label>
      </div><label class="pa-check"><input name="identityLock" type="checkbox"${state.groups.identity?.locked ? " checked" : ""}> Keep identity group locked</label><div class="pa-grid pa-overrides">
        <label>Positive prefix<textarea name="positivePrefix" rows="2"></textarea></label><label>Positive suffix<textarea name="positiveSuffix" rows="2"></textarea></label><label>Negative prefix<textarea name="negativePrefix" rows="2"></textarea></label><label>Negative suffix<textarea name="negativeSuffix" rows="2"></textarea></label>
      </div><button type="button" class="pa-secondary" data-reset>Reset selected profile</button></section>
      <section class="pa-pane" data-pane="fields" role="tabpanel" hidden><div class="pa-loading" data-fields>Loading fields…</div></section>
      <section class="pa-pane" data-pane="groups" role="tabpanel" hidden><div class="pa-loading" data-groups>Loading groups…</div></section>
      <section class="pa-pane" data-pane="preview" role="tabpanel" hidden>
        <div class="pa-actions pa-actions-top"><button type="button" class="pa-secondary" data-import>Import JSON</button><button type="button" class="pa-secondary" data-export>Export JSON</button><button type="button" class="pa-primary" data-preview>Generate preview</button></div>
        <input type="file" accept="application/json,.json" data-import-file hidden><div class="pa-preview" aria-live="polite" data-preview-output><strong>Authoritative preview</strong><span>Generate a preview without queuing the workflow.</span></div>
        <details><summary>Manifest</summary><pre data-manifest>No preview yet.</pre></details><label>Advanced JSON<textarea name="advancedJson" rows="14" spellcheck="false"></textarea></label><button type="button" class="pa-secondary" data-apply-json>Apply advanced JSON</button>
      </section>
      <p class="pa-error" role="alert" data-pa-error hidden></p><footer class="pa-actions"><button type="button" class="pa-secondary" data-pa-cancel>Cancel</button><button type="submit" class="pa-primary">Save configuration</button></footer>
    </form></section>`;
  document.body.append(overlay);
  const form = overlay.querySelector("[data-pa-form]");
  const errorBox = overlay.querySelector("[data-pa-error]");
  const showError = (error) => { errorBox.textContent = error.message ?? String(error); errorBox.hidden = false; };
  const clearError = () => { errorBox.hidden = true; errorBox.textContent = ""; };
  const close = () => overlay.remove();
  const setOverrides = () => {
    for (const key of ["positivePrefix", "positiveSuffix", "negativePrefix", "negativeSuffix"]) form.elements[key].value = state.overrides[key.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)] ?? "";
  };
  const syncJson = () => { form.elements.advancedJson.value = serializeConfiguration(state); };
  const collectSections = () => {
    state = readBasics(state, form);
    for (const card of overlay.querySelectorAll("[data-field-id]")) {
      const fieldMode = card.querySelector("[data-field-mode]").value;
      state = setFieldConfiguration(state, card.dataset.fieldId, { mode: fieldMode, value: fieldMode === "custom" ? card.querySelector("[data-field-custom]").value : card.querySelector("[data-field-value]").value, includeTags: card.querySelector("[data-include-tags]").value, excludeTags: card.querySelector("[data-exclude-tags]").value });
    }
    for (const card of overlay.querySelectorAll("[data-group-id]")) state = setGroupConfiguration(state, card.dataset.groupId, { locked: card.querySelector("[data-group-lock]").checked, seed: card.querySelector("[data-group-seed]").value });
    syncJson();
    return state;
  };
  const loadProfile = async (profileId) => {
    overlay.classList.add("pa-busy"); clearError();
    try {
      const data = await fetchData(`/prompt_architect/v1/profiles/${encodeURIComponent(profileId)}`);
      const sections = data.profile.sections;
      overlay.querySelector("[data-fields]").innerHTML = sections.map((section) => fieldMarkup(section, state.fields[section.id])).join("");
      const groups = [...new Set(sections.map((section) => section.group))].sort();
      overlay.querySelector("[data-groups]").innerHTML = groups.map((group) => groupMarkup(group, state.groups[group])).join("");
    } catch (error) { showError(error); } finally { overlay.classList.remove("pa-busy"); }
  };
  setOverrides(); syncJson(); await loadProfile(state.profile_id);
  overlay.querySelector("[data-pa-close]").addEventListener("click", close);
  overlay.querySelector("[data-pa-cancel]").addEventListener("click", close);
  overlay.addEventListener("click", (event) => { if (event.target === overlay) close(); });
  overlay.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close();
    if (event.key !== "Tab") return;
    const focusable = [...overlay.querySelectorAll('button, input, select, textarea, summary')].filter((item) => !item.disabled && item.offsetParent !== null);
    if (!focusable.length) return;
    if (event.shiftKey && document.activeElement === focusable[0]) { focusable.at(-1).focus(); event.preventDefault(); }
    else if (!event.shiftKey && document.activeElement === focusable.at(-1)) { focusable[0].focus(); event.preventDefault(); }
  });
  overlay.querySelector(".pa-tabs").addEventListener("click", (event) => {
    const tab = event.target.closest("[data-tab]"); if (!tab) return;
    for (const item of overlay.querySelectorAll("[data-tab]")) item.setAttribute("aria-selected", String(item === tab));
    for (const pane of overlay.querySelectorAll("[data-pane]")) pane.hidden = pane.dataset.pane !== tab.dataset.tab;
  });
  overlay.querySelector(".pa-tabs").addEventListener("keydown", (event) => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    const tabs = [...overlay.querySelectorAll("[data-tab]")];
    const current = tabs.indexOf(document.activeElement);
    const next = (current + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    tabs[next].focus(); tabs[next].click(); event.preventDefault();
  });
  overlay.querySelector("[data-fields]").addEventListener("change", (event) => { if (event.target.matches("[data-field-mode]")) syncFieldControls(event.target.closest("[data-field-id]")); try { collectSections(); clearError(); } catch (error) { showError(error); } });
  overlay.querySelector("[data-groups]").addEventListener("change", () => { try { collectSections(); clearError(); } catch (error) { showError(error); } });
  form.elements.identityLock.addEventListener("change", () => { const identity = overlay.querySelector('[data-group-id="identity"] [data-group-lock]'); if (identity) identity.checked = form.elements.identityLock.checked; });
  overlay.querySelector("[data-groups]").addEventListener("change", (event) => { if (event.target.matches('[data-group-id="identity"] [data-group-lock]')) form.elements.identityLock.checked = event.target.checked; });
  for (const control of form.querySelectorAll('[data-pane="basic"] input, [data-pane="basic"] select, [data-pane="basic"] textarea')) control.addEventListener("change", () => { if (control.name === "profile") return; try { state = readBasics(state, form); syncJson(); clearError(); } catch (error) { showError(error); } });
  form.elements.profile.addEventListener("change", async (event) => {
    const previous = state.profile_id;
    const hasUserValues = Object.values(state.fields).some((field) => field.mode === "fixed" || field.mode === "custom");
    if (hasUserValues && !window.confirm("Changing profile resets field overrides, including fixed and custom values. Continue?")) { event.target.value = previous; return; }
    state = defaultConfiguration(event.target.value); setOverrides(); syncJson(); await loadProfile(state.profile_id);
  });
  overlay.querySelector("[data-reset]").addEventListener("click", async () => { if (!window.confirm("Reset all settings for this profile?")) return; state = defaultConfiguration(form.elements.profile.value); form.elements.mode.value = state.mode; form.elements.seed.value = state.master_seed; form.elements.batchIndex.value = state.batch_index; form.elements.identityLock.checked = true; setOverrides(); syncJson(); await loadProfile(state.profile_id); });
  overlay.querySelector("[data-apply-json]").addEventListener("click", async () => { try { state = parseConfiguration(form.elements.advancedJson.value, form.elements.profile.value); form.elements.profile.value = state.profile_id; form.elements.mode.value = state.mode; form.elements.seed.value = state.master_seed; form.elements.batchIndex.value = state.batch_index; form.elements.identityLock.checked = state.groups.identity?.locked ?? false; setOverrides(); syncJson(); await loadProfile(state.profile_id); clearError(); } catch (error) { showError(error); } });
  overlay.querySelector("[data-preview]").addEventListener("click", async () => { const button = overlay.querySelector("[data-preview]"); button.disabled = true; overlay.classList.add("pa-busy"); clearError(); try { const configuration = collectSections(); const data = await fetchData("/prompt_architect/v1/preview", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ configuration }) }); overlay.querySelector("[data-preview-output]").innerHTML = `<strong>Positive</strong><span>${escapeHtml(data.positive_prompt)}</span><strong>Negative</strong><span>${escapeHtml(data.negative_prompt)}</span>`; overlay.querySelector("[data-manifest]").textContent = JSON.stringify(data.manifest, null, 2); } catch (error) { showError(error); } finally { button.disabled = false; overlay.classList.remove("pa-busy"); } });
  overlay.querySelector("[data-export]").addEventListener("click", () => { try { const content = serializeConfiguration(collectSections()); const link = document.createElement("a"); link.href = URL.createObjectURL(new Blob([content], { type: "application/json" })); link.download = `prompt-architect-${state.profile_id}.json`; link.click(); URL.revokeObjectURL(link.href); } catch (error) { showError(error); } });
  const fileInput = overlay.querySelector("[data-import-file]");
  overlay.querySelector("[data-import]").addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", async () => { const file = fileInput.files?.[0]; if (!file) return; try { if (file.size > 262144) throw new Error("Imported JSON exceeds the 262,144 byte limit."); state = parseConfiguration(await file.text(), form.elements.profile.value); form.elements.advancedJson.value = serializeConfiguration(state); overlay.querySelector("[data-apply-json]").click(); } catch (error) { showError(error); } finally { fileInput.value = ""; } });
  form.addEventListener("submit", (event) => { event.preventDefault(); try { applyNodeState(node, collectSections()); close(); } catch (error) { showError(error); } });
  form.elements.profile.focus();
}

function installStyles() {
  if (document.getElementById(STYLE_ID)) return;
  const link = document.createElement("link"); link.id = STYLE_ID; link.rel = "stylesheet"; link.href = new URL("./prompt_architect.css", import.meta.url).href; document.head.append(link);
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
