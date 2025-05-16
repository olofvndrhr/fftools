import sys
from pathlib import Path


sys.path.insert(0, str(Path("..", "src").resolve()))

from fftools.__about__ import __version__


### sphinx config ###

project = "fftools"
copyright = "2025-now, Ivan Schaller"  # noqa
author = "Ivan Schaller"
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinx_copybutton",
]


### autodoc ###

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": False,
    "special-members": "__init__",
    "show-inheritance": True,
    "exclude-members": "__weakref__",
}
autodoc_typehints = "both"
autodoc_typehints_description_target = "all"

### intersphinx ###

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}


### todo ###

todo_include_todos = True


### myst ###

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3


### content ###

master_doc = "index"

templates_path = ["_templates"]
html_static_path = ["_static"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


### theme ###

# tml_theme = "alabaster"
html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/olofvndrhr/fftools/",
    "source_branch": "main",
    "source_directory": "docs/",
}
