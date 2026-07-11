        # Generated TestNG Automation

        Category: `api`

        Main generated test:

        ```text
        src/test/java/com/example/generated/TestCaseOrderStatusApiApiTest.java
        ```

        Compile the generated tests:

        ```powershell
        mvn -q -DskipTests test-compile
        ```

        ## Source Test Cases

        ```text
        # Test Case: Order Status API

Test case ID: API-ORD-001

Scenario:
Verify that the order status API returns the latest status for a valid order.

Preconditions:
- A valid customer exists.
- Order `ORD-1001` exists for that customer.
- The caller has a valid bearer token with order read permission.

Steps:
1. Send a GET request to `/orders/{orderId}/status` with `orderId=ORD-1001`.
2. Include the `Accept: application/json` header.
3. Include a valid bearer token.

Expected results:
- The response status code is `200`.
- The response contains `orderId=ORD-1001`.
- The response contains a non-empty `status` field.
- The response contains `lastUpdatedAt` in ISO-8601 format.
        ```
