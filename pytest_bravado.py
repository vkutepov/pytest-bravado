import json
from operator import attrgetter

import pytest
from bravado.client import SwaggerClient


def pytest_addoption(parser):
    group = parser.getgroup('bravado')
    group.addoption('--swagger_url',
                    action="append",
                    default=[],
                    dest="swagger_url",
                    help="Openapi spec file path or url")

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
                    help="Do not use fallback results even if they're provided")

    group.addoption('--not_return_response',
                    action="store_true",
                    default=False,
                    dest="also_return_response",
                    help="Please use HttpFuture.response() for accessing the http response")

    group.addoption('--not_validate_responses',
                    action="store_false",
                    default=True,
                    dest="validate_responses",
                    help="Validate incoming responses")

    group.addoption("--not_validate_requests",
                    action="store_false",
                    default=True,
                    dest="validate_requests",
                    help="Validate outgoing requests", )

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
            'also_return_response': config.getoption('also_return_response'),
            'validate_responses': config.getoption('validate_responses'),
            'validate_requests': config.getoption('validate_requests'),
            'validate_swagger_spec': config.getoption('validate_swagger_spec'),
            'use_models': config.getoption('use_models')
        }
        for spec in config.getoption('swagger_url'):
            create(
                SwaggerClient.from_url(
                    spec,
                    request_headers=json.loads(headers),
                    config=bravado_config
                )
            )


def create(client):
    for resource in attrgetter(*dir(client))(client):
        for path in dir(resource):
            globals()[path] = generate_fixtures(getattr(resource, path))


def generate_fixtures(path):
    @pytest.fixture()
    def _fixture(request):
        return path(body=request.param)
    return _fixture
