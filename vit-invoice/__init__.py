import yaml
import os

# Export render function
from main import render_html

# Export theme configuration
config_path = os.path.join(os.path.dirname(__file__), "config.yml")
config = yaml.load(file(config_path, "r"))

# Export the directory
directory = os.path.dirname(__file__)