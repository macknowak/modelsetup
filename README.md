# ModelSetup: Utility Supporting Initial Model Setup

ModelSetup is a Python utility that supports an initial setup of a
computational model that may utilize spiking neural networks implemented using
Nengo and the robot simulator V-REP.

## Initial setup process

The aim of an initial setup of a model is to create a dedicated virtual
environment in its project directory, install necessary dependencies in it
(such as Nengo and V-REP remote API bindings), and optionally create additional
directories and files that will be used when running simulations (such as a
parent directory for directories related to individual simulations).

The initial setup process involves the following steps:

1. determining the desired configuration (e.g., what dependencies should be
   installed);
2. determining the system configuration (e.g., operating system, Python
   version);
3. creating a virtual environment;
4. installing dependencies in the virtual environment;
5. creating additional directories and files.

The desired configuration is provided using a dedicated configuration file.

## Launching an initial setup process

To launch an initial setup process, package `modelsetup` should be executed as
a script. Additionally, a single argument that specifies a configuration file
with the desired configuration is required (no other arguments are accepted).

For example, an initial setup process may be launched as follows:
```
python -m modelsetup init.cfg
```
where `init.cfg` is the name of a configuration file.

## Configuration file

To specify the desired configuration, a dedicated configuration file is
employed. The conventional name of such a file is `init.cfg`, but this is not a
requirement as any name can be used. An example configuration file, named
`init.cfg`, is stored, together with other modules, in the package install
directory; it can be copied from that location to the project directory of the
model and adjusted accordingly.

The format of the configuration file follows that of the INI file: individual
aspects of the desired configuration are specified as values associated with
the corresponding keys, which are grouped into sections. There are 5 sections
in the configuration file: `VirtualEnv`, `Dependencies`,
`OptionalDependencies`, `VRep`, and `ExtraDirectoriesAndFiles`. Some keys
require that their value be specified, but for others it is optional (in which
case the value may be left empty).

### Section `VirtualEnv`

This section describes a virtual environment to be created in the project
directory of the model.

Supported keys:

- `Directory` (required) - the name of the directory in which the virtual
  environment should be stored (an example value: `virtualenv`);
- `Interpreter` (optional) - the name of or the path to the Python interpreter
  that should be installed in the virtual environment; if empty, the Python
  interpreter invoked for launching an initial setup process will be used (an
  example value: `python2`);
- `SystemSitePackages` (required) - specification whether the virtual
  environment should be given access to the system site-packages directory
  (allowed values: `yes`, `no`).

### Section `Dependencies`

This section describes which required dependencies should be installed in the
virtual environment. Such dependencies can be determined either based on the
contents of the requirements file provided with the model (`requirements.txt`)
or based on the values associated with the keys that follow.

Supported keys:

- `OverrideRequirementsFile` (required) - specification whether the contents of
  the requirements file provided with the model should be overridden (and thus
  the required dependencies should be determined based on the keys that follow)
  or the keys that follow should be ignored (and the required dependencies
  should be installed based on the contents of the requirements file) (allowed
  values: `yes`, `no`);
- `SimTools` (optional) - specification of the SimTools package; if empty, the
  package will not be installed; the value is ignored if the required
  dependencies should be installed based on the contents of the requirements
  file;
- `VRepSim` (optional) - specification of the VRepSim package; if empty, the
  package will not be installed; the value is ignored if the required
  dependencies should be installed based on the contents of the requirements
  file;
- `Nengo` (optional) - specification of the Nengo library; if empty, the
  library will not be installed; the value is ignored if the required
  dependencies should be installed based on the contents of the requirements
  file.

In the case of the last three keys, a specification of a dependency can take
one of the following forms:

- version - used for installing packages from The Python Package Index (PyPI)
  (an example entry: `Nengo = 2.8.0`);
- URL - used for installing packages from online repositories (an example
  entry: `Nengo = git+https://github.com/nengo/nengo@v2.8.0`);
- file name (or path to a file) - used for installing packages from downloaded
  archive files (an example entry: `Nengo =
  /home/user/Downloads/nengo-2.8.0.zip`);
- directory name (or path to a directory) - used for installing packages in
  editable/develop mode (an example entry: `Nengo =
  /home/user/Projects/nengo`).

### Section `OptionalDependencies`

This section describes which optional dependencies should be installed in the
virtual environment. These dependencies are installed independently of the
required dependencies described in the previous section and are determined
based on the values associated with the keys that follow.

Supported key:

- `NengoGui` (optional) - specification of the Nengo GUI interactive
  visualizer; if empty, the visualizer will not be installed.

Optional dependencies can be specified using the same forms as in the case of
required dependencies.

### Section `VRep`

This section describes the robot simulator V-REP if used by the model and thus
allows its remote API bindings to be installed in the virtual environment.

Supported key:

- `Directory` (optional) - path to the V-REP install directory; if empty, no
  remote API bindings will be installed (an example entry: `Directory =
  /opt/V-REP_PRO_EDU_V3_6_2_Ubuntu18_04`).

### Section `ExtraDirectoriesAndFiles`

This section describes additional directories and files to be created in the
project directory of the model, which will be used when running simulations.

Supported keys:

- `CreateSimulationsDir` (required) - specification whether a parent directory
  for directories related to individual simulations (also called the "master
  directory") should be created; if so, directory `simulations` will be created
  in the project directory of the model (allowed values: `yes`, `no`);
- `CreateSetupFile` (required) - specification whether a setup script that can
  be used for activating the virtual environment, setting relevant environment
  variables, and creating useful aliases should be created; if so, such a setup
  script fitted to a shell appropriate for the operating system used will be
  created in the project directory of the model and partially populated with
  appropriate settings (depending on the operating system, it will be either
  `setup.sh` for Bash or `setup.bat` for Windows command line) (allowed values:
  `yes`, `no`).
