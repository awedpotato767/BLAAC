#!python3

import os
import tomllib

#check that this module is running in the root directory
#and check for the license text at the same time.
try:
    with open("README.md") as readme:
        if "This code is released under the CC BY-SA license." not in readme.read():
            raise EOFError("Cannot find license text in README.md")
except FileNotFoundError:
    raise FileNotFoundError("Cannot find README.md. Please run this code from the BLAAC root directory.")


#config file reading
if not os.path.isfile("config/config.toml"):
    with open("config/sample_config.toml","r") as conf_file:
        conf_data = conf_file.read()
    with open("config/config.toml", "w") as cf:
        cf.write(str(conf_data))

#create some default entries
with open("config/sample_config.toml","rb") as conf_file:
    global_config = tomllib.load(conf_file)
#overwrite them with any custom values.
with open("config/config.toml","rb") as conf_file:
    global_config.update(tomllib.load(conf_file))
