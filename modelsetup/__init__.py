"""Utility supporting initial model setup.

ModelSetup is a Python utility that supports an initial setup of a
computational model that may utilize spiking neural networks implemented using
Nengo and the robot simulator V-REP.
"""

__version__ = '0.2.0.dev1'
__author__ = "Przemyslaw (Mack) Nowak"

import argparse
import collections
import configparser
import errno
import functools
import os
import re
import shutil
import subprocess
import sys


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


def parse_args(args=None):
    """Parse command line arguments."""

    def file_r_type(filename):
        """Check if file exists and is readable."""
        if not os.path.isfile(filename):
            raise argparse.ArgumentTypeError(f"no such file: '{filename}'")
        if not os.access(filename, os.R_OK):
            raise argparse.ArgumentTypeError(f"permission denied: "
                                             f"'{filename}'")
        return filename

    parser = argparse.ArgumentParser(description="Set up model.")
    parser.add_argument(
        "--use-virtualenv",
        dest='use_virtualenv', action='store_true',
        help="use third-party package 'virtualenv' instead of package 'venv' "
             "from the standard library")
    parser.add_argument(
        "config_filename", metavar="CONFIGFILE",
        type=file_r_type,
        help="config file")
    args = parser.parse_args(args)
    return args


def main(args=None):
    prog_name = os.path.basename(sys.argv[0])
    n_warnings = 0

    def warn(warning):
        """Display warning and count it."""
        nonlocal n_warnings
        print(f"[{prog_name}] Warning:", warning, file=sys.stderr)
        n_warnings += 1

    # Process command line arguments
    args = parse_args(args)

    print("*** Configuration ***")

    # Determine configuration
    cfg = parse_config(args.config_filename)

    # Import appropriate package for creating virtual environments
    if args.use_virtualenv:
        try:
            import virtualenv
        except ImportError:
            raise ImportError(
                "Third-party package 'virtualenv' was requested to be used "
                "for creating a virtual environment, but it is not installed; "
                "please install it and try again.") from None
        use_virtualenv_pkg = True
    elif cfg['venv_python_exec']:
        try:
            import virtualenv
        except ImportError:
            raise ImportError(
                "If a specific Python interpreter is required, third-party "
                "package 'virtualenv' is required to create a virtual "
                "environment, but it is not installed; please install it and "
                "try again.") from None
        use_virtualenv_pkg = True
    else:
        import venv
        use_virtualenv_pkg = False

    # Check if virtual environment already exists
    if os.path.isdir(cfg['venv_dirname']):
        raise OSError(errno.EEXIST, "Directory exists", cfg['venv_dirname'])

    # Determine Python version and bit architecture
    if not cfg['venv_python_exec']:
        python_ver = ".".join(map(str, sys.version_info[0:2]))
        python_bit_arch = 64 if sys.maxsize > 2**32 else 32
    else:
        py_cmd = ('import sys; '
                  'print(".".join(map(str, sys.version_info[0:2]))); '
                  'print(64 if sys.maxsize > 2**32 else 32)')
        try:
            proc_info = subprocess.run([cfg['venv_python_exec'], "-c", py_cmd],
                                       stdout=subprocess.PIPE, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise ValueError(f"invalid Python interpreter: "
                             f"'{cfg['venv_python_exec']}'") from None
        python_ver, python_bit_arch = \
            proc_info.stdout.decode('utf-8').splitlines()

    # Determine operating system
    if sys.platform.startswith('win'):
        sys_name = "Windows"
        lib_ext = "dll"
        venv_bin_dirpath = os.path.join(cfg['venv_dirname'], "Scripts")
        venv_pkg_dirpath = os.path.join(cfg['venv_dirname'], "Lib",
                                        "site-packages")
    else:
        if sys.platform.startswith('darwin'):
            sys_name = "Mac"
            lib_ext = "dylib"
        else:
            sys_name = "Linux"
            lib_ext = "so"
        venv_bin_dirpath = os.path.join(cfg['venv_dirname'], "bin")
        venv_pkg_dirpath = os.path.join(cfg['venv_dirname'], "lib",
                                        f"python{python_ver}", "site-packages")

    # If necessary, determine V-REP version
    if cfg['vrep_dirname']:
        if not os.path.isdir(cfg['vrep_dirname']):
            raise ValueError(f"invalid V-REP directory: "
                             f"'{cfg['vrep_dirname']}'")
        vrep_version = get_vrep_version(cfg['vrep_dirname'])

    # Confirm configuration
    print("Directory:\t", cfg['venv_dirname'])
    print("System:\t\t", sys_name)
    print("Python:\t\t", python_ver, f"{python_bit_arch}-bit")
    if cfg['use_requirements_file']:
        print("Dependencies:\t requirements.txt")
    else:
        print("Dependencies:\t", args.config_filename)
    print("V-REP:\t\t", vrep_version if cfg['vrep_dirname'] else "-")
    print("Creator:\t", "venv" if not use_virtualenv_pkg else "virtualenv")
    print()
    while True:
        response = input("Proceed ([y]/n)? ").lower()
        if response in ("", "y", "yes"):
            break
        elif response in ("n", "no"):
            return 1

    print("*** Creating virtual environment ***")

    # Create virtual environment
    if not use_virtualenv_pkg:
        print("Running venv")
        if cfg['venv_system_site_packages']:
            venv.main(["--system-site-packages", cfg['venv_dirname']])
        else:
            venv.main([cfg['venv_dirname']])
    else:
        print("Running virtualenv", virtualenv.__version__)
        args = []
        if cfg['venv_python_exec']:
            args.extend(["-p", cfg['venv_python_exec']])
        if cfg['venv_system_site_packages']:
            args.append("--system-site-packages")
        args.append(cfg['venv_dirname'])
        virtualenv_pkg_major_ver = int(virtualenv.__version__.split(".", 1)[0])
        if virtualenv_pkg_major_ver >= 20:
            try:  # version >= 20.0.3
                virtualenv.cli_run(args)
            except AttributeError:  # version < 20.0.3
                import virtualenv.run
                virtualenv.run.run_via_cli(args)
        else:
            sys_argv = sys.argv.copy()
            sys.argv[1:] = args
            try:
                virtualenv.main()
            except SystemExit:
                pass
            sys.argv = sys_argv
            del sys_argv

    print("*** Creating virtual environment completed ***\n")

    print("*** Installing dependencies ***")

    # Install dependencies
    pip_exec = os.path.join(venv_bin_dirpath, "pip")
    if cfg['use_requirements_file']:
        if os.path.isfile("requirements.txt"):
            proc_info = subprocess.run(
                [pip_exec, "install", "-r", "requirements.txt"])
            if proc_info.returncode:
                warn("dependencies from file 'requirements.txt' not "
                     "installed.")
        else:
            warn("file 'requirements.txt' not found.")
    for dep_name, dep_spec in cfg['deps'].items():
        if os.path.isdir(dep_spec):
            cmd = [pip_exec, "install", "-e", dep_spec]
        elif re.match("[0-9]+(\.[0-9]+)*$", dep_spec):
            cmd = [pip_exec, "install", f"{dep_name}=={dep_spec}"]
        else:
            cmd = [pip_exec, "install", dep_spec]
        proc_info = subprocess.run(cmd)
        if proc_info.returncode:
            warn(f"package '{dep_name}' not installed.")

    # If necessary, install V-REP remote API bindings
    if cfg['vrep_dirname']:
        vrep_remote_api_dirpath = os.path.join(
            cfg['vrep_dirname'], "programming", "remoteApiBindings")
        vrep_py_dirpath = os.path.join(vrep_remote_api_dirpath, "python",
                                       "python")
        try:
            shutil.copy(os.path.join(vrep_py_dirpath, "vrep.py"),
                        venv_pkg_dirpath)
        except Exception:
            warn("file 'vrep.py' not copied.")
        else:
            print("File copied: 'vrep.py'.")
        try:
            shutil.copy(os.path.join(vrep_py_dirpath, "vrepConst.py"),
                        venv_pkg_dirpath)
        except Exception:
            warn("file 'vrepConst.py' not copied.")
        else:
            print("File copied: 'vrepConst.py'.")
        if sys_name == "Mac":
            vrep_lib_filepath = os.path.join(vrep_remote_api_dirpath, "lib",
                                             "lib", sys_name,
                                             f"remoteApi.{lib_ext}")
            if not os.path.isfile(vrep_lib_filepath):
                vrep_lib_filepath = os.path.join(vrep_remote_api_dirpath,
                                                 "lib", "lib",
                                                 f"remoteApi.{lib_ext}")
        else:
            vrep_lib_filepath = os.path.join(
                vrep_remote_api_dirpath, "lib", "lib", sys_name,
                f"{python_bit_arch}Bit", f"remoteApi.{lib_ext}")
            if not os.path.isfile(vrep_lib_filepath):
                vrep_lib_filepath = os.path.join(
                    vrep_remote_api_dirpath, "lib", "lib",
                    f"{python_bit_arch}Bit", f"remoteApi.{lib_ext}")
        try:
            shutil.copy(vrep_lib_filepath, venv_pkg_dirpath)
        except Exception:
            warn(f"file 'remoteApi.{lib_ext}' not copied.")
        else:
            print(f"File copied: 'remoteApi.{lib_ext}'.")

    print("*** Installing dependencies completed ***\n")

    print("*** Creating additional directories and files ***")

    # If necessary, create simulations directory
    if cfg['create_simulations_dir']:
        try:
            os.mkdir("simulations")
        except FileExistsError:
            warn("directory 'simulations' not created; directory already "
                 "exists.")
        except Exception:
            warn("directory 'simulations' not created.")
        else:
            print("Directory created: 'simulations'.")

    # If necessary, create setup file
    if cfg['create_setup_file']:
        if sys_name == "Windows":
            make_setup_file = make_setup_file_cmd
            setup_filename = "setup.bat"
        else:
            make_setup_file = functools.partial(make_setup_file_bash,
                                                sys_name=sys_name)
            setup_filename = "setup.sh"
        try:
            make_setup_file(setup_filename, venv_bin_dirpath,
                            cfg['vrep_dirname'])
        except FileExistsError:
            warn(f"file '{setup_filename}' not created; file already exists.")
        except Exception:
            warn(f"file '{setup_filename}' not created.")
        else:
            print(f"File created: '{setup_filename}'.")

    if not (cfg['create_simulations_dir'] or cfg['create_setup_file']):
        print("Nothing to create")

    print("*** Creating additional directories and files completed ***\n")

    # Display summary information
    if not n_warnings:
        print("*** Success ***")
    else:
        print(f"*** Success, but with {n_warnings} warning(s) ***")


if __name__ == '__main__':
    sys.exit(main())
