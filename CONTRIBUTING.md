# Contributing

Contributions are welcome through issues and pull requests.

## Principles

- Keep skills reusable across contests and datasets.
- Do not submit real contest attachments, team identities, private papers, credentials, or materials without redistribution rights.
- Preserve the human-decision boundary: a skill may present evidence and choices but must not fabricate the modeler's decision.
- Preserve evidence traceability from data and code to figures and paper claims.
- Avoid adding a skill when a focused update to an existing skill is sufficient.

## Before submitting

```powershell
python plugins/math-modeling-workflow/scripts/validate_repo.py .
python -m unittest discover -s tests -v
```

Describe the workflow stage affected, observable behavior changed, compatibility impact, and any new artifact contract.
