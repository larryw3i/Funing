import getopt
import os
import re
import shutil
import sys
from pathlib import Path

from funing.local import _

app_name = _("funing")
app_version = _("0.2.35")
app_description = _("A face recognition gui")