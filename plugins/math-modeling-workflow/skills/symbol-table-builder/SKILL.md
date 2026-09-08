---
name: symbol-table-builder
description: Build and maintain one global mathematical symbol and unit table from the problem frame and active method cards, resolving cross-subquestion conflicts before code or paper work.
---

# Purpose

Ensure the same concept uses one symbol and different concepts do not collide.

# Inputs

- problem parse and relationships;
- active `methods/Qx/qx_method_card.md`;
- approved code plans when available;
- question dependency map;
- existing `planning/symbol_table.md`.

Read legacy candidate pools only when method cards are absent.

# Workflow

1. Extract inputs, outputs, parameters, decisions, states, indices, sets, functions, and intermediate quantities.
2. Preserve user-established notation unless it conflicts or is ambiguous.
3. Resolve:
   - same meaning with different symbols;
   - different meanings with the same symbol;
   - unit/domain conflicts;
   - Qx output-to-input handoff conflicts.
4. Classify each symbol by role and scope.
5. Save or update `planning/symbol_table.md`.
6. If a canonical symbol changes, classify it `CANONICAL` and run scoped consistency for affected Qx.

# Table Fields

- symbol;
- plain name;
- definition;
- type: input, output, parameter, estimated parameter, decision, state, intermediate, index, set, function;
- domain/range;
- unit;
- scope/Qx;
- source artifact;
- notes or conflict resolution.

# Rules

- **Capacity & Positioning (6–15 Lines)**: The symbol description table in the contest paper acts as a concise dictionary, not an exhaustive registry of all scratch variables. The table MUST be kept within **6–15 rows** (maximum ~17 rows, strictly under half a page). It must NEVER cross pages or fill an entire page.
- **One Family per Line ("一族一行")**: Group different subscripts of the same physical quantity into a single general row (e.g. $x_i$: mass fraction of the $i$-th component; $T_{50, j}$: characteristic transition temperature of catalyst $j$).
- **Strict Negative Exclusion List (NEVER include in the master symbol table)**:
  1. Statistical model internal parameters: regression coefficients $\beta_0, \beta_i$, residuals/error terms $\varepsilon$, variance $\sigma^2$, weights $w_i$;
  2. Algorithm hyperparameters & internal thresholds: learning rate $\eta$, penalty coefficient $\lambda$, tolerance $\delta$, similarity threshold $\tau$;
  3. Pure mathematical summation/loop indices: indices $i, j, k$, integration variable $t$, indicator function $I(\cdot)$;
  4. Local intermediate quantities that appear only once in a specific derivation.
- **In-Situ Formula Explanations**: Any local variables, regression parameters, or algorithm thresholds excluded from the master table MUST be explained immediately below their respective equations using "设/记/其中/式中...". When recurring in later sections, note "...含义同前".
- **Units & Dimensions**: State units clearly (e.g. `^\circ\text{C}`, `\text{kJ/mol}`). Dimensionless quantities must be explicitly marked as "无" or "1" or "/", never left empty.
- Define every symbol before first use.
- Code variable mappings must adhere to the non-standard naming rules: chemical formulas for elements/compounds (e.g. `Pb`, `SiO2`), CET-4 English for common terms, and Pinyin for domain/out-of-scope concepts.
- Record units and domains when applicable.
- Use one notation for cross-question handoffs.
- Do not invent variables to make a table look complete.
- Do not maintain a separate verbose conflict log; record material resolutions in the table notes.

# Verification

- Active method-card and code-plan variables are covered.
- No unresolved symbol or unit collision remains.
- Shared quantities agree across Qx.
- Downstream artifacts can cite one canonical table.
