pytest-bravado
==============

Pytest-bravado automatically generates client fixtures from OpenAPI specification.
Using `Bravado <https://github.com/Yelp/bravado>`__.

Installation
-------------

To install pytest-bravado via pip run the following command:

.. code-block:: bash

    pip install pytest-bravado

Example Usage
-------------

Your test:

.. code-block:: Python

    import pytest

    @pytest.mark.parametrize('body', [{'id': '1', 'username': 'Ivan'}])
    def test(createUser):
        assert createUser.response().result

Run:

.. code-block:: bash

    pytest --swagger_url http://user-service.com/swagger.json

Spec example:

.. code-block:: yaml

    swagger: "2.0"
    info:
      version: "1.0.0"
      title: "User service"
    host: "user-service.com"
    schemes:
    - "http"
    paths:
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
          responses:
            default:
              description: "successful"
    definitions:
      User:
        type: "object"
        properties:
          id:
            type: "integer"
            format: "int64"
          username:
            type: "string"