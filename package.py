# -*- coding: utf-8 -*-

name = 'red_env_launcher'

version = '0.0.0'

requires = [
    '~python-3',
    'rez',
    'PyYAML',
]

build_requires = [
    'red_build_tools',
]

build_command = "python {root}/rezbuild.py install"

def commands():
    env.PATH.append("{root}/bin")
    env.PYTHONPATH.append("{root}")

