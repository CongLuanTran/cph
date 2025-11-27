# Competitive Programming Helper

This is a small helper program for competitive programming. It can create a new
program to solve problem in C++ or Python according to a template that you can
set in `.config/cph/` and also the input and output file for that problem.

## Install

The way I would do it is to clone the project and install with make.

```bash
git clone git@github.com:CongLuanTran/cph.git
cd chp
make
```

## Usage

You can create a new solution for a problem with

```bash
cph new --language py --problem B
```

The program for now support only `py` and `cpp` for language, with `py` being
the default if you let it blank. Problem name is defaulted to `A`. Upon the
creation of the solution, two files for input and output will also be created.
