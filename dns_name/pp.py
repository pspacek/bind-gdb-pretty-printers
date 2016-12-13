import os
import sys
import json

import dns.name # python-dns

def gdb_printer_decorator(fn):
    gdb.pretty_printers.append(fn)
    return fn

class DNSNamePrinter(object):
    def __init__(self, val):
        self.val = val
        self.root = dns.name.from_text(".")

    def to_string(self):
        if self.val['magic'] != 0x444e536e:
            return "! INVALID MAGIC"

        # find enabled flags
        flags = int(self.val['attributes'])
        if not flags:
            attrs = ["no flags"]
        else:
            attrs = []
        is_absolute = (flags & int(_dnsattr_dict['DNS_NAMEATTR_ABSOLUTE']) != 0)

        for name, value in _dnsattr_dict.items():
            value = int(value)
            if flags & value:
                attrs.append(name)
                flags -= value
        # check that all flags where processed
        if flags != 0:
            attrs.append("!UNKNOWN:" + hex(flags))
        attrs_str = " | ".join(attrs)

        if self.val['ndata'] == 0x0:
            name = "(NULL ndata)"
        else:
            try:
                # append \x00 to the ndata to create name in wire format
                wire = self.val['ndata'].string()[0:int(self.val['length'])] + "\x00"
                wire = wire.encode('utf-8')  # wtf?
                name = dns.name.from_wire(wire, 0)[0]

                # relativize to root if the name is not absolute
                if not is_absolute:
                    name = name.choose_relativity(self.root, True)

                return "%s (%s)" % (name, attrs_str)

            except Exception as e:
                errmsg = "! FormErr? %s %s" % (type(e), e)
                return errmsg


script_dir = os.path.dirname(os.path.realpath(__file__))
dict_fn = script_dir + "/nameattr_dict.json"
_dnsattr_dict = json.load(open(dict_fn))

# register pretty printers
@gdb_printer_decorator
def dns_name_printer(val):
    if str(val.type) == 'dns_name_t':
        return DNSNamePrinter(val)
    return None
