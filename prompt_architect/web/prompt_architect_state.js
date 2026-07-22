const SCHEMA_VERSION = "1.0";
const PROFILE_VERSION = "1.0.0";
const PROFILES = ["portrait", "virtual-model", "dataset"];
const MODES = ["strict", "balanced", "creative"];

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
