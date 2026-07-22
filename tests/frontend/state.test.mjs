import assert from "node:assert/strict";
import test from "node:test";

import {
  defaultConfiguration,
  parseConfiguration,
  serializeConfiguration,
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
