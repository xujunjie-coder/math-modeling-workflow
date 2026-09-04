# 装配清单契约

`paper/master/assembly_manifest.json` 至少包含：

```json
{
  "schema_version": 1,
  "paper_scope": "full_submission",
  "competition": "",
  "problem_id": "",
  "questions": ["Q1"],
  "question_mapping": {
    "Q1": {
      "goal": "",
      "inputs": [],
      "upstream": [],
      "core_outputs": [],
      "downstream": [],
      "claims": [],
      "figures": [],
      "tables": [],
      "target_section": "6.1",
      "source_section": "paper/sections/Q1/q1_model_and_results.md",
      "section_manifest": "paper/sections/Q1/q1_section_manifest.json"
    }
  },
  "global_sources": {
    "problem_parse": "",
    "assumptions": "",
    "symbol_table": "",
    "references": ""
  },
  "deduplication": [
    {
      "topic": "",
      "source_blocks": [],
      "kept_at": "",
      "disposition": "merged|kept_local|excluded",
      "reason": ""
    }
  ],
  "renumbering": {
    "figures": {},
    "tables": {},
    "equations": {},
    "references": {}
  },
  "validation": {
    "structural_passed": false,
    "claim_map_passed": false,
    "artifact_paths_passed": false
  }
}
```

## Requirements

- `questions` must match active submission manifests.
- Each Qx maps to one unique `6.x` section.
- Every retained claim/figure/table has a source and destination.
- `renumbering` maps initial chapter-based figure/table labels (e.g., `图1-1`, `表1-1`) to final sequential labels (`图1`, `表1`), enabling in-text reference replacement after human review.
- Duplicate disposition is explicit; absence from the final paper is not silently inferred.
- Validation booleans are observed results, not placeholders copied into a final manifest.
