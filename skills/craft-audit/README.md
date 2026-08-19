# CRAFT Audit Skill

This directory is the **complete runtime unit** for the CRAFT structural resilience audit.

```text
craft-audit/
├── SKILL.md
└── references/
    ├── profile.md
    └── output-schema.md
```

> **Keep this directory intact.** `SKILL.md` resolves both reference files by relative path. Copying `SKILL.md` alone creates an incomplete installation.

## File responsibilities

- **`SKILL.md`** — agent procedure: repository inventory, boundary discovery, evidence resolution, scoring, findings, remediation and output generation.
- **`references/profile.md`** — normative scoring profile (`CRAFT/MS-1.1.1`): weights, conditional rules, maxima, penalties and normalization rules.
- **`references/output-schema.md`** — machine-readable contract for audit JSON and corpus-level outputs.

## Installing from source

Copy the entire `craft-audit` directory into the skill search path used by your agent runtime. The exact installation path is runtime-specific; the invariant is that `SKILL.md` and `references/` remain siblings exactly as shown above.

## Packaged distribution

From the repository root, run:

```bash
python3 scripts/package_skill.py
```

This creates:

```text
dist/craft-audit.skill
```

The `.skill` file is a ZIP-compatible archive containing this same directory structure.
