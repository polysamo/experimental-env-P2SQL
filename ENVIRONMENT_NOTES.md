# Experimental environment notes

## Base environment

The environment uses one application stack and activates defenses according to the selected scenario. This matches the paper design where the base system is fixed and security controls are layered on top.

## Scenario behavior

- **C0**: direct LLM-to-SQL generation and execution, with only logging.
- **C1**: adds input screening and policy enforcement.
- **C2**: adds SQL validation and output filtering on top of C1.
- **C3**: same as C2, but one layer is disabled through `ABLATION_DISABLED_LAYER`.

## Current permissions model

- Legitimate reads: `users`, `job_posts`, `applications`
- Restricted tables: `admin_notes`, `audit_logs`
- Writes: disabled by default through `ALLOW_WRITE_OPERATIONS=false`

## What you still need to plug in

1. Your actual OpenAI-compatible model endpoint.
2. Your final `04_prompt_dataset_final.csv`.
3. Your execution driver to send prompts into `/query`.
4. Your final evaluation script over the collected logs.
