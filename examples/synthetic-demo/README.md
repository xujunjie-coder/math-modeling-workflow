# Synthetic Demo

This example is intentionally small and synthetic. It demonstrates workspace discovery and early routing without embedding a real contest statement or a finished solution.

Suggested prompt:

```text
Use $workflow-orchestrator to inspect this synthetic project, parse the problem statement, and report the next gate action. Do not infer a method decision for me.
```

Expected initial route: `problem-parser`, followed by `problem-classifier` and `data-auditor-cleaner` as evidence becomes available.
