const DEFAULT_SETUP_JSON = "{}";

function ensureObject(value, label) {
  if (!value || Array.isArray(value) || typeof value !== "object") {
    throw new Error(`${label} must be an object.`);
  }
  return value;
}

function createId() {
  const random = Math.random().toString(36).slice(2, 10);
  return `setup-${Date.now().toString(36)}-${random}`;
}

export function validateSetupJson(value) {
  const text = String(value ?? "").trim();
  if (!text) throw new Error("Setup JSON cannot be empty.");
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch (error) {
    throw new Error(`Invalid setup JSON: ${error.message}`);
  }
  ensureObject(parsed, "Setup JSON");
  return text;
}

function normalizeEntry(value, index) {
  const entry = ensureObject(value, `setups[${index}]`);
  const title = String(entry.title ?? "").trim();
  const description = String(entry.description ?? "").trim();
  const setupJson = validateSetupJson(entry.setup_json ?? DEFAULT_SETUP_JSON);
  return {
    id: typeof entry.id === "string" && entry.id.trim() ? entry.id : createId(),
    title,
    description,
    setup_json: setupJson,
  };
}

export function parseSetupLibrary(value) {
  const source = String(value ?? "").trim();
  if (!source) return [];
  let parsed;
  try {
    parsed = JSON.parse(source);
  } catch (error) {
    throw new Error(`Invalid setup library JSON: ${error.message}`);
  }
  if (!Array.isArray(parsed)) {
    throw new Error("Setup library JSON must be an array.");
  }
  return parsed.map((entry, index) => normalizeEntry(entry, index));
}

export function serializeSetupLibrary(entries) {
  if (!Array.isArray(entries)) {
    throw new Error("Setup library must be an array.");
  }
  return JSON.stringify(entries.map((entry, index) => normalizeEntry(entry, index)));
}

export function createSetupEntry(position = 0) {
  const index = Number.isInteger(position) && position >= 0 ? position : 0;
  return {
    id: createId(),
    title: `Setup ${index + 1}`,
    description: "",
    setup_json: DEFAULT_SETUP_JSON,
  };
}
