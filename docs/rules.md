# Compatibility rules

Rules are declarative data, not executable expressions. Conditions can inspect a resolved field's
option ID or tags, safe profile metadata, and the generation mode. Supported operators are
`equals`, `not_equals`, `in`, `not_in`, `contains_tag`, `missing`, and `present`.

- `requires` removes a candidate when its condition is false.
- `excludes` removes a candidate when its condition is true.
- `prefer` multiplies a compatible candidate's weight. Creative mode uses the square root of the
  multiplier so preference has less influence.
- `implies` fills an empty field or replaces a random value and records the change.

An implication may never silently replace a fixed user value. Such conflicts raise a
`RuleConflictError` that names both values. Transitive implications use a bounded queue and track
assignments; repeated conflicting assignments are reported as cycles. Absolute requirements and
exclusions are revalidated on the final structured context.
