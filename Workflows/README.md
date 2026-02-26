# Workflows

A workflow is a repeatable process that Claude executes with you.
Each workflow lives in its own folder with its own CLAUDE.md.

## Structure

```
Workflows/[workflow-name]/
├── CLAUDE.md           ← Context when Claude enters this workflow
├── workflow-spec.md    ← Steps, inputs, outputs, rules
├── step-1.md           ← Step-level instructions (add as needed)
└── Drafts/             ← Work in progress outputs
```

## Creating a New Workflow

1. Copy `_template/` to `Workflows/[workflow-name]/`
2. Edit `workflow-spec.md` with the specific process
3. Break complex steps into `step-N.md` files
4. Test once manually, then run via Claude

## Existing Workflows

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| _(none yet)_ | | |
