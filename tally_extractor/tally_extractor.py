"""
This Python script processes ".mctal" files in a specified directory to extract relevant data, such as
Tally names, values, and associated errors. It creates a Pandas DataFrame with these data and saves it to
an Excel file in the same directory.

The script includes several functions that perform specific data processing steps:
- remove_blank_lines(): Removes blank lines from the ".mctal" file.
- extract_tally_names(): Extracts Tally names from the ".mctal" files.
- extract_tally_values(): Extracts Tally values from the ".mctal" files.
- extract_energies(): Extracts energies from Tally values.
- extract_errors(): Extracts errors from Tally values.
- extract_version(): Extracts the MCNP version from the ".mctal" files.
- extract_particles(): Extracts the number of particles from the ".mctal" files.
- process_files(): Main function that coordinates the processing of all ".mctal" files in the specified directory.

The main code executes the process_files() function with the path of the folder containing the ".mctal" files as an argument.
Make sure to provide the correct path to the folder containing the ".mctal" files before running this script.
"""

import os
import re
import pandas as pd


def remove_blank_lines(file_lines):
    return [line.strip() for line in file_lines if line.strip()]


def extract_tally_names(file_lines):
    return [file_lines[i + 2] for i, line in enumerate(file_lines) if 'tally' in line]


def extract_tally_values(file_lines):
    return [file_lines[i + 1] for i, line in enumerate(file_lines) if line == 'vals']


def extract_energies(tally_values):
    return [value.split()[0] for value in tally_values]


def extract_errors(tally_values):
    return [value.split()[-1] for value in tally_values]


def extract_version(file_lines):
    first_line = file_lines[0]
    if re.search(r"mcnpx", first_line, re.IGNORECASE):
        return "MCNPX"
    elif re.search(r"mcnp\s+6", first_line, re.IGNORECASE):
        return "MCNP6"
    else:
        return "Version not found"


def extract_particles(file_lines):
    match = re.search(r"\s(\d{8,11})\s", file_lines[0])
    return f'NPS: {match.group(1)}' if match else "Particles not found"


def process_files(directory_path):
    mctal_files = sorted([f for f in os.listdir(directory_path) if f.endswith('.mctal')])
    results_df = pd.DataFrame()

    for file in mctal_files:
        file_path = os.path.join(directory_path, file)
        with open(file_path, 'r') as mctal_file:
            file_lines = remove_blank_lines(mctal_file.readlines())

        file_name = os.path.splitext(file)[0]
        mcnp_version = extract_version(file_lines)
        particle_count = extract_particles(file_lines)
        tally_values = extract_tally_values(file_lines)
        tally_names = extract_tally_names(file_lines)
        energies = list(map(float, extract_energies(tally_values)))
        errors = list(map(float, extract_errors(tally_values)))

        tally_names.insert(0, file_name)
        energies.insert(0, mcnp_version)
        errors.insert(0, particle_count)

        data_df = pd.DataFrame({
            'Names': tally_names,
            'Values': energies,
            'Errors': errors
        })

        results_df = pd.concat([results_df, data_df], axis=1)

    output_file = os.path.join(directory_path, 'tally_extractor.xlsx')
    results_df.to_excel(output_file, index=False)


if __name__ == "__main__":
    mctal_folder = input("Please enter the path to the folder containing the .mctal files: ")
    process_files(mctal_folder)
