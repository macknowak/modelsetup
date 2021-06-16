Changelog
=========

0.1.0 - Unreleased
------------------

### Added

- Added parsing a configuration file (function `parse_config()`). It is a
  function that reads a configuration file and determines the desired
  configuration with respect to the virtual environment to be created,
  dependencies to be installed, and optional additional directories and files
  to be created.
- Added determining V-REP version (function `get_vrep_version()`). It is a
  function that attempts to determine V-REP version based on the contents of
  the V-REP directory. On some V-REP installations, however, such an attempt
  may be unsuccessful.

### Documentation

- Added package description (file `README.md`).
- Added package license terms (file `LICENSE.txt`). The package is licensed
  according to the terms and conditions of the MIT License.
