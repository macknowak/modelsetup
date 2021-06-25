Changelog
=========

0.1.0 - Unreleased
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

### Documentation

- Added package description (file `README.md`).
- Added package license terms (file `LICENSE.txt`). The package is licensed
  according to the terms and conditions of the MIT License.
