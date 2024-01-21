# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

sys.path.insert(0, os.path.abspath('../..'))
project = 'PythonGram'
copyright = '2024, GodVov4'
author = 'GodVov4'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['autodoc2', 'myst_parser']
autodoc2_packages = [
    '../../main.py',
    '../../src/routes',
    '../../src/repository',
    '../../src/services',
    '../../src/database',
    '../../src/entity',
    '../../src/schemas',
]
myst_heading_anchors = 3

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'alembic']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'press'
html_static_path = ['_static']
