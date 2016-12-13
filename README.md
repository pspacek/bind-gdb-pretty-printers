GDB pretty printers for data structures used by ISC BIND 9 
==========================================================
This directory contains pretty-printers which make easier to read
ISC BIND data structures in GDB with Python support.

Installation
------------
Some of the pretty printers need values specified in BIND's header files.
You have to run script `gen_json_dict.py` for each pretty-printer
before you start using it.

The script compiles short C program which prints values from the BIND header
files. Requirements are GNU cpp and gcc.

Usage
-----
To use pretty-printers, simply source the files into GDB:
(gdb) source /path/to/pretty/pp.py

BEWARE:
The pretty printers work well if memory is not corrupted.
Disable pretty printers if you suspect memory corruption:
(gdb) disable pretty-printer

For further information see
https://sourceware.org/gdb/onlinedocs/gdb/Python-API.html
