# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""An editorial interchange format and library.

see: http://opentimeline.io

.. moduleauthor:: Contributors to the OpenTimelineIO project <otio-discussion@lists.aswf.io>
"""

# flake8: noqa

# in dependency hierarchy
from . import (
    opentime,
    exceptions,
    core,
    schema,
    schemadef,
    plugins,
    media_linker,
    adapters,
    hooks,
    algorithms,
    url_utils,
    versioning,
)

# Non-editable builds stamp __version__ et al. onto the end of this file (see
# setup.py), overriding this.  Editable installs load this file unstamped, so
# fall back to the installed package metadata.
try:
    from importlib.metadata import version as _version
    __version__ = _version("OpenTimelineIO")
    del _version
except Exception:
    __version__ = "unknown"
