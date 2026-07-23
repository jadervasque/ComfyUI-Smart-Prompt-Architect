# Frontend assets

`prompt_architect.js` registers the visual editor for the
`PromptArchitect_PromptArchitect` node. The editor keeps `configuration_json` as its portable
source of truth, mirrors the basic values to visible node widgets, and marks the graph dirty when
the user saves changes.

`prompt_architect_state.js` contains the pure, independently tested state parser and serializer.
Composition and authoritative validation remain in the Python core; no prompt selection logic is
implemented in the browser.

The stylesheet uses ComfyUI theme variables with accessible fallbacks, keyboard focus states,
reduced-motion handling, and a responsive single-column layout.

The advanced editor loads profile metadata from the versioned local API and provides Basic,
Fields, Groups, and Preview & JSON tabs. Field modes, values, tag filters, group locks/seeds,
server preview, manifest inspection, reset, and JSON import/export remain synchronized with the
same workflow configuration. Profile changes that would discard fixed or custom values require explicit
confirmation.
