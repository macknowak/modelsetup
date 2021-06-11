"""Utility supporting initial model setup.

ModelSetup is a Python utility that supports an initial setup of a
computational model that may utilize spiking neural networks implemented using
Nengo and the robot simulator V-REP.
"""

__version__ = '0.1.0.dev1'
__author__ = "Przemyslaw (Mack) Nowak"

import collections
import configparser


def parse_config(filename):
    """Parse configuration file."""
    parser = configparser.ConfigParser()
    parser.read(filename)
    cfg = {}
    venv_dirname = parser.get('VirtualEnv', 'Directory')
    if venv_dirname:
        cfg['venv_dirname'] = venv_dirname
    else:
        raise ValueError("empty option: 'Directory'")
    cfg['venv_python_exec'] = parser.get('VirtualEnv', 'Interpreter')
    cfg['venv_system_site_packages'] = parser.getboolean('VirtualEnv',
                                                         'SystemSitePackages')
    cfg['use_requirements_file'] = not parser.getboolean(
        'Dependencies', 'OverrideRequirementsFile')
    deps = collections.OrderedDict()
    if not cfg['use_requirements_file']:
        simtools_spec = parser.get('Dependencies', 'SimTools')
        if simtools_spec:
            deps['simtools'] = simtools_spec
        vrepsim_spec = parser.get('Dependencies', 'VRepSim')
        if vrepsim_spec:
            deps['vrepsim'] = vrepsim_spec
        nengo_spec = parser.get('Dependencies', 'Nengo')
        if nengo_spec:
            deps['nengo'] = nengo_spec
    nengo_gui_spec = parser.get('OptionalDependencies', 'NengoGui')
    if nengo_gui_spec:
        deps['nengo_gui'] = nengo_gui_spec
    cfg['deps'] = deps
    cfg['vrep_dirname'] = parser.get('VRep', 'Directory')
    cfg['create_simulations_dir'] = parser.getboolean(
        'ExtraDirectoriesAndFiles', 'CreateSimulationsDir')
    cfg['create_setup_file'] = parser.getboolean('ExtraDirectoriesAndFiles',
                                                 'CreateSetupFile')
    return cfg
