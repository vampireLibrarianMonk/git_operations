# Improved Git Commit Message

## Summary

Add an interactive Bedrock model selection workflow to the CLI. Users can now run
`gitops-summary model` to choose their preferred model family (Claude, Llama,
Mistral, Amazon Nova) and then select a specific model within that family. The
selection is persisted locally and used automatically by all subsequent Bedrock
calls, replacing the previously hard-coded default.

---

## Modified Files

| File | Change Summary |
|------|---------------|
| `src/gitops_summary/bedrock.py` | Replace static `MODEL_ID` import with `load_model_id()` so the runtime model respects the user's saved selection |
| `src/gitops_summary/cli.py` | Register the `model` subcommand, import and route to `model_workflow` |

## New Files

| File | Change Summary |
|------|---------------|
| `src/gitops_summary/model.py` | Model catalog, `load_model_id`/`save_model_id` persistence helpers, and interactive family→model selection workflow |
