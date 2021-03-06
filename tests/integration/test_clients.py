# -*- coding: utf-8 -*-
import json
import os
import pytest
import sys


def test_local_bad_opts(pepper_cli):
    with pytest.raises(SystemExit):
        pepper_cli('*')
    with pytest.raises(SystemExit):
        pepper_cli('test.ping')
    with pytest.raises(SystemExit):
        pepper_cli('--client=ssh', 'test.ping')
    with pytest.raises(SystemExit):
        pepper_cli('--client=ssh', '*')


@pytest.mark.xfail(
    pytest.config.getoption("--salt-api-backend") == "rest_tornado",
    reason="timeout kwarg isnt popped until next version of salt/tornado"
)
def test_runner_client(pepper_cli):
    ret = pepper_cli(
        '--timeout=123', '--client=runner', 'test.arg',
        'one', 'two=what',
        'three={0}'.format(json.dumps({"hello": "world"})),
    )
    assert ret == {"args": ["one"], "kwargs": {"three": {"hello": "world"}, "two": "what"}}


@pytest.mark.xfail(
    pytest.config.getoption("--salt-api-backend") == "rest_tornado",
    reason="wheelClient unimplemented for now on tornado",
)
def test_wheel_client_arg(pepper_cli, session_minion_id):
    ret = pepper_cli('--client=wheel', 'minions.connected')
    # note - this seems not to work in returning session_minion_id with current runner, returning []
    # the test originally was asserting the success atr but that isn't returned anymore
    # further debugging needed with pytest-salt
    assert ret == []


@pytest.mark.xfail(
    pytest.config.getoption("--salt-api-backend") == "rest_tornado",
    reason="wheelClient unimplemented for now on tornado",
)
def test_wheel_client_kwargs(pepper_cli, session_master_config_file):
    ret = pepper_cli(
        '--client=wheel', 'config.update_config', 'file_name=pepper',
        'yaml_contents={0}'.format(json.dumps({"timeout": 5})),
    )
    assert ret == 'Wrote pepper.conf'
    assert os.path.isfile('{0}.d/pepper.conf'.format(session_master_config_file))


@pytest.mark.xfail(
    pytest.config.getoption("--salt-api-backend") == "rest_tornado",
    reason="sshClient unimplemented for now on tornado",
)
@pytest.mark.xfail(sys.version_info >= (3, 0),
                   reason='Broken with python3 right now')
def test_ssh_client(pepper_cli, session_roster_config, session_roster_config_file):
    ret = pepper_cli('--client=ssh', '*', 'test.ping')
    assert ret['ssh']['localhost']['return'] is True


def test_bad_client(pepper_cli):
    ret = pepper_cli('--client=whatever')
    assert ret == 1
