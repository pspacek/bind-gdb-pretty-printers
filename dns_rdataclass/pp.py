import os
import sys
import json



def gdb_printer_decorator(fn):
    gdb.pretty_printers.append(fn)
    return fn

class DNSRdataClassPrinter(object):
    def __init__(self, val):
        self.val = val

    def to_string(self):
        try:
            return _dns_rdataclass_dict[str(int(self.val))]
        except KeyError:
            return "! UNKNOWN " + str(int(self.val))

script_dir = os.path.dirname(os.path.realpath(__file__))
dict_fn = script_dir + "/rdataclass_dict.json"
_dns_rdataclass_dict = json.load(open(dict_fn))

# register pretty printers
@gdb_printer_decorator
def dns_rdataclass_printer(val):
    if str(val.type) == 'dns_rdataclass_t':
        return DNSRdataClassPrinter(val)
    return None
