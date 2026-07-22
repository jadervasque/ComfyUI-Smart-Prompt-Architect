const SCHEMA_VERSION = "1.0";
const PROFILE_VERSION = "1.0.0";
const PROFILES = ["portrait", "virtual-model", "dataset"];
const MODES = ["strict", "balanced", "creative", "dataset", "sequential"];
const FIELD_MODES = ["inherit", "random", "fixed", "disabled"];

export function defaultConfiguration(profile = "portrait") {
  return {
    schema_version: SCHEMA_VERSION,
    profile_id: PROFILES.includes(profile) ? profile : "portrait",
    profile_version: PROFILE_VERSION,
    mode: "balanced",
    master_seed: 0,
    batch_index: 0,
    groups: { identity: { locked: true } },
    fields: {},
    overrides: {
      positive_prefix: "",
      positive_suffix: "",
      negative_prefix: "",
      negative_suffix: "",
    },
  };
}

export function parseConfiguration(value, fallbackProfile = "portrait") {
  let parsed;
  try {
    parsed = value && value.trim() ? JSON.parse(value) : {};
  } catch (error) {
    throw new Error(`Invalid configuration JSON: ${error.message}`);
  }
  if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
    throw new Error("Configuration JSON must be an object.");
  }
  const base = defaultConfiguration(fallbackProfile);
  const profile = parsed.profile_id ?? base.profile_id;
  const mode = parsed.mode ?? base.mode;
  const seed = parsed.master_seed ?? base.master_seed;
  const batchIndex = parsed.batch_index ?? base.batch_index;
  if (!PROFILES.includes(profile)) throw new Error(`Unknown profile: ${profile}`);
  if (!MODES.includes(mode)) throw new Error(`Unknown generation mode: ${mode}`);
  if (!Number.isSafeInteger(seed) || seed < 0) throw new Error("Seed must be a non-negative safe integer.");
  if (!Number.isSafeInteger(batchIndex) || batchIndex < 0) throw new Error("Batch index must be a non-negative safe integer.");

  const groups = objectValue(parsed.groups, "groups");
  const fields = objectValue(parsed.fields, "fields");
  const overrides = objectValue(parsed.overrides, "overrides");
  const identity = objectValue(groups.identity, "groups.identity");
  return {
    ...base,
    ...parsed,
    schema_version: SCHEMA_VERSION,
    profile_id: profile,
    profile_version: parsed.profile_version ?? PROFILE_VERSION,
    mode,
    master_seed: seed,
    batch_index: batchIndex,
    groups: { ...groups, identity: { ...identity, locked: identity.locked ?? true } },
    fields,
    overrides: { ...base.overrides, ...overrides },
  };
}

export function serializeConfiguration(configuration) {
  const validated = parseConfiguration(JSON.stringify(configuration), configuration.profile_id);
  return JSON.stringify(sortDeep(validated));
}

export function updateConfiguration(configuration, values) {
  return parseConfiguration(JSON.stringify({
    ...configuration,
    profile_id: values.profile,
    mode: values.mode,
    master_seed: values.seed,
    batch_index: values.batchIndex,
    groups: {
      ...configuration.groups,
      identity: {
        ...configuration.groups.identity,
        locked: values.identityLock,
      },
    },
    overrides: {
      ...configuration.overrides,
      positive_prefix: values.positivePrefix,
      positive_suffix: values.positiveSuffix,
      negative_prefix: values.negativePrefix,
      negative_suffix: values.negativeSuffix,
    },
  }), values.profile);
}

export function setFieldConfiguration(configuration, fieldId, values) {
  if (!fieldId || typeof fieldId !== "string") throw new Error("Field ID is required.");
  if (!FIELD_MODES.includes(values.mode)) throw new Error(`Unknown field mode: ${values.mode}`);
  const field = {
    mode: values.mode,
    include_tags: normalizeTags(values.includeTags),
    exclude_tags: normalizeTags(values.excludeTags),
  };
  if (values.mode === "fixed") {
    if (!values.value) throw new Error(`${fieldId}: fixed mode requires a value.`);
    field.value = values.value;
  }
  return parseConfiguration(JSON.stringify({
    ...configuration,
    fields: { ...configuration.fields, [fieldId]: field },
  }), configuration.profile_id);
}

export function setGroupConfiguration(configuration, groupId, values) {
  if (!groupId || typeof groupId !== "string") throw new Error("Group ID is required.");
  const seed = values.seed === "" || values.seed === null ? undefined : Number(values.seed);
  if (seed !== undefined && (!Number.isSafeInteger(seed) || seed < 0)) {
    throw new Error(`${groupId}: group seed must be a non-negative safe integer.`);
  }
  const group = { locked: Boolean(values.locked) };
  if (seed !== undefined) group.seed = seed;
  return parseConfiguration(JSON.stringify({
    ...configuration,
    groups: { ...configuration.groups, [groupId]: group },
  }), configuration.profile_id);
}

export function normalizeTags(value) {
  const items = Array.isArray(value) ? value : String(value ?? "").split(",");
  return [...new Set(items.map((item) => String(item).trim().toLowerCase()).filter(Boolean))].sort();
}

function objectValue(value, path) {
  if (value === undefined) return {};
  if (!value || Array.isArray(value) || typeof value !== "object") {
    throw new Error(`${path} must be an object.`);
  }
  return value;
}

function sortDeep(value) {
  if (Array.isArray(value)) return value.map(sortDeep);
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortDeep(value[key])]));
}

export const promptArchitectProfiles = Object.freeze([...PROFILES]);
export const promptArchitectModes = Object.freeze([...MODES]);
export const promptArchitectFieldModes = Object.freeze([...FIELD_MODES]);
