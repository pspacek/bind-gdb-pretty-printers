import os
import sys
import json



def gdb_printer_decorator(fn):
    gdb.pretty_printers.append(fn)
    return fn

class ISCResultPrinter(object):
    def __init__(self, val):
        self.val = val

    def to_string(self):
        try:
            return _isc_result_dict[str(int(self.val))]
        except KeyError:
            return "! UNKNOWN " + str(int(self.val))

script_dir = os.path.dirname(os.path.realpath(__file__))
dict_fn = script_dir + "/result_dict.json"
_isc_result_dict = json.load(open(dict_fn))

# register pretty printers
@gdb_printer_decorator
def isc_result_printer(val):
    if str(val.type) == 'isc_result_t':
        return ISCResultPrinter(val)
    return None
