# noinspection PyUnresolvedReferences
from xrlint.api import *
from xrlint.plugins.core.rules import import_rules
from xrlint.formatters import import_formatters

import_rules()
import_formatters()
