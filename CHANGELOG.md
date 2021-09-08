Changelog
=========

0.2.0 - Unreleased
------------------

### Added

- Added optional command-line argument for performing an initial setup of a
  model, which specifies that third-party package _virtualenv_ should be used
  for creating a virtual environment instead of package _venv_ from the
  standard library (argument `--use-virtualenv`).

### Fixed

- Fixed compatibility issues with invoking versions >=20.0.0 of package
  _virtualenv_.

0.1.0 - 2021-07-12
------------------

### Added

- Added performing an initial setup of a model (function `main()`). It is a
  function that first determines the desired configuration based on a provided
  configuration file and also determines the system configuration, then creates
  a virtual environment in the project directory of the model, and finally
  installs necessary dependencies in the virtual environment, optionally
  creating as well additional directories and files that will be used when
  running simulations.
- Added parsing a configuration file (function `parse_config()`). It is a
  function that reads a configuration file and determines the desired
  configuration with respect to the virtual environment to be created,
  dependencies to be installed, and optional additional directories and files
  to be created.
- Added determining V-REP version (function `get_vrep_version()`). It is a
  function that attempts to determine V-REP version based on the contents of
  the V-REP directory. On some V-REP installations, however, such an attempt
  may be unsuccessful.
- Added creating a setup file for Bash (function `make_setup_file_bash()`). It
  is a function that creates a setup script in the project directory of the
  model and populates it with appropriate settings. The script can be later
  sourced in the Bash interpreter, thereby activating the virtual environment,
  setting relevant environment variables and creating useful aliases.
- Added creating a setup file for Windows command line (function
  `make_setup_file_cmd()`). It is a function that creates a setup script in the
  project directory of the model and populates it with appropriate settings.
  The script can be later run in the Windows command-line interpreter, thereby
  activating the virtual environment, setting relevant environment variables
  and creating useful aliases.
- Added an example configuration file (file `init.cfg`). During installation
  this file is saved in the package install directory, from where it can
  subsequently be copied to the project directory of a model and adjusted
  accordingly.
- Added initial model setup launcher (file `__main__.py`). It is the main
  module of the package and thus is supposed to be executed as a script. When
  executed, it launches an initial setup of a model in the following manner: it
  first determines the desired configuration based on a provided configuration
  file and also determines the system configuration, then creates a virtual
  environment in the project directory of the model, and finally installs
  necessary dependencies in the virtual environment, optionally creating as
  well additional directories and files that will be used when running
  simulations.

### Documentation

- Added package description (file `README.md`). It includes a general
  characterization of the package and a description of the configuration file.
- Added package license terms (file `LICENSE.txt`). The package is licensed
  according to the terms and conditions of the MIT License.
