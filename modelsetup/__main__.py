"""Initial model setup launcher.

Initial model setup launcher launches an initial setup of a model. It first
determines the desired configuration based on a provided configuration file and
also determines the system configuration, then creates a virtual environment in
the project directory of the model, and finally installs necessary dependencies
in the virtual environment, optionally creating as well additional directories
and files that will be used when running simulations.
"""

import sys

from modelsetup import main

if __name__ == '__main__':
    sys.exit(main())
