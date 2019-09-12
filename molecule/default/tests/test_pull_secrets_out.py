import json

import pytest

# Loading the pull secrets should be a fixture, but the expected_auth_keys test
# needs to be parametrized on hostnames so that when a host fails (or if
# *all* hosts fail), it's easy to see what happened. That means that instead
# of having a test to assert against the loadability of the pull secrets,
# this json.load will just explode in collection if the output file is either
# not written or invalid json.
try:
    with open('pull_secrets_output.json') as pull_secrets:
        pull_secrets = json.load(pull_secrets)
except Exception as exc:
    # this suppresses the huge "INTERNALERROR" traceback that happens if/when
    # the json.load fails and reduces it to a concise actionable error
    pytest.fail(str(exc))


def test_injected_auths():
    # check that the example.com auth exists and has the correct values
    assert pull_secrets['auths']['example.com']
    assert pull_secrets['auths']['example.com']['email'] == 'user@example.com'
    assert pull_secrets['auths']['example.com']['auth'] == 'testing_auth_key'


@pytest.mark.parametrize('auth', pull_secrets['auths'].values(),
                         ids=pull_secrets['auths'].keys())
def test_expected_auth_keys(auth):
    # check that every auth key has the expected keys
    assert auth.get('email')
    assert auth.get('auth')
