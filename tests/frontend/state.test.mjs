import assert from "node:assert/strict";
import test from "node:test";

import {
  defaultConfiguration,
  normalizeTags,
  parseConfiguration,
  serializeConfiguration,
  setFieldConfiguration,
  setGroupConfiguration,
  updateConfiguration,
} from "../../prompt_architect/web/prompt_architect_state.js";

test("configuration round-trips deterministically", () => {
  const original = defaultConfiguration("portrait");
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
