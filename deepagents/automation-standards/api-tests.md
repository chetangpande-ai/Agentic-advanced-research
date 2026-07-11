# API Test Automation Standards

Use these standards when generating Java TestNG Maven API tests.

## Project Shape

- Use Maven with Java 17 or newer.
- Keep API tests under `src/test/java`.
- Use TestNG annotations: `@BeforeClass`, `@BeforeMethod`, `@Test`, and
  `@AfterMethod` when setup or cleanup is needed.
- Use Rest Assured for HTTP calls.
- Keep base URLs, credentials, tokens, tenant IDs, and environment names outside
  source code. Read them from Maven system properties, environment variables, or
  a test configuration layer.

## Naming

- Test class names end with `ApiTest`.
- Test method names should describe behavior, not implementation.
- Prefer names like `shouldReturnOrderStatusForValidOrderId`.

## Assertions

- Assert HTTP status code.
- Assert required response fields.
- Assert key headers when relevant, such as content type and correlation IDs.
- Assert business rules, not only that the API returns any response.
- Validate negative paths when the test case includes invalid, missing, expired,
  duplicate, or unauthorized data.

## Test Data

- Use stable test data owned by automation.
- Do not depend on production records.
- When tests create data, clean it up or make creation idempotent.
- Never log secrets, access tokens, passwords, or full personal data.

## Reliability

- Avoid fixed sleeps.
- Use request timeouts and retry only for known transient setup operations.
- Make tests independent; one test must not require another test to run first.
- Capture enough request and response context to debug failures, while redacting
  sensitive values.

## Must Avoid

- Do not hardcode live production URLs.
- Do not assert only `response != null`.
- Do not hide failures in broad `try/catch` blocks.
- Do not mix API test setup, business assertions, and cleanup in one unreadable
  method.
