# Database Test Automation Standards

Use these standards when generating Java TestNG Maven database tests.

## Project Shape

- Use Maven with Java 17 or newer.
- Keep database tests under `src/test/java`.
- Use TestNG for lifecycle and assertions.
- Use JDBC or an approved internal database helper layer.
- Keep JDBC URLs, usernames, passwords, schemas, and environment names outside
  source code.

## Safety

- Default to read-only validation.
- Never point generated tests at production unless an explicit read-only,
  approved validation path exists.
- Avoid destructive SQL such as `DELETE`, `TRUNCATE`, `DROP`, or broad `UPDATE`
  statements unless the test case explicitly requires controlled cleanup.
- Use transactions for setup and cleanup where possible.

## SQL

- Use parameterized queries through `PreparedStatement`.
- Do not build SQL by string-concatenating user or test data.
- Keep queries small and explainable.
- Prefer business keys owned by the test data set.

## Assertions

- Assert row counts when presence or absence matters.
- Assert specific column values for the business rule.
- Assert timestamps with tolerances when clock differences are possible.
- Assert relational integrity when the test case crosses tables.

## Test Data

- Use isolated schemas or test-owned records.
- Seed test data in setup when needed.
- Clean up created records, or use generated unique IDs so reruns are safe.

## Must Avoid

- Do not log passwords, connection strings with secrets, or personal data.
- Do not make tests depend on manual database state.
- Do not hide SQL exceptions without failing the test.
