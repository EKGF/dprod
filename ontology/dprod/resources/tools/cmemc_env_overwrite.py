#!/usr/bin/env python3

import os
import sys
from configparser import ConfigParser

"""Replace values by environment variables in an ini file.

Call this script with

```
python cmemc_env_overwrite.py ini_file config-section env_vars …
```

e.g.
```
python cmemc_env_overwrite.py cmemc.ini instance.eccenca.dev OAUTH_CLIENT_ID OAUTH_CLIENT_SECRET
```

It inserts (writes) the keys and their values to the ini file.

"""

config_file = sys.argv[1]
config_section = sys.argv[2]

config = ConfigParser()
config.read(config_file)
for config_var in sys.argv[3:]:
    config.set(config_section, config_var, os.environ[config_var])

with open(config_file, 'w') as config_file_handler:
    config.write(config_file_handler)
