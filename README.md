# Competitive Programming Helper

This is a small helper program for competitive programming. It can create a new
program to solve problem in C++ or Python, according to a template that you can
set in `.config/cph/`, and also the input and output file for that problem.

## Install

The way I would do it is to clone the project and install with make.

```bash
git clone ssh://git@codeberg.org/CongLuanTran/cph.git
cd chp
make
```

## Usage

### Solution file creation

You can create a new solution for a problem with

```bash
cph new --language py --problem B
```

The program for now support only `py` and `cpp` for language, with `py` being
the default if you let it blank. Problem name is defaulted to `A`. Upon the
creation of the solution, two files for input and output will also be created.
The input file has the suffix `.INP` and the output file has `.OUT`

### Run the solution

You can run the solution file:

```bash
cph run B.py
```

You will be prompted for the input and output file if you don't specify them.
The default basename for both of them is assumed to be the same as the problem
name. For Python, the program simply run the `.py` file, but for C++ it will
automatically compile the source code and then run the binary. The program will
try to run Python files using PyPy if it is in path, else it will revert to
CPython.
