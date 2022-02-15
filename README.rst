pytest-bravado
==============

Pytest-bravado automatically generates client fixtures from OpenAPI specification.
`Bravado documentation <https://github.com/Yelp/bravado>`__.

Installation
-------------

To install pytest-bravado via pip run the following command:

.. code-block:: bash

    pip install pytest-bravado

Example Usage
-------------

**Simple tests:**

.. code-block:: Python

    import pytest

    @pytest.mark.parametrize('getUser', [{'id': 1}], indirect=True)
    def test_get_user(getUser):
        assert getUser.result


    @pytest.mark.parametrize('createUser', [{'id': 2, 'username': 'Ivan'}], indirect=True)
    def test_create_user(createUser, getUser):
        assert getUser(id=2).response().result

**Support openapi example:**

If there is an instance in the specifics, it will be used as the default request body.

.. code-block:: yaml

    parameters:
      - in: "body"
        name: "body"
        schema:
          $ref: "#/definitions/User"
        example:
          id: 10
          username: Oleg

.. code-block:: Python

    import pytest

    def test_create_user(createUser):
        assert createUser.response().result

*request body:*

.. code-block:: Python

    {'id': 10, 'username': 'Oleg'}

You can use mark parametrize to change all or part of the example.

.. code-block:: Python

    @pytest.mark.parametrize('createUser', [{'username': 'Ivan'}], indirect=True)
    def test_create_user(createUser):
        assert createUser.result

*request body:*

.. code-block:: Python

    {'id': 10, 'username': 'Ivan'}

**Run:**

.. code-block:: bash

    pytest --swagger_url http://user-service.com/swagger.json

**Spec example:**

.. code-block:: yaml

    swagger: "2.0"
    info:
      version: "1.0.0"
      title: "User service"
    host: "user-service.com"
    schemes:
    - "http"
    paths:
      /user{id}:
        get:
          operationId: "getUser"
          parameters:
          - in: "path"
            name: "id"
            required: true
            type: "integer"
          responses:
            default:
              description: "successful"
              schema:
                $ref: "#/definitions/User"
      /createUser:
        post:
          operationId: "createUser"
          produces:
          - "application/json"
          parameters:
          - in: "body"
            name: "body"
            schema:
              $ref: "#/definitions/User"
            example:
              id: 10
              username: Oleg
          responses:
            default:
              description: "successful"
    definitions:
      User:
        type: "object"
        properties:
          id:
            type: "integer"
          username:
            type: "string"

The following flags are supported
----------------------------------

- `--swagger_url` - openapi spec url
- `--request_headers` - request headers
- `--not_validate_responses` - not validate incoming responses
- `--not_validate_requests` - not validate outgoing requests
- `--not_validate_swagger_spec` - not validate the swagger spec
- `--not_use_models` - not use models (Python classes) instead of dicts for #/definitions/{models}
- `--enable_fallback_results` - use fallback results even if they're provided
- `--response_metadata_class` - What class to use for response metadata