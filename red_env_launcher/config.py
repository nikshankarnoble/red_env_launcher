import copy
import json
import os.path
from pathlib import Path

import yaml

DEFAULT_CONFIG_NAME = 'default'

EXCLUDE_TOKEN = '__exclude__'


def get_config_root_path() -> Path:
    """
    """
    return Path(__file__).parent.parent / 'config'


def apply_override(base_config: dict, override_config: dict) -> dict:
    new_config = copy.deepcopy(base_config)

    if '_resolve_settings' in new_config:
        new_config['_resolve_settings'].update(
            override_config.pop('_resolve_settings', {})
        )
    else:
        new_config['_resolve_settings'] = override_config.pop('_resolve_settings', {})

    for profile, profile_data in override_config.items():
        if profile not in new_config:
            new_config[profile] = profile_data
        else:
            package_overrides = profile_data.get('packages', {})
            new_config[profile]['packages'].update(package_overrides)

    return new_config


class EnvironmentConfig:
    def __init__(self, data: dict):
        self._data = data

        self._resolve_settings = self._data.pop('_resolve_settings', {})

        print('self._data', self._data)
        print('self._resolve_settings', self._resolve_settings)

    @classmethod
    def resolve_config(cls, config='default', project=None, department=None):
        """
        Resolves a configuration for the provided environment.

        Args:
            config (str):
            project (str):
            department (str):

        Returns:
            (EnvironmentConfig)
        """
        config_dir = get_config_root_path() / config

        default_config_path = config_dir / '_base.yml'
        if default_config_path.exists():
            with default_config_path.open() as fp:
                config = yaml.load(fp, Loader=yaml.Loader)
        else:
            config = {}

        show_config_path = config_dir / f'{project}.yml'
        if show_config_path.exists():
            with show_config_path.open() as fp:
                show_overrides = yaml.load(fp, Loader=yaml.Loader)
            config = apply_override(config, show_overrides)

        dept_config_path = config_dir / f'{project}_{department}.yml'
        if dept_config_path.exists():
            with dept_config_path.open() as fp:
                department_overrides = yaml.load(fp, Loader=yaml.Loader)
            config = apply_override(config, department_overrides)

        if not config:
            raise ValueError(
                f'No configuration defined for:'
                f'\t Config: {config}\n'
                f'\t Project: {project}\n'
                f'\t Department: {department}\n'
            )

        return cls(config)

    @classmethod
    def from_path(cls, config_path):
        """
        Returns an EnvironmentConfig object from a file on YAML or JSON file on
        disk.

        Args:
            config_path (str): the path to the JSON/YAML file.

        Returns:
            (EnvironmentConfig) a config object from the data in that file.
        """
        config_path = os.path.abspath(config_path)
        if not os.path.isfile(config_path):
            raise ValueError(f'Provided path is not a file: {config_path}.')

        if config_path.lower().endswith((".yaml", ".yml")):
            with open(config_path, 'r') as f:
                data = yaml.load(f, Loader=yaml.Loader)
                return cls(data)
        elif config_path.lower().endswith((".json")):
            with open(config_path, 'r') as f:
                data = json.load(f)
                return cls(data)
        else:
            raise ValueError(
                f'Unrecognised file type for {config_path}, please provide a '
                f'JSON or YAML file.'
            )

    def package_requests(self, profile):
        """
        Returns the list of Rez package requests for the provided profile.

        Args:
            profile (str): the name of the profile, e.g 'maya'.

        Returns:
            (list[str]) the Rez package requests for the profile.
        """
        packages_dict = self._data[profile].get('packages', {})
        requests = []
        for package, version in packages_dict.items():
            if version == EXCLUDE_TOKEN:
                continue

            if version.startswith(('==', '>', '<')):
                requests.append(package + version)
            elif version:
                requests.append(f"{package}-{version}")
            else:
                requests.append(package)

        return requests


if __name__ == '__main__':
    print('base')
    cfg = EnvironmentConfig.resolve_config()
    print(cfg.package_requests('maya'))
    print()

    print('show')
    cfg = EnvironmentConfig.resolve_config(project='testjob')
    print(cfg.package_requests('maya'))
    print()

    print('dept')
    cfg = EnvironmentConfig.resolve_config(project='testjob', department='model')
    print(cfg.package_requests('maya'))
    print()