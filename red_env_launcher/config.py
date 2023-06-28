import copy
from pathlib import Path

import yaml

DEFAULT_CONFIG_NAME = 'default'


def get_config_root_path() -> Path:
    """
    """
    return Path(__file__).parent.parent / 'config'


def resolve_config(config_name='default', show_name=None, department=None):
    config_dir = get_config_root_path() / config_name
    default_config_path = config_dir / '_base.yml'
    if not default_config_path.exists():
        raise ValueError(f'Base configuration not found at {default_config_path.as_posix()}')

    config = yaml.load(default_config_path.open(), Loader=yaml.Loader)

    show_config_path = config_dir / f'{show_name}.yml'
    if show_config_path.exists():
        config = apply_overrides(config, yaml.load(show_config_path.open(), Loader=yaml.Loader))

    dept_config_path = config_dir / f'{show_name}_{department}.yml'
    if dept_config_path.exists():
        config = apply_overrides(config, yaml.load(dept_config_path.open(), Loader=yaml.Loader))

    return config


def apply_overrides(base_config: dict, overrides: dict) -> dict:
    new_config = copy.deepcopy(base_config)

    for profile, profile_data in overrides.items():
        if profile not in new_config:
            new_config[profile] = profile_data
        else:
            package_overrides = profile_data.get('packages', {})
            new_config[profile]['packages'].update(package_overrides)

    return new_config


def get_package_requests(config, profile):
    packages_dict = config[profile].get('packages', {})
    requests = []
    for package, version in packages_dict.items():
        if version.startswith(('==', '>', '<')):
            requests.append(package + version)
        elif version:
            requests.append(f"{package}-{version}")
        else:
            requests.append(package)

    return requests


if __name__ == '__main__':
    from pprint import pprint
    print('base')
    pprint(resolve_config())
    print()

    print('show')
    pprint(resolve_config(show_name='testjob'))
    print()

    print('dept')
    pprint(resolve_config(show_name='testjob', department='model'))
    print()