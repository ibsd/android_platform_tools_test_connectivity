# Copyright 2016 - The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class SshSettings(object):
    """Contains settings for ssh.

    Container for ssh connection settings.

    Attributes:
        username: The name of the user to log in as.
        hostname: The name of the host to connect to.
        executable: The ssh executable to use.
        port: The port to connect through (usually 22).
        host_file: The known host file to use.
        connect_timeout: How long to wait on a connection before giving a
                         timeout.
        alive_interval: How long between ssh heartbeat signals to keep the
                        connection alive.
    """

    def __init__(self,
                 hostname,
                 username,
                 port=22,
                 host_file='/dev/null',
                 connect_timeout=30,
                 alive_interval=300,
                 executable='ssh'):
        self.username = username
        self.hostname = hostname
        self.executable = executable
        self.port = port
        self.host_file = host_file
        self.connect_timeout = connect_timeout
        self.alive_interval = alive_interval

    def construct_ssh_options(self):
        """Construct the ssh options.

        Constructs a dictionary of option that should be used with the ssh
        command.

        Returns:
            A dictionary of option name to value.
        """
        current_options = {}
        current_options['StrictHostKeyChecking'] = False
        current_options['UserKnownHostsFile'] = self.host_file
        current_options['ConnectTimeout'] = self.connect_timeout
        current_options['ServerAliveInterval'] = self.alive_interval
        return current_options

    def construct_ssh_flags(self):
        """Construct the ssh flags.

        Constructs what flags should be used in the ssh connection.

        Returns:
            A dictonary of flag name to value. If value is none then it is
            treated as a binary flag.
        """
        current_flags = {}
        current_flags['-a'] = None
        current_flags['-x'] = None
        current_flags['-p'] = self.port
        return current_flags
