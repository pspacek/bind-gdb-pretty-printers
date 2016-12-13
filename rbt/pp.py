import os
import sys
import json

import dns.name # python-dns

NULL = 0
RED = 0
BLACK = 1

def gdb_printer_decorator(fn):
    gdb.pretty_printers.append(fn)
    return fn

def NAMELEN(node):
    return node.dereference()['namelen']

def NAME(node):
    ptr = node + 1
    ptr = ptr.cast(gdb.lookup_type('unsigned char').pointer())
    return ptr

def IS_RED(node):
    return (int(node) != NULL and (node['color'] == RED))

def IS_BLACK(node):
    return (int(node) == NULL or (node['color'] == BLACK))

def IS_ROOT(node):
    return node['is_root'] == 1

def PARENT(node):
    return node['parent']

def LEFT(node):
    return node['left']

def RIGHT(node):
    return node['right']

def DOWN(node):
    return node['down']

def dns_rbt_printnodename(node):
    wire_len = int(NAMELEN(node))
    wire = NAME(node).string()[0:wire_len].encode('utf-8')  # wtf?
    wire += b'\x00'
    name = dns.name.from_wire(wire, 0)[0]
    if not name == dns.name.root:
        name = name.choose_relativity(dns.name.root, True)
    
    return str(name)

def dns_rbt_indent(depth):
     return " "*4*depth

def dns_rbt_printtree(root, parent, depth):
    out = dns_rbt_indent(depth)

    if (root != NULL):
        out += dns_rbt_printnodename(root)
        out += " ("
        if IS_RED(root):
            out += "RED"
        else:
            out += "black"
        if (parent):
            out += " from "
            out += dns_rbt_printnodename(parent)

        if ((not IS_ROOT(root) and PARENT(root) != parent) or
            (    IS_ROOT(root) and depth > 0 and
                 DOWN(PARENT(root)) != root)):

            out += " (BAD parent pointer! -> "
            if (PARENT(root) != NULL):
                out += dns_rbt_printnodename(PARENT(root))
            else:
                out += "NULL"
            out += ")"

        out += "; node "
        out += str(root)

        out += "; data "
        out += str(root['data'])
        out += ")\n"

        depth += 1

        if (DOWN(root)):
            out += dns_rbt_indent(depth)
            out += "++ BEG down from "
            out += dns_rbt_printnodename(root)
            out += "\n"
            out += dns_rbt_printtree(DOWN(root), NULL, depth)
            out += dns_rbt_indent(depth)
            out += "-- END down from "
            out += dns_rbt_printnodename(root)
            out += "\n"

        if (IS_RED(root) and IS_RED(LEFT(root))):
            out += "** Red/Red color violation on left\n"
        out += dns_rbt_printtree(LEFT(root), root, depth)

        if (IS_RED(root) and IS_RED(RIGHT(root))):
            out += "** Red/Red color violation on right\n"
        out += dns_rbt_printtree(RIGHT(root), root, depth)

    else:
        out += "NULL\n"

    return out

class RBTPrinter(object):
    def __init__(self, val):
        self.val = val

    def to_string(self):
        if self.val['magic'] != 0x5242542b:
            return "! INVALID MAGIC"

        out = "RBT node count = %s\n" % self.val['nodecount']
        out += dns_rbt_printtree(self.val['root'], 0, 0)
        return out

# register pretty printers
@gdb_printer_decorator
def dns_rbt_printer(val):
    if str(val.type) == 'dns_rbt_t':
        return RBTPrinter(val)
    return None
