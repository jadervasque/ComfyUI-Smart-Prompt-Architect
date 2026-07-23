import assert from "node:assert/strict";
import test from "node:test";

import {
  defaultConfiguration,
  normalizeTags,
  parseConfiguration,
  serializeConfiguration,
  setFieldConfiguration,
  setGroupConfiguration,
  synchronizeIdentityLock,
  updateConfiguration,
} from "../../prompt_architect/web/prompt_architect_state.js";

import {
  createSetupEntry,
  parseSetupLibrary as parseSetupLibraryState,
  serializeSetupLibrary as serializeSetupLibraryState,
} from "../../prompt_architect/web/setup_library_state.js";

test("configuration round-trips deterministically", () => {
  const original = defaultConfiguration("portrait-core");
  assert.deepEqual(parseConfiguration(serializeConfiguration(original)), original);
  assert.equal(serializeConfiguration(original), serializeConfiguration(original));
});

test("form state survives serialization", () => {
  const updated = updateConfiguration(defaultConfiguration(), {
    profile: "virtual-model", mode: "strict", seed: 42, batchIndex: 3,
    identityLock: false, positivePrefix: "Editorial", positiveSuffix: "sharp",
    negativePrefix: "avoid", negativeSuffix: "noise",
  });
  const restored = parseConfiguration(serializeConfiguration(updated));
  assert.equal(restored.profile_id, "virtual-model");
  assert.equal(restored.master_seed, 42);
  assert.equal(restored.groups.identity.locked, false);
  assert.equal(restored.overrides.positive_prefix, "Editorial");
});

test("visible identity lock overrides stale serialized editor state", () => {
  const stale = defaultConfiguration();
  assert.equal(stale.groups.identity.locked, true);
  const synchronized = synchronizeIdentityLock(stale, false);
  assert.equal(synchronized.groups.identity.locked, false);
  assert.equal(parseConfiguration(serializeConfiguration(synchronized)).groups.identity.locked, false);
  assert.throws(() => synchronizeIdentityLock(stale, "false"), /must be a boolean/);
});

test("invalid JSON and unsafe seeds are rejected", () => {
  assert.throws(() => parseConfiguration("{"), /Invalid configuration JSON/);
  assert.throws(() => parseConfiguration('{"master_seed":-1}'), /non-negative/);
});

test("field modes, tags, and groups serialize without manual JSON", () => {
  let state = setFieldConfiguration(defaultConfiguration(), "outfit", {
    mode: "fixed", value: "formal-suit", includeTags: " Formal, studio,formal ", excludeTags: ["experimental"],
  });
  state = setGroupConfiguration(state, "appearance", { locked: true, seed: "99" });
  const restored = parseConfiguration(serializeConfiguration(state));
  assert.deepEqual(restored.fields.outfit.include_tags, ["formal", "studio"]);
  assert.equal(restored.fields.outfit.value, "formal-suit");
  assert.deepEqual(restored.groups.appearance, { locked: true, seed: 99 });
  assert.deepEqual(normalizeTags("B, a, b"), ["a", "b"]);
});

test("fixed values and invalid group seeds are never discarded silently", () => {
  assert.throws(() => setFieldConfiguration(defaultConfiguration(), "outfit", {
    mode: "fixed", value: "", includeTags: "", excludeTags: "",
  }), /requires a value/);
  assert.throws(() => setGroupConfiguration(defaultConfiguration(), "scene", {
    locked: true, seed: "-2",
  }), /non-negative/);
});

test("custom mode stores bounded free text and upgrades the configuration schema", () => {
  const state = setFieldConfiguration(defaultConfiguration(), "outfit", {
    mode: "custom",
    value: "  a bespoke emerald coat with brass buttons  ",
    includeTags: "",
    excludeTags: "",
  });
  const restored = parseConfiguration(serializeConfiguration(state));
  assert.equal(restored.schema_version, "1.1");
  assert.equal(restored.fields.outfit.mode, "custom");
  assert.equal(restored.fields.outfit.value, "a bespoke emerald coat with brass buttons");
  assert.throws(() => setFieldConfiguration(defaultConfiguration(), "outfit", {
    mode: "custom", value: " ", includeTags: "", excludeTags: "",
  }), /requires a value/);
  assert.throws(() => setFieldConfiguration(defaultConfiguration(), "outfit", {
    mode: "custom", value: "x".repeat(4097), includeTags: "", excludeTags: "",
  }), /cannot exceed 4096/);
});

test("legacy schema cannot smuggle in custom mode", () => {
  assert.throws(() => parseConfiguration(JSON.stringify({
    schema_version: "1.0",
    fields: { outfit: { mode: "custom", value: "custom coat" } },
  })), /requires configuration schema 1.1/);
  assert.throws(() => parseConfiguration('{"schema_version":"2.0"}'), /Unknown configuration schema/);
});

test("setup library entries round-trip with deterministic normalization", () => {
  const entries = [
    {
      id: "setup-a",
      title: "  Portrait baseline  ",
      description: " Studio balanced run ",
      setup_json: '{"schema_version":"1.1","profile_id":"portrait-core"}',
    },
  ];
  const serialized = serializeSetupLibraryState(entries);
  const restored = parseSetupLibraryState(serialized);
  assert.equal(restored.length, 1);
  assert.equal(restored[0].id, "setup-a");
  assert.equal(restored[0].title, "Portrait baseline");
  assert.equal(restored[0].description, "Studio balanced run");
  assert.equal(restored[0].setup_json, '{"schema_version":"1.1","profile_id":"portrait-core"}');
});

test("setup library rejects invalid shape and invalid setup JSON", () => {
  assert.throws(() => parseSetupLibraryState('{"id":"x"}'), /must be an array/);
  assert.throws(() => serializeSetupLibraryState([{ title: "Broken", setup_json: "{" }]), /Invalid setup JSON/);
  assert.throws(() => serializeSetupLibraryState(["invalid-entry"]), /must be an object/);
});

test("setup entry factory creates valid defaults", () => {
  const entry = createSetupEntry(2);
  assert.equal(entry.title, "Setup 3");
  const restored = parseSetupLibraryState(serializeSetupLibraryState([entry]));
  assert.equal(restored[0].title, "Setup 3");
});
