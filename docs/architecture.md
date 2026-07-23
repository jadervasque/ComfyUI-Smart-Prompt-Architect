# Architecture

Prompt Architect separates its framework-independent domain core from application orchestration,
infrastructure, the ComfyUI API V3 adapter, and frontend assets.

Dependency direction is inward: frontend and ComfyUI adapters may call application services;
application services may use domain contracts and infrastructure interfaces; the domain package
must not import ComfyUI, HTTP frameworks, or frontend code.

The engine pipeline will load validated data, resolve modes and locks, select compatible values,
apply rules, validate structured context, render text, normalize it, validate final output, and
build a manifest. Selection must happen before rendering. Node execution must not access the
network, execute user code, invoke subprocesses, install packages, or accept arbitrary paths.

Detailed contracts and algorithms are introduced stage by stage in `plans/PLAN0.md`.
