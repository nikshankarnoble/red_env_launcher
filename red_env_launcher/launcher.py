import os
import shlex
import subprocess
import sys

from rez.config import config as rezconfig
from rez.resolved_context import ResolvedContext, ResolverStatus

from red_env_launcher import config as envconfig


def get_default_env_config():
    return envconfig.resolve_config(
        show_name=os.getenv('JOB'),  # TODO: Check variable names
        department=os.getenv('DEPARTMENT'),
    )


class EnvLauncher:
    def __init__(
            self,
            profile,
            local_packages=False,
            extra_package_paths=None,
            patch_packages=None,
            timestamp=None,
            config=None,
    ):
        self._profile = profile
        self._use_local_packages = local_packages
        self._extra_package_paths = extra_package_paths
        self._patch_packages = patch_packages
        self._resolve_timestamp = timestamp
        self._env_config = config or get_default_env_config()

        self._context = self._resolve_rez_context()

    def _resolve_rez_context(self):
        # timestamp = self._resolve_timestamp or self._resolver_config.resolve_timestamp()
        package_list = envconfig.get_package_requests(self._env_config, self._profile)
        print(package_list)

        # Package paths.
        package_paths = rezconfig.nonlocal_packages_path
        if self._use_local_packages:
            package_paths.insert(0, rezconfig.local_packages_path)
        if self._extra_package_paths:
            package_paths.extend(self._extra_package_paths)

        # Resolve the base context.
        context = ResolvedContext(
            package_list,
            # timestamp=timestamp,
            package_paths=package_paths,
        )

        if context.status_ == ResolverStatus.failed:
            context.print_info(verbosity=True)
            raise ValueError('Context failed to resolve.')

        if self._patch_packages:
            patched_context = context.get_patched_request(
                self._patch_packages, strict=True
            )

            # Re-resolve with testing and local paths available.
            test_packages_path = os.getenv('RED_TESTING_PACKAGES_PATH')
            if test_packages_path:
                package_paths.insert(0, test_packages_path)

            package_paths.insert(0, rezconfig.local_packages_path)

            context = ResolvedContext(patched_context, package_paths=package_paths)

        return context

    def parent_environ(self):
        return os.environ.copy()

    def context(self):
        return self._context

    def popen(self, command, suppress_rez_msg=True, **kwargs):
        if isinstance(command, str):
            command = shlex.split(command)
        parent_environment = self.parent_environ()

        return self._context.execute_shell(
            command=command,
            parent_environ=parent_environment,
            block=False,
            quiet=suppress_rez_msg,
            **kwargs,
        )

    def run(self, command, stdout_stream=sys.stdout, **kwargs):
        process = self.popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            errors='replace',
            **kwargs,
        )

        stdout_capture = ''
        for line in iter(process.stdout.readline, ""):
            if stdout_stream:
                stdout_stream.write(line)
            stdout_capture += line

        process.wait()
        return subprocess.CompletedProcess(command, process.returncode, stdout_capture)


if __name__ == '__main__':
    # Example
    launcher = EnvLauncher('ipython', local_packages=True)
    launcher.run(['ipython', '--help'])
    launcher.context().print_info()