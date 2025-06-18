# Kobon generator utils.
# Pavlo Savchuk 2025

import koboncnf

import subprocess
import threading
import signal
import sys
import ast
import os

from datetime import datetime


def print_err(msg):
  print("ERROR: " + msg)
  print("Run the script without parameters to see the help.")
  exit(1)

help_info_template = """
{info}

Use `Ctrl+C` to stop the script. Later, you can resume to where it was.

For more info: <... github link here ...>

Usage:
> python[3] {name}.py <line_count> [<options> ...]

Where:
    <line_count>      -- Number of straight lines (>= 3).

Options:
    -C                -- Clear all the previous data and start from scratch.
    -R <number>       -- Set rotational symmetry (default = 1).
    -M                -- Enable mirror symmetry (disables rotational symmetry).
    -L <n1,n2,...>    -- Specify a list of one-based line indices with missing 
                         triangles.
{params}"""


# Original signal handler
original_handler = signal.getsignal(signal.SIGINT)

def block_ctrl_c():
    # Ignore Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def unblock_ctrl_c():
    # Restore the original handler
    signal.signal(signal.SIGINT, original_handler)


def tabs_to_str(tabs):
    res = "[\n"
    for t in tabs:
      res += "[\n"
      for r in t:
        res += "["
        for i in range(len(r)):
          res += str(r[i])
          if i < (len(r) - 1):
            res += ","
        res += "],\n"
      res += "],\n"
    res += "]"
    return res


def get_res_filename(RES_DIR, params_str):
    return RES_DIR + "kobon" + params_str + ".txt"

def get_params_filename(PARAMS_DIR, params_str):
    return PARAMS_DIR + "kobon" + params_str + ".txt"

def run(main_func,
        script_name = "script_name_here",
        info_text = "<... info text here ...>",
        additional_params = [],
        additional_params_info = "",
        ):

    # Default options:

    TMP_DIR = "tmp/"
    RES_DIR = "res/"
    FIT_DIR = "fit/"

    line_count = 3
    mirrored = False
    rotational_symmetry = 1
    missing_triangles = []
    clear = False

    # ========================== Read the options =========================== #

    if len(sys.argv) == 1:
        print(help_info_template.format(
            info = info_text, 
            name = script_name, 
            params = additional_params_info,
            ))
        exit(0)

    line_count = int(sys.argv[1])

    i = 2
    mt_str = ""
    while (i < len(sys.argv)):
        next_option = sys.argv[i]
        i += 1

        if next_option == "-M":
          mirrored = True

        if next_option == "-C":
          clear = True

        elif next_option == "-R":
          if i >= len(sys.argv):
            print_err("Expecting -R <number>.")
          rotational_symmetry = int(sys.argv[i])
          i += 1

        elif next_option == "-L":
          if i >= len(sys.argv):
            print_err("Expecting -L <n1,n2,...>.")
          l_str = sys.argv[i]
          mt_str = "-l-" + l_str.replace(",", "-")
          i += 1
          missing_triangles = [ int(s) for s in l_str.split(",") ]

        elif next_option in additional_params:
          continue

        else:
          print_err("Unknown option `{}`".format(next_option))

    if mirrored:
        rotational_symmetry = 1

    params_str = "-{N}{symm}{mirr}{missing}".format(
      N = line_count,
      symm = "" if rotational_symmetry==1 else "-rot{}".format(rotational_symmetry),
      mirr = "" if not mirrored else "-m",
      missing = mt_str,
      )

    # Run the main func:
    main_func(
        TMP_DIR = TMP_DIR,
        RES_DIR = RES_DIR,
        FIT_DIR = FIT_DIR,
        
        params_str = params_str,
        
        line_count = line_count,
        mirrored = mirrored,
        rotational_symmetry = rotational_symmetry,
        missing_triangles = missing_triangles,
        clear = clear,
    )
