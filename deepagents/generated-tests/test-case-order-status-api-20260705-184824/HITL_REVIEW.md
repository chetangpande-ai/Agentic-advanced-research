        # HITL Review

        Generated project:

        ```text
        D:\AI\Agentic-Practise\deepagents\generated-tests\test-case-order-status-api-20260705-184824
        ```

        ## Reviewer Checklist

        - [ ] Test case intent is correctly understood.
        - [ ] Category selection is correct.
        - [ ] Environment URLs, credentials, and tokens are not hardcoded.
        - [ ] Assertions match the expected business outcome.
        - [ ] Test data is safe for repeat execution.
        - [ ] Generated code follows the local automation standards.
        - [ ] Validation result is acceptable.

        ## Clarity Result

        ```json
        {
  "status": "clear",
  "ready_for_generation": true,
  "signals": [],
  "questions": []
}
        ```

        ## Category Result

        ```json
        {
  "web_vs_non_web": "non-web",
  "primary_category": "api",
  "scores": {
    "web": 1,
    "api": 7,
    "database": 0
  },
  "standards_file": "api-tests.md"
}
        ```

        ## Validation Result

        ```json
        {
  "project_dir": "D:\\AI\\Agentic-Practise\\deepagents\\generated-tests\\test-case-order-status-api-20260705-184824",
  "static_validation": {
    "status": "passed",
    "issues": [],
    "java_files": [
      "src\\test\\java\\com\\example\\generated\\TestCaseOrderStatusApiApiTest.java"
    ]
  },
  "compile_validation": {
    "status": "skipped",
    "reason": "Maven was not found on PATH. Static validation still ran.",
    "command": "mvn -q -DskipTests test-compile"
  }
}
        ```
