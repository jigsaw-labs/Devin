import copy
import json
import os
from abc import ABC, abstractmethod

from opendevin.core.config import SandboxConfig
from opendevin.core.schema import CancellableStream
from opendevin.runtime.plugins.mixin import PluginMixin


class Sandbox(ABC, PluginMixin):
    _env: dict[str, str] = {}
    is_initial_session: bool = True

    def __init__(self, config: SandboxConfig):
        self.config = copy.deepcopy(config)
        for key in os.environ:
            if key.startswith('SANDBOX_ENV_'):
                sandbox_key = key.removeprefix('SANDBOX_ENV_')
                self.add_to_env(sandbox_key, os.environ[key])
        if config.enable_auto_lint:
            self.add_to_env('ENABLE_AUTO_LINT', 'true')
        self.initialize_plugins: bool = config.initialize_plugins

    def add_to_env(self, key: str, value: str):
        self._env[key] = value
        # Note: json.dumps gives us nice escaping for free
        self.execute(f'export {key}={json.dumps(value)}')

    @abstractmethod
    def execute(
        self, cmd: str, stream: bool = False, timeout: int | None = None
    ) -> tuple[int, str | CancellableStream]:
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def copy_to(self, host_src: str, sandbox_dest: str, recursive: bool = False):
        pass

    @abstractmethod
    def get_working_directory(self):
        pass
