import json
from operator import attrgetter
from pathlib import Path

import pytest
from bravado.client import SwaggerClient
from nested_lookup import nested_update, nested_lookup


def pytest_addoption(parser):
    group = parser.getgroup('bravado')
    group.addoption('--swagger_url',
                    action="append",
                    default=[],
                    dest="swagger_url",
                    help="Openapi spec url")

    group.addoption('--request_headers',
                    action="store",
                    default="{}",
                    type=str,
                    dest="request_headers",
                    help="Request headers")

    group.addoption('--response_metadata_class',
                    action="store",
                    default='bravado.response.BravadoResponseMetadata',
                    dest="response_metadata_class",
                    help="What class to use for response metadata")

    group.addoption('--enable_fallback_results',
                    action="store_true",
                    default=False,
                    dest="disable_fallback_results",
                    help="Use fallback results even if they're provided")

    group.addoption('--not_validate_responses',
                    action="store_false",
                    default=True,
                    dest="validate_responses",
                    help="Validate incoming responses")

    group.addoption("--not_validate_requests",
                    action="store_false",
                    default=True,
                    dest="validate_requests",
                    help="Validate outgoing requests")

    group.addoption('--not_validate_swagger_spec',
                    action="store_false",
                    default=True,
                    dest="validate_swagger_spec",
                    help="Validate the swagger spec")

    group.addoption('--not_use_models',
                    action="store_false",
                    default=True,
                    dest="use_models",
                    help="Use models (Python classes) instead of dicts for #/definitions/{models}")


def pytest_configure(config):
    if config.getoption('swagger_url'):
        headers = config.getoption('request_headers')
        bravado_config = {
            'response_metadata_class': config.getoption('response_metadata_class'),
            'disable_fallback_results': config.getoption('disable_fallback_results'),
            'validate_responses': config.getoption('validate_responses'),
            'validate_requests': config.getoption('validate_requests'),
            'validate_swagger_spec': config.getoption('validate_swagger_spec'),
            'use_models': config.getoption('use_models')
        }
        for spec in config.getoption('swagger_url'):
            create(SwaggerClient.from_url(
                spec,
                request_headers=json.loads(headers),
                config=bravado_config
                )
             )


def get_request_example(resource):
    for param in resource.operation.params.values():
        if 'schema' not in param.param_spec:
            return nested_lookup('example', param.param_spec)
        definition_name = Path(param.param_spec['schema']['$ref']).name
        deref = resource.operation.swagger_spec.deref_flattened_spec['definitions'].get(definition_name)
        return nested_lookup('example', deref)


def update_body(body, param):
    if param:
        for k, v in param.items():
            del param[k]
            return update_body(nested_update(body, k, v), param)
    return body


def create(client):
    for resource in attrgetter(*dir(client))(client):
        for path in dir(resource):
            operation = getattr(resource, path)
            globals()[path] = generate_fixtures(operation, get_request_example(operation))


def generate_fixtures(resource, example):
    @pytest.fixture()
    def _fixture(request):
        if body := getattr(request, 'param', []):
            if example:
                body = update_body(example, body)
            response = resource(body=body[0]).response()
            response.request_body = response.metadata.incoming_response._delegate.request.body
            return response
        if example:
            return resource(body=example[0])
        return resource
    return _fixture
