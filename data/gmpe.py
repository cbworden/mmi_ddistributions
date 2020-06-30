#!/usr/bin/env python

import os
from configobj import ConfigObj

from shakemap.utils.config import (
    get_config_paths, get_configspec, get_custom_validator)
from shakelib.multigmpe import MultiGMPE


def ngaw2():
    shake_conf = get_shake_conf()
    return MultiGMPE.from_config(shake_conf)


def get_shake_conf():
    """
    Get the shakemap global conf dictionary.
    """
    install_path, _ = get_config_paths()
    spec_file = get_configspec()
    validator = get_custom_validator()
    modules = ConfigObj(
        os.path.join(install_path, 'config', 'modules.conf'),
        configspec=spec_file)
    gmpe_sets = ConfigObj(
        os.path.join(install_path, 'config', 'gmpe_sets.conf'),
        configspec=spec_file)
    global_config = ConfigObj(
        os.path.join(install_path, 'config', 'model.conf'),
        configspec=spec_file)
    global_config.merge(modules)
    global_config.merge(gmpe_sets)
    results = global_config.validate(validator)
    return global_config
