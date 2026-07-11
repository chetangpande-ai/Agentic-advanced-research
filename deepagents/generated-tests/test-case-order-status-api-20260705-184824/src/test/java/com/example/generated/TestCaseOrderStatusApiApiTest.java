package com.example.generated;

import io.restassured.RestAssured;
import org.testng.annotations.Test;

import static io.restassured.RestAssured.given;
import static org.testng.Assert.assertEquals;
import static org.testng.Assert.assertFalse;

public class TestCaseOrderStatusApiApiTest {

    @Test
    public void shouldReturnOrderStatusForValidOrderId() {
        RestAssured.baseURI = System.getProperty("api.baseUri", "https://example.test");

        String orderId =
            given()
                .header("Accept", "application/json")
            .when()
                .get("/orders/{orderId}/status", "ORD-1001")
            .then()
                .statusCode(200)
                .extract()
                .path("orderId");

        assertEquals(orderId, "ORD-1001", "The API should return the requested order ID.");
        assertFalse(orderId.isBlank(), "The order ID should not be blank.");
    }
}
