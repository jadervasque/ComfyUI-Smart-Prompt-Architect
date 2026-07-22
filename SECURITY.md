# Security Policy

## Supported versions

Prompt Architect is pre-release software. No version is currently supported for production use.
This section will be updated before the public beta.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting for the repository when it becomes public. Do
not disclose exploitable details in a public issue. Publisher contact information remains a
placeholder and will be added before publication.

Include the affected version or commit, impact, reproduction steps, and any suggested mitigation.
No response-time commitment is made during pre-alpha development.

## Security boundaries

The node must not execute profile code, access the network while composing, install packages at
runtime, invoke subprocesses, accept arbitrary paths, or persist user libraries in the MVP.
