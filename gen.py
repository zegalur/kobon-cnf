# Kobon generator using CNF model and Kissat SAT-solver.
# Pavlo Savchuk 2025

import koboncnf

import subprocess
import threading
import signal
import sys
import ast
import os

from datetime import datetime

help_info = """This script, with the help of `koboncnf` and the Kissat SAT solver, generates 
as many distinct tables of Kobon triangle problem pseudo-line arrangements as 
possible. You can interrupt the process and resume it later - just run the 
script with the same parameters and say "Y" to continue.

Make sure Kissat is installed and accessible by running `kissat` from 
the command line."""

def gen_main(
        TMP_DIR,
        RES_DIR,
        FIT_DIR,
        params_str,
        
        line_count,
        mirrored,
        rotational_symmetry,
        missing_triangles,
        clear,
        ):

    skip = []
    
    cnf_filename = TMP_DIR + "in-kobon" + params_str + ".cnf"
    sat_filename = TMP_DIR + "out-kobon" + params_str + ".cnf"
    res_filename = koboncnf.get_res_filename(RES_DIR, params_str)

    # ====================== Clear the data if needed ======================= #

    if clear:
        print("Deleting existing data...")
        if os.path.exists(res_filename):
            os.remove(res_filename)
        print("The file '{}' has been deleted.".format(res_filename))

    # ======================= Read the previous data ======================== #

    if os.path.exists(res_filename):
        cont = input("Previous results found. Continue? (y/Y/n/N):")
        if (len(cont) == 0) or (cont in "yY"):
          print("Reading previous data...")
          with open(res_filename, "r") as file:
            data_str = file.read()
            skip = ast.literal_eval(data_str)
            print("...DONE")

    # ============================ Calculations ============================= #

    def run_kissat(params, output_file):
        with open(output_file, 'w') as f:
          # Start the process
          process = subprocess.Popen(
              ['kissat'] + params,
              stdout=f,
              stderr=subprocess.STDOUT
          ) 
          # Wait for kissat to finish
          process.wait() 

    while True:
        print("\nCurrently known: {}".format(len(skip)))

        print("    Generating the next CNF model...")
        koboncnf.generate(
            line_count, cnf_filename,
            rotational_symmetry = rotational_symmetry,
            mirrored = mirrored,
            missing_triangles = missing_triangles,
            skip = skip,
            generate_table = False,
            )

        print("    Running Kissat (from {})...".format(datetime.now()))
        run_kissat([cnf_filename], sat_filename)

        print("    Reading the results...")
        res = koboncnf.generate(
            line_count, sat_filename,
            rotational_symmetry = rotational_symmetry,
            mirrored = mirrored,
            missing_triangles = missing_triangles,
            skip = skip,
            generate_table = True,
            )

        if res['status'] == "ERROR":
            koboncnf.print_err(res['msg'])
            exit(1)

        if res['status'] == "OK":
            koboncnf.block_ctrl_c()
            print("    New table:")
            print(koboncnf.tabs_to_str([res['table']]))
            try:
              skip.append(res['table'])
              with open(res_filename, "w") as file:
                file.write(koboncnf.tabs_to_str(skip))
                print("    Results have been updated (`{}`).".format(
                  res_filename))
            finally:
              koboncnf.unblock_ctrl_c()

        if res['status'] == "UNSATISFIABLE":
            print("The last CNF model is UNSATISFIABLE.")
            print("All possible arrangements have been found.")
            print("Arrangements have been saved to `{}`".format(res_filename))
            print("EXIT")
            exit(0)


# Run the tool:
koboncnf.run(gen_main, script_name = "gen", info_text = help_info)
