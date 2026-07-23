# Prompt Architect Setup Library

Store reusable setup JSON snippets directly inside your workflow file.

## Inputs

This utility node has no input ports.

## Outputs

This utility node has no output ports.

## Workflow behavior

Use **Open Setup Library** to manage setup cards in a dedicated editor:

- **Add setup** creates a new card.
- Each card provides:
  - **Name**
  - **Description**
  - **Setup JSON**
  - **Copy setup** button
  - **Delete** button
- **Save library** validates every setup JSON and stores the library in workflow metadata.

The node does not execute network requests or file system writes. Data is serialized into the
workflow itself so experiments can be kept together with the graph.
