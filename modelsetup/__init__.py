"""Utility supporting initial model setup.

ModelSetup is a Python utility that supports an initial setup of a
computational model that may utilize spiking neural networks implemented using
Nengo and the robot simulator V-REP.
"""

__version__ = '0.1.0.dev1'
__author__ = "Przemyslaw (Mack) Nowak"

import collections
import configparser
import os
import re


def get_vrep_version(vrep_dirname):
    """Determine V-REP version."""
    try:
        with open(os.path.join(vrep_dirname, "readme.txt")) as readme_file:
            line = readme_file.readline()
        return re.search("release V([0-9]+\.[0-9]+\.[0-9]+)", line).group(1)
    except Exception:
        return "Unknown"


def make_setup_file_bash(filename, venv_bin_dirpath, vrep_dirname, sys_name):
    """Create setup file for Bash."""
    venv_activate_script = os.path.join(venv_bin_dirpath, "activate")
    if sys_name == "Mac":
        vrep_alias = "open '$VREP_EXEC' --args"
        if vrep_dirname:
            vrep_exec = os.path.join(vrep_dirname, "vrep.app")
        else:
            vrep_exec = ""
    else:
        vrep_alias = "'$VREP_EXEC'"
        if vrep_dirname:
            vrep_exec = os.path.join(vrep_dirname, "vrep.sh")
        else:
            vrep_exec = ""
    file_contents = (
"""# ------
# Config
# ------

# Virtual environment
VENV_ACTIVATE_SCRIPT="__VENV_ACTIVATE_SCRIPT__"

# V-REP
VREP_EXEC="__VREP_EXEC__"

# Python
EXTRA_PYTHONPATH=""

# Computational context
PYOPENCL_CTX=""


# -----
# Setup
# -----

cleanup() {
    unset VENV_ACTIVATE_SCRIPT
    unset VREP_EXEC
    unset EXTRA_PYTHONPATH
    if [ -z "$PYOPENCL_CTX" ]; then
        unset PYOPENCL_CTX
    fi
}

setup() {
    # Activate model virtual environment
    if [ -z "$VENV_ACTIVATE_SCRIPT" ]; then
        echo 'Error: empty VENV_ACTIVATE_SCRIPT.' >&2
        return 1
    fi
    source "$VENV_ACTIVATE_SCRIPT"
    if [ $? -ne 0 ]; then
        echo 'Error: virtual environment not activated.' >&2
        return 1
    fi

    # Make alias for launching V-REP
    if [ -n "$VREP_EXEC" ]; then
        alias vrep="__VREP_ALIAS__"
    fi

    # Add directories to be searched for Python module files
    if [ -n "$EXTRA_PYTHONPATH" ]; then
        export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$EXTRA_PYTHONPATH"
    fi

    # Export environment variable describing computational context
    if [ -n "$PYOPENCL_CTX" ]; then
        export PYOPENCL_CTX
    fi

    return 0
}

setup
if [ $? -eq 0 ]; then
    cleanup
    return 0
else
    cleanup
    return 1
fi
""")
    file_contents = file_contents.replace("__VENV_ACTIVATE_SCRIPT__",
                                          venv_activate_script)
    file_contents = file_contents.replace("__VREP_EXEC__", vrep_exec)
    file_contents = file_contents.replace("__VREP_ALIAS__", vrep_alias)
    with open(filename, 'x') as setup_file:
        setup_file.write(file_contents)


def make_setup_file_cmd(filename, venv_bin_dirpath, vrep_dirname):
    """Create setup file for Windows command line."""
    venv_activate_script = os.path.join(venv_bin_dirpath, "activate.bat")
    vrep_exec = os.path.join(vrep_dirname, "vrep.exe") if vrep_dirname else ""
    file_contents = (
"""@echo off

rem ------
rem Config
rem ------

rem Virtual environment
set "VENV_ACTIVATE_SCRIPT=__VENV_ACTIVATE_SCRIPT__"

rem V-REP
set "VREP_EXEC=__VREP_EXEC__"

rem Python
set "EXTRA_PYTHONPATH="

rem Computational context
set "PYOPENCL_CTX="


rem -----
rem Setup
rem -----

rem Activate model virtual environment
if not defined VENV_ACTIVATE_SCRIPT (
    echo Error: empty VENV_ACTIVATE_SCRIPT. 1>&2
    set SETUP_ERR=1
    goto cleanup
)
call "%VENV_ACTIVATE_SCRIPT%"
if %ERRORLEVEL% neq 0 (
    echo Error: virtual environment not activated. 1>&2
    set SETUP_ERR=1
    goto cleanup
)

rem Make alias for launching V-REP
if defined VREP_EXEC doskey vrep="%VREP_EXEC%" $*

rem Add directories to be searched for Python module files
if defined EXTRA_PYTHONPATH (
    if defined PYTHONPATH set "PYTHONPATH=%EXTRA_PYTHONPATH%;%PYTHONPATH%"
    if not defined PYTHONPATH set "PYTHONPATH=%EXTRA_PYTHONPATH%"
)

:cleanup
set "VENV_ACTIVATE_SCRIPT="
set "VREP_EXEC="
set "EXTRA_PYTHONPATH="

if defined SETUP_ERR (
    set "SETUP_ERR="
    exit /b 1
)
exit /b 0
""")
    file_contents = file_contents.replace("__VENV_ACTIVATE_SCRIPT__",
                                          venv_activate_script)
    file_contents = file_contents.replace("__VREP_EXEC__", vrep_exec)
    with open(filename, 'x') as setup_file:
        setup_file.write(file_contents)


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
