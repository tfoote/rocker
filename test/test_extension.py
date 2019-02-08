# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import em
import getpass
import os
import unittest
from pathlib import Path


from rocker.cli import list_plugins
from rocker.extensions import name_to_argument

class ExtensionsTest(unittest.TestCase):
    def test_name_to_argument(self):
        self.assertEqual(name_to_argument('asdf'), '--asdf')
        self.assertEqual(name_to_argument('as_df'), '--as-df')
        self.assertEqual(name_to_argument('as-df'), '--as-df')

class HomeExtensionTest(unittest.TestCase):

    def setUp(self):
        # Work around interference between empy Interpreter
        # stdout proxy and test runner. empy installs a proxy on stdout
        # to be able to capture the information.
        # And the test runner creates a new stdout object for each test.
        # This breaks empy as it assumes that the proxy has persistent
        # between instances of the Interpreter class
        # empy will error with the exception
        # "em.Error: interpreter stdout proxy lost"
        em.Interpreter._wasProxyInstalled = False

    def test_home_extension(self):
        plugins = list_plugins()
        home_plugin = plugins['home']
        self.assertEqual(home_plugin.get_name(), 'home')

        p = home_plugin()
        
        mock_cliargs = {}
        self.assertEqual(p.get_snippet(mock_cliargs), '')
        self.assertEqual(p.get_preamble(mock_cliargs), '')
        args = p.get_docker_args(mock_cliargs)
        self.assertTrue('-v %s:%s' % (Path.home(), Path.home()) in args)


class UserExtensionTest(unittest.TestCase):

    def setUp(self):
        # Work around interference between empy Interpreter
        # stdout proxy and test runner. empy installs a proxy on stdout
        # to be able to capture the information.
        # And the test runner creates a new stdout object for each test.
        # This breaks empy as it assumes that the proxy has persistent
        # between instances of the Interpreter class
        # empy will error with the exception
        # "em.Error: interpreter stdout proxy lost"
        em.Interpreter._wasProxyInstalled = False

    def test_user_extension(self):
        plugins = list_plugins()
        user_plugin = plugins['user']
        self.assertEqual(user_plugin.get_name(), 'user')

        p = user_plugin()

        env_subs = p.get_environment_subs()
        self.assertEqual(env_subs['user_id'], os.getuid())
        self.assertEqual(env_subs['username'],  getpass.getuser())

        mock_cliargs = {}
        snippet = p.get_snippet(mock_cliargs).splitlines()

        passwd_line = [l for l in snippet if 'chpasswd' in l][0]
        self.assertTrue(getpass.getuser() in passwd_line)

        uid_line = [l for l in snippet if '--uid' in l][0]
        self.assertTrue(str(os.getuid()) in uid_line)

        self.assertEqual(p.get_preamble(mock_cliargs), '')
        self.assertEqual(p.get_docker_args(mock_cliargs), '')


EXPECTED_PULSE_SNIPPET = """RUN mkdir -p /etc/pulse
RUN echo '\\n\\
# Connect to the hosts server using the mounted UNIX socket\\n\\
default-server = unix:/run/user/1000/pulse/native\\n\\
\\n\\
# Prevent a server running in the container\\n\\
autospawn = no\\n\\
daemon-binary = /bin/true\\n\\
\\n\\
# Prevent the use of shared memory\\n\\
enable-shm = false\\n\\
\\n'\\
> /etc/pulse/client.conf
"""

class PulseExtensionTest(unittest.TestCase):

    def setUp(self):
        # Work around interference between empy Interpreter
        # stdout proxy and test runner. empy installs a proxy on stdout
        # to be able to capture the information.
        # And the test runner creates a new stdout object for each test.
        # This breaks empy as it assumes that the proxy has persistent
        # between instances of the Interpreter class
        # empy will error with the exception
        # "em.Error: interpreter stdout proxy lost"
        em.Interpreter._wasProxyInstalled = False

    def test_pulse_extension(self):
        plugins = list_plugins()
        pulse_plugin = plugins['pulse']
        self.assertEqual(pulse_plugin.get_name(), 'pulse')

        p = pulse_plugin()
        
        mock_cliargs = {}

        self.assertEqual(p.get_snippet(mock_cliargs), EXPECTED_PULSE_SNIPPET)
        self.assertEqual(p.get_preamble(mock_cliargs), '')

EXPECTED_DEV_HELPERS_SNIPPET = """# workspace development helpers
RUN apt-get update \\
 && apt-get install -y \\
    byobu \\
    emacs \\
 && apt-get clean
"""

class DevHelpersExtensionTest(unittest.TestCase):

    def setUp(self):
        # Work around interference between empy Interpreter
        # stdout proxy and test runner. empy installs a proxy on stdout
        # to be able to capture the information.
        # And the test runner creates a new stdout object for each test.
        # This breaks empy as it assumes that the proxy has persistent
        # between instances of the Interpreter class
        # empy will error with the exception
        # "em.Error: interpreter stdout proxy lost"
        em.Interpreter._wasProxyInstalled = False

    def test_pulse_extension(self):
        plugins = list_plugins()
        pulse_plugin = plugins['dev_helpers']
        self.assertEqual(pulse_plugin.get_name(), 'dev_helpers')

        p = pulse_plugin()
        
        mock_cliargs = {}

        self.assertEqual(p.get_snippet(mock_cliargs), EXPECTED_DEV_HELPERS_SNIPPET)
        self.assertEqual(p.get_preamble(mock_cliargs), '')