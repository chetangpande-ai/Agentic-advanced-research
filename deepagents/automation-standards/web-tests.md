# Web Test Automation Standards

Use these standards when generating Java TestNG Maven web UI tests.

## Project Shape

- Use Maven with Java 17 or newer.
- Keep UI tests under `src/test/java`.
- Use TestNG for test lifecycle and assertions.
- Use Selenium WebDriver for browser automation.
- Prefer a Page Object Model when the generated test has more than one page or
  repeated interactions.

## Locators

- Prefer stable product-owned locators such as `data-testid`, `id`, or explicit
  accessibility labels.
- Avoid brittle absolute XPath.
- Avoid locators based only on CSS position, visual order, or translated text
  unless the test case is specifically validating that text.

## Synchronization

- Use explicit waits for visible, clickable, present, or stale states.
- Do not use `Thread.sleep` for normal synchronization.
- Keep timeout values configurable.

## Test Data And Environment

- Read app URL, browser, credentials, and feature flags from configuration.
- Do not hardcode passwords or tokens in Java files.
- Use test-owned users and reset state before or after tests.

## Assertions

- Assert visible user outcomes, not only that a button was clicked.
- Assert page URL, visible messages, table rows, field values, or state changes
  based on the test case.
- For negative tests, assert both the error message and that invalid state was
  not saved.

## Failure Evidence

- Capture screenshots on failure.
- Capture browser console logs when the framework supports it.
- Include the test case ID in test method comments or metadata when available.

## Must Avoid

- Do not keep WebDriver setup inside every test method when a shared setup class
  exists.
- Do not rely on test execution order.
- Do not automate visual layout checks with ordinary functional assertions unless
  the test case explicitly requires it.
