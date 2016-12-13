#!/bin/python

import re
import subprocess

def preprocess_header():
    # cpp -dM -I /usr/include/bind9 /usr/include/bind9/dns/result.h > out.h
    cpp = subprocess.Popen(["cpp", "-dM", "-I", "/usr/include/bind9", "/usr/include/bind9/dns/name.h"],
            stdout=subprocess.PIPE)
    output, stderr = cpp.communicate()
    if cpp.returncode != 0:
        raise ValueError("cpp failed")
    return output.split("\n")

def c_prog_gen(defines):
    """generate C program which outputs JSON dict {value: define name}"""
    c_prog = """
#include <stdio.h>
#include <dns/name.h>

/*
 this program generates JSON dict with numberic values for all result #defines
  {"ISC_R_SUCCESS": 0}
*/
int                                                                             
main (int argc, char ** argv) {
    printf("{\\n");
"""

    prefix = ""
    for l in defines:
        match = re.match("^#define +(DNS_NAMEATTR_[A-Z]+) ", l)
        if match:
            c_prog += '    printf("%s\\"%s\\": %%u", %s);\n' % (prefix, match.group(1), match.group(1))
            prefix = ",\\n"
    
    c_prog += """
    printf("\\n}");

    return 0;
}
"""
    
    return c_prog

def c_compile(source_fn, out_fn):
    gcc = subprocess.Popen(["gcc", "-I/usr/include/bind9", "-o", "dict_generator", source_fn],
            stdout=subprocess.PIPE)
    output, stderr = gcc.communicate()
    if gcc.returncode != 0:
        raise ValueError("gcc failed")


def gen_dict(binary_fn, out_fn):
    with open(out_fn, "w") as output_f:
        gen = subprocess.Popen(["./" + binary_fn],
                stdout=subprocess.PIPE)
        output, stderr = gen.communicate()
        if gen.returncode != 0:
            raise ValueError("dict generator failed")
        output_f.write(output)



dict_fn = "nameattr_dict.json"
binary_fn = "dict_generator"
source_fn = binary_fn + ".c"

defines = preprocess_header()
c_prog = c_prog_gen(defines)
with open(source_fn, "w") as c_prog_f:
    c_prog_f.write(c_prog)
c_compile(source_fn, binary_fn)
gen_dict(binary_fn, dict_fn)
