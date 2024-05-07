# Vendor Management System

## Contents

- #### [Setup](#setup)
- #### [API Documentations](#api-documentation)
- #### [Tests](#test-documentation)

## Setup

- **Requirements**

  `python` `v.3.10` (_recommended version_)

- **Clone Github Repository**  
  Clone the github repository to your local machine:

  ```bash
  git clone https://github.com/febinmathew-xd/vendor-management-system.git
  ```

- **Setup a Virtual Environment**  
  create a new virtual environment and activate it:

  ```bash
  #create virtual env
  python -m venv venv
  # activate vitual env
  source venv/bin/activate
  ```

- **Install Dependencies**  
  After activating virtual environment, install the required packages:

  ```bash
  pip install -r requirements.txt
  ```

- **Migrate the Database and Start Server**  
  With everything set up, migrate the database and run the development server:

  ```bash
  python manage.py makemigrations
  python manage.py migrate
  python manage.py runserver
  ```

## API DOCUMENTATION

### Overview

The vendor management system API allows developers to manage **user**, **vendors** and **purchase order**.

### Authentication

Authentication is required for all endpoints. Client must provide a valid access key in the `Authorization` header.

## Endpoints:

## User

### create user

- **Endpoint :** `/api/user/register/`
- **Method :** `POST`
- **Description :** Create a new user.
- **Authentication :** Not required
- **Request Body :**

  (_required fields_)

  - `username` (_string_) : Username for the new user.
  - `email` (_string_) : The user's email address.
  - `password`(_string_) : Password for the new user.

- **Example Request Body:**

  ```json
  {
    "username": "example",
    "email": "example@mail.com",
    "password": "password123"
  }
  ```

- **Response :**  
  On successful creation, the api will return the following response:

  - **status :** `201 CREATED`
  - **Body :** `id` `username` `email`
  - **Example Body :**

    ```json
    {
      "id": 1,
      "username": "example",
      "email": "example@mail.com"
    }
    ```

- **Error**

  - `400 BAD_REQUEST` : Request body is invalid.possibly due to missing required field.

---

## Authorization Tokens (access token, refresh token)

### Obtain Token Pair

- **Endpoint :** `/api/token/`
- **Method :** `POST`
- **Description :** Get `access` token and `refresh` token for authentication and authorization of the user.
- **Authentication :** Not required
- **Request Body :**

  (_required fields_)

  - `username` (_string_) : username of the user.
  - `password` (_string_) : password of the user.

- **Example Request Body:**

  ```json
  {
    "username": "example",
    "password": "password123"
  }
  ```

- **Response :**  
  on successful request the api will return the following response:

  - **status :** `200 OK`
  - **Body :** `access` `refresh`
  - **Example Body :**

    ```json
    {
      "access": "hhsfd78h3JYJefssdfsfwDFD34fweft4343DFD42e3dg3dgds",
      "refresh": "ssdFBFGDGfsfwDFD34fwe3dg3dgds2DFDl9slFGDffd5tRTR"
    }
    ```

- **Error :**

  - `400 BAD_REQUEST` invalid or missing required fields.
  - `401 UNAUTHORIZED` incorrect username or password.

---

## Vendor

### Create Vendor

- **Endpoint :** `/api/vendors/`
- **Method :** `POST`
- **Description :** Create a new vendor .
- **Authentication :** (_required_) provide `access` token in `Authorization` header.
- **Request Body :**

  (_required fields_)

  - `user` (_integer_) : user ID of the user.
  - `name` (_string_) : name of the new vendor.
  - `contact_details` (_string_) : contact details of the vendor.
  - `address` (_string_) : address of the vendor.

  (_optional fields_)

  - `vendor_code` (_string_) (_unique_) : unique identification code for the vendor.

- **Example Request Body:**

  ```json
  {
  "user": 1,
  "name": "example",
  "contact_details": "sample contact details",
  "address": "sample address"
  "vendor_code": "34353534332"
  }
  ```

- **Response :**  
  On successful creation, the API will return the following response:

  - **status :** `201 CREATED`
  - **Body :** `id` `name` `contact_details` `address` `vendor_code` `user` `fulfillment_rate` `on_time_delivery_rate` `quality_rating_avg` `average_response_time`
  - **Example Body :**

    ```json
    {
      "id": 1,
      "name": "sample",
      "contact_details": "sample contact",
      "address": "sample address",
      "vendor_code": "34353634643",
      "user": 1,
      "fulfillment_rate": 0.0,
      "on_time_delivery_rate": 0.0,
      "quality_rating_avg": 0.0,
      "average_response_time": 0.0
    }
    ```

- **Error :**

  - `400 BAD_REQUEST` Invalid or missing required field.
  - `401 UNAUTHORIZED` Expired/invalid access token or access token is not provided.

---

### List All Vendors

- **Endpoint :** `/api/vendors/`
- **Method :** `GET`
- **Description :** List all vendors.
- **Authentication :** provide `access` token in `Authorization` header (_required_).
- **Request Body :** None
- **Response :**  
  On successful request, the API will return following response:

  - **status :** `200 OK`
  - **Body :** List of all `vendor` details.

- **Error :**

  - `401 UNAUTHORIZED` Expired/invalid `access` token or `access` token is not provided.

---

### Get Vendor by ID

- **Endpoint :** `/api/vendors/{vendor_id}/`
- **Method :** `GET`
- **Parameter :** `vendor_id` ID of the vendor .
- **Description :** Retrive a specific vendor details by `vendor_id`.
- **Authentication :** provide `access` token in `Authorization` header (_required_).
- **Request Body :** None
- **Response :**  
  On successful request, the API will return following response:

  - **status :** `200 OK`
  - **Body :** Vendor details of the provided `vendor_id`.
  - **Example Body :**

    ```json
    {
      "id": 1,
      "name": "sample",
      "contact_details": "sample contact",
      "address": "sample address",
      "vendor_code": "34353634643",
      "user": 1,
      "fulfillment_rate": 0.0,
      "on_time_delivery_rate": 0.0,
      "quality_rating_avg": 0.0,
      "average_response_time": 0.0
    }
    ```

- **Error :**

  - `404 NOT_FOUND` Provided `vendor_id` is not valid.
    vendor details not found.
  - `401 UNAUTHORIZED` Expired/invalid `access` token or `access` token is not provided.

---

### Update Vendor by ID

- **Endpoint :** `/api/vendors/{vendor_id}/`
- **Method :** `PUT`
- **Parameter :** `vendor_id` id of the vendor.
- **Description :** Update a specific vendor details by `vendor_id`.
- **Authentication :** provide `access` token in `Authorization` header (_required_).
- **Request Body :** Fields which you want to update.All field is not required .

- **Example Request Body :**

  ```json
  {
    "name": "new name",
    "address": "new address"
  }
  ```

- **Response :**  
  On successful request, the API will return following response:

  - **status :** `200 OK`
  - **Body :** Updated vendor details of the provided `vendor_id`.
  - **Example Body :**

    ```json
    {
      "id": 1,
      "name": "new name",  #updated name
      "contact_details": "sample contact",
      "address": "new address",  #updated address
      "vendor_code": "34353634643",
      "user": 1,
      "fulfillment_rate": 0.0,
      "on_time_delivery_rate": 0.0,
      "quality_rating_avg": 0.0,
      "average_response_time": 0.0
    }
    ```

- **Error :**

  - `400 BAD_REQUEST` Invalid request body data.
  - `404 NOT_FOUND` Provided `vendor_id` is not valid.
    vendor details not found.
  - `403 FORBIDDEN` `user` doesnot have the permission to update `vendor`. Because of `user` is not the owner of the `vendor`.
  - `401 UNAUTHORIZED` Expired/invalid `access` token or `access` token is not provided.

---

### Delete Vendor by ID

- **Endpoint :** `/api/vendors/{vendor_id}/`
- **Method :** `DELETE`
- **Parameter :** `vendor_id` id of the vendor .
- **Description :** Delete a specific vendor by `vendor_id`.
- **Authentication :** provide `access` token in `Authorization` header (_required_).
- **Request Body :** None
- **Response :**  
  On successful request, the API will return following response:

  - **status :** `200 OK`
  - **Body :** `message` saying vendor successfully deleted.
  - **Example Body :**

    ```json
    {
      "message": "successfully deleted"
    }
    ```

- **Error :**

  - `404 NOT_FOUND` Provided `vendor_id` is not valid.
    vendor details not found.
  - `403 FORBIDDEN` `user` doesnot have the permission to delete `vendor`. Because of `user` is not the owner of the `vendor`.
  - `401 UNAUTHORIZED` Expired/invalid `access` token or `access` token is not provided.

---

### Get Vendor Performance

- **Endpoint :** `/api/vendors/{vendor_id}/performance/`
- **Method :** `GET`
- **Parameter :** `vendor_id` id of the vendor.
- **Description :** Retrieves the calculated performance metrics for a specific vendor.
- **Authentication :** provide `access` token in `Authorization` header (_required_).
- **Request Body :** None
- **Response :**  
  On successful request, the API will return following response:

  - **status :** `200 OK`
  - **Body :** calculated matrics of the vendor .
  - **Example Body :**

    ```json
    {
      "on_time_delivery_rate": 1.0,
      "quality_rating_avg": 4.5,
      "average_response_time": 1.5,
      "fulfillment_rate": 0.7
    }
    ```

- **Error :**

  - `404 NOT_FOUND` Provided `vendor_id` is not valid.
    vendor details not found.
  - `401 UNAUTHORIZED` Expired/invalid `access` token or `access` token is not provided.

---

## Purchase Order

### Create Purchase Order

- **Endpoint :** `/api/purchase_orders/`
- **Method :** `POST`
- **Description :** Create a purchase order .
- **Authentication :** (_required_) provide `access` token in `Authorization` header .
- **Request Body :**

  (_required fields_)

  - `vendor` (_integer_) : `id` of the vendor.
  - `delivery_date` (_datetime_) : Expected or actual delivery date of the order.
  - `items` (_json_) : details of the items ordered.
  - `quantity` (_integer_) : total quantity of items in the purchase order.

  (_optional fields_)

  - `po_number` (_string_) (_unique_) : Unique number for identifying the purchase order.
  - `quality_rating` (_float_) : Rating given to the vendor for this purchase order (nullable) .

- **Example Request Body:**

  ```json
  {
    "vendor": 1,
    "delivery_date": "2024-05-06 15:02:02.759037+00:00",
    "items": [
      { "name": "item1", "price": 2999 },
      { "name": "item2", "price": 1000 }
    ],
    "quantity": 2,
    "po_number": "34353534332"
  }
  ```

- **Response :**  
  On successful creation, the API will return the following response:

  - **status :** `201 CREATED`
  - **Body :** `id` `po_number` `vendor` `delivery_date` `items` `quantity` `order_date` `status` `quality_rating` `issue_date` `acknowledgement_date`
  - **Example Body :**

    ```json
    {
      "id": 1,
      "po_number": "3555334864",
      "vendor": 1,
      "delivery_date": "2024-05-06 15:02:02.759037+00:00",
      "items": [
        { "name": "item1", "price": 2999 },
        { "name": "item2", "price": 1000 }
      ],
      "quantity": 2,
      "order_date": "2024-05-06 15:02:02.759037+00:00",
      "issue_date": "2024-05-06 15:02:02.759037+00:00",
      "status": "pending",
      "quality_rating": null,
      "acknowledgement_date": null
    }
    ```

- **Error :**

  - `400 BAD_REQUEST` Invalid or missing required field.
  - `401 UNAUTHORIZED` Expired/invalid access token or access token is not provided.

---

### Acknowledge Purchase Order

- **Endpoint :** `/api/purchase_orders/{po_id}/acknowledge/`
- **Method :** `POST`
- **Paramater :** `po_id` purchase order id .
- **Description :** Update `acknowledgement_date` of the purchase order with `po_id` .
- **Authentication :** (_required_) provide `access` token in `Authorization` header.
- **Request Body :** None

- **Response :**  
  On successful request, the API will return the following response:

  - **Status :** `200 OK`
  - **Body :** `message` saying purchase order acknowledged by the vendor.
  - **Example Body :**

    ```json
    { "message": "purchase order acknowledged by the vendor" }
    ```

- **Error :**

  - `403 BAD_REQUEST` `vendor` doesnot have the permission to acknowldge the purchase order (not owner).
  - `404 NOT_FOUND` Invalid purchase order id `po_id` .
  - `401 UNAUTHORIZED` Expired/invalid `access` token or `access` token is not provided.

---

### List All Purchase Order (Filter by Vendor)

- **Endpoint :** `/api/purchase_orders/?vendor_id={id}`
- **Method :** `GET`
- **Paramater :** `id` vendor id.
- **Description :** List all purchase order with an option to filter by vendor.
- **Authentication :** (_required_) provide `access` token in `Authorization` header.
- **Request Body :** None

- **Response :**  
  On successful request, the API will return the following response:

  - **Status :** `200 OK`
  - **Body :** List of all purchase order of the vendor with `id` .

- **Error :**

  - `400 BAD_REQUEST` `id` parameter is not given.
  - `404 NOT_FOUND` Vendor with `id` not found. Invalid `id` .
  - `401 UNAUTHORIZED` Expired/invalid `access` token or `access` token is not provided.

---

### Get Purchase Order by ID

- **Endpoint :** `/api/purchase_orders/{po_id}/`
- **Method :** `GET`
- **Parameter :** `po_id` purchase order id.
- **Description :** Retrive a specific purchase order details by `po_id` .
- **Authentication :** provide `access` token in `Authorization` header (_required_).
- **Request Body :** None
- **Response :**  
  On successful request, the API will return following response:

  - **status :** `200 OK`
  - **Body :** Purchase order details of the provided purchase order id `po_id` .
  - **Example Body :**

    ```json
    {
      "id": 1,
      "po_number": "3555334864",
      "vendor": 1,
      "delivery_date": "2024-05-06 15:02:02.759037+00:00",
      "items": [
        { "name": "item1", "price": 2999 },
        { "name": "item2", "price": 1000 }
      ],
      "quantity": 2,
      "order_date": "2024-05-06 15:02:02.759037+00:00",
      "issue_date": "2024-05-06 15:02:02.759037+00:00",
      "status": "pending",
      "quality_rating": null,
      "acknowledgement_date": null
    }
    ```

- **Error :**

  - `404 NOT_FOUND` Provided `po_id` is not valid.
    Purchase order not found.
  - `401 UNAUTHORIZED` Expired/invalid `access` token or `access` token is not provided.

---

### Update Purchase Order by ID

- **Endpoint :** `/api/purchase_orders/{po_id}/`
- **Method :** `PUT`
- **Parameter :** `po_id` purchase order id.
- **Description :** Update a specific purchase order details by `po_id` .
- **Authentication :** provide `access` token in `Authorization` header (_required_).
- **Request Body :** Fields which you want to update .All fields are not required .
- **Example Request Body :**

  ```json
  {
    "status": "completed",
    "quality_rating": 5.0
  }
  ```

- **Response :**  
  On successful request, the API will return following response:

  - **status :** `200 OK`
  - **Body :** Updated purchase order details of the provided purchase order id `po_id` .
  - **Example Body :**

    ```json
    {
      "id": 1,
      "po_number": "3555334864",
      "vendor": 1,
      "delivery_date": "2024-05-06 15:02:02.759037+00:00",
      "items": [
        { "name": "item1", "price": 2999 },
        { "name": "item2", "price": 1000 }
      ],
      "quantity": 2,
      "order_date": "2024-05-06 15:02:02.759037+00:00",
      "issue_date": "2024-05-06 15:02:02.759037+00:00",
      "status": "completed",  #updated
      "quality_rating": 5.0,  #updated
      "acknowledgement_date": null
    }
    ```

- **Error :**

  - `400 BAD_REQUEST` Invalid request body data .
  - `403 FORBIDDEN` Vendor doesnot have the permission to update the purchase order (not owner).
  - `404 NOT_FOUND` Provided `po_id` is not valid.
    Purchase order not found.
  - `401 UNAUTHORIZED` Expired/invalid `access` token or `access` token is not provided.

---

### Delete Purchase Order by ID

- **Endpoint :** `/api/purchase_orders/{po_id}/`
- **Method :** `DELETE`
- **Parameter :** `po_id` purchase order id .
- **Description :** Delete a specific purchase by `po_id`.
- **Authentication :** provide `access` token in `Authorization` header (_required_).
- **Request Body :** None
- **Response :**  
  On successful request, the API will return following response:

  - **status :** `200 OK`
  - **Body :** `message` saying vendor successfully deleted.
  - **Example Body :**

    ```json
    {
      "message": "successfully deleted"
    }
    ```

- **Error :**

  - `404 NOT_FOUND` Provided `vendor_id` is not valid.
    vendor details not found.
  - `403 FORBIDDEN` Vendor doesnot have the permission to delete purchase order (not owner).
  - `401 UNAUTHORIZED` Expired/invalid `access` token or `access` token is not provided.

# Test Documentation

## Running All Tests

Inorder to run all tests, execute the following command from the `root` directory of the project(where `manage.py` is located) .

```bash
python manage.py test
```

## Running Specific Tests

### User and Authentication Tests

To run user-related tests, execute the following command from the root directory:

```bash
python manage.py test --pattern="test_user_creation.py"
```

#### Test cases

These test cases focus on user creation and token-based authentication.

- Token generation for authentication

- #### Create User

  - ##### Endpoint : `POST` `/api/user/register/`
  - ##### Tests :
    - Create user using valid credentials.
    - Create user using invalid credentials.
    - Create user using missing credentials.
    - Create user using duplicate username.
    - Create user using invalid email address.

- #### Obtain Token Pair
  - ##### Endpoint : `POST` `/api/token/`
  - ##### Tests :
    - Generate token with proper credentials.
    - Generate token with invalid credentials.
    - Generate token with missing required fields.

---

### Vendor Management Tests

To run vendor-related tests, execute the following command from the root directory:

```bash
python manage.py test --pattern="test_vendor.py"
```

#### Test Cases

These test cases cover vendor creation, retrieval, delete and update operations.

- #### Create Vendor

  - ##### Endpoint : `POST` `/api/vendors/`
  - ##### Tests :
    - Create vendor using valid data.
    - Create vendor using invalid data.
    - Create vendor with missing required fields.
    - Create vendor with unauthorized users.

- #### Retrive All Vendors

  - ##### Endpoint : `GET` `/api/vendors/`
  - ##### Tests :
    - Retrive all vendors with proper authorization.
    - Retrive all vendors without authorization.

- #### Vendor Details by ID

  - ##### Endpoint : `GET` `/api/vendors/{vendor_id}/`
  - ##### Tests :
    - Retirve with valid `vendor_id` and authorized users.
    - Retirve with invalid `vendor_id` .
    - Retirve with unauthorized users.

- #### Update Vendor by ID

  - ##### Endpoint : `PUT` `/api/vendors/{vendor_id}/`
  - ##### Tests :
    - Updating with valid `vendor_id` , valid data and authorized users.
    - Updating with invalid `vendor_id` .
    - Updating with invalid data.
    - Updating with non-owner users.
    - Updating with unauthorized users.

- #### Delete Vendor by ID

  - ##### Endpoint : `DELETE` `/api/vendors/{vendor_id}/`
  - ##### Tests :
    - Delete with valid `vendor_id` , ownership and authorization.
    - Delete with invalid `vendor_id`.
    - Delete with non-owner users.
    - Delete with authorized users.

- #### Vendor Performance Metrics
  - ##### Endpoint : `GET` `/api/vendors/{vendor_id}/performance/`
  - ##### Tests :
    - Retrive metrics with valid `vendor_id` and authorization.
    - Retrive metrics with invalid `vendor_id`.
    - Retrive metrics with unauthorized users.

---

### Purchase Order Tests

To run purchase order related tests, execute the following command from the root directory:

```bash
python manage.py test --pattern="test_purchase_order.py"
```

#### Test Cases

These test cases cover purchase order creation, retrieval, delete and update operations.

- #### Create Purchase Order

  - ##### Endpont : `POST` `/api/purchase_orders/`
  - ##### Tests :
    - Create purchase order using valid data and authorization.
    - Create purchase order using invalid data.
    - Create purchase order with unauthorized users.

- #### Retive List of Purchase Order by Vendor ID

  - ##### Endpoint : `GET` `/api/purchase_orders/?vendor_id={id}`
  - ##### Tests :
    - Retrive with valid `vendor_id` and authorization.
    - Retrive without providing parameter.
    - Retrive with invalid `vendor_id`.
    - Retrive with unauthorized users.

- #### Purchase Order Details by ID

  - ##### Endpoint : `GET` `/api/purchase_orders/{order_id}/`
  - ##### Tests :
    - Get with valid `order_id` and authorization.
    - Get with invalid `order_id`.
    - Get with unauthorized users.

- #### Update Purchase Order by ID

  - ##### Endpoint : `PUT` `/api/purchase_orders/{order_id}/`
  - ##### Tests :
    - Update with valid `order_id`, valid data and authorization.
    - Update with invalid data.
    - Update with invalid `order_id`.
    - Update with non-owner users.
    - Update with unauthorized users.

- #### Delete Purchase Order by ID

  - ##### Endpoint : `DELETE` `/api/purchase_orders/{order_id}/`
  - ##### Tests :
    - Delete with valid `order_id` and authorization.
    - Delete with invalid `order_id`.
    - Delete with non-owner users.
    - Delete with unauthorized users.

- #### Acknowledge Purchase Order by ID

  - ##### Endpoint : `POST` `/api/purchase_orders/{order_id}/acknowledge/`
  - ##### Tests :
    - Acknowledge with valid `order_id` and authorization.
    - Acknowledge with invalid `order_id`.
    - Acknowledge with non-owner users.
    - Acknowledge with unauthorized users.

---

### Signal Handler Test (Metrics Calculations)

To run real time metrics calulations (_signal handler_) related tests, execute the following command from the root directory:

```bash
python manage.py test --pattern="test_signals.py"
```

#### Test Cases

These test cases covers real time vendor performance metrics in various scenarious.

- #### Quality Rating Average

  - ##### Tests:
    - Quality rating of a purchase order gets updated in the intial state.
    - Quality rating of a already rated purchase order modifies again.
    - No quality rating presents in any purchase orders.
    - All the purchase orders have quality rating.
    - Purchase orders with mixed rated and non-rated .
    - Quality ratings average gets recalculate and update efficiently when any purchase order gets deleted.
    - Checking quality rating average calculate and updates at each point of the above scenarious.
    - Checking any other field updation is not affecting.

- #### On Time Delivery Rate

  - ##### Tests :
    - Delivery completed on or before delivery date.
    - Delivery completed after delivery date.
    - Accurate calculation if pending orders exists.
    - Accurate calculation if canceled orders exists.
    - Recalculate and update metrics if any of the completed purchase order gets deleted.
    - Checking any other field updations not affecting metrics.

- #### Fulfillment Rate

  - ##### Tests :
    - With completed deliveries.
    - With canceled deliveries.
    - Accurate calculation if pending orders exists.
    - Recalculate and update metrics if any of the non pending purchase orders gets deleted.
    - checking if any other field updations not affecting metrics.

- #### Average Response Time
  - ##### Tests :
    - Test with different response time.
    - Efficiently calcuate average response time when vendor acknowledge purchase order.
