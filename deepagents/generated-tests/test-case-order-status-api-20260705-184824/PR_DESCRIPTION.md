# Add generated TestNG automation

## Summary

- Adds generated Java TestNG Maven automation under `test-case-order-status-api-20260705-184824`.
- Includes HITL review evidence.
- Keeps environment-specific values outside Java source.

## Validation

- Static validation: `passed`
- Maven test compile: `skipped`

## Suggested Commands

```powershell
git checkout -b feature/generated-testng-automation
git add deepagents/generated-tests/test-case-order-status-api-20260705-184824
git commit -m "Add generated TestNG automation"
gh pr create --title "Add generated TestNG automation" --body-file deepagents/generated-tests/test-case-order-status-api-20260705-184824/PR_DESCRIPTION.md
```

## Reviewer Notes

Review `HITL_REVIEW.md` before opening or merging the PR.
