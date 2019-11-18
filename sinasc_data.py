import pandas as pd
import statsmodels.api as sm
import json

from pysus.utilities.readdbc import read_dbc
from wget import download
from zipfile import ZipFile
from datetime import datetime
from patsy import dmatrices
from argparse import ArgumentParser


def print_or_write(to_print, write_file=None):
    """
    Prints or write the message in `to_print` to the file `write_file`
    :param to_print: the string to print
    :param write_file: the optional file name to print to
    """
    if write_file:
        f = open(write_file, "a+")
        f.write(str(to_print) + '\n')
        f.close()
    print(to_print)


def download_sinasc_2017_data(url='http://www2.datasus.gov.br/DATASUS/cache/Arq_865499362/Arq_865499362.zip',
                              fname='./data/sinasc2017.zip'):
    """
    Downloads data directly from Datasus ftp server from a preconfigured file with data from all
    states in 2017
    """
    download(url, fname)
    with ZipFile(fname, 'r') as zip_ref:
        zip_ref.extractall()


def read_data_from_state(state):
    """
    Reads data from the state passed in and formats it into a pandas data frame
    :param state: the Brazilian state code (e.g. "MG") to read into memory in a dataframe format
    :return: pandas dataframe
    """
    print(f"reading {state} dbc file")
    fname = f'./data/DN{state}2017.dbc'
    df = read_dbc(fname, encoding='iso-8859-1')
    return df


def clean_data(df, year=2017):
    """
    Given a pandas dataframe will clean the data by converting specific column value types and
    removing any rows with empty entries and/or null data. Will also remove all data prior to 2017
    :param df: the pandas dataframe corresponding to a given state or the country
    :param year: the year to start collecting data from. Defaults to 2017
    :return: a pandas dataframe with clean and reformatted data.
    """
    df = df[df["DTNASC"] != '']
    df = df[(df["HORANASC"] != '') & (df["HORANASC"].str.len() == 4)]
    df["NASC"] = df[["DTNASC", "HORANASC"]].apply(lambda x: ' '.join(x), axis=1)
    df["NASC"] = pd.to_datetime(df["NASC"], format="%d%m%Y %H%M")
    df = df[df["NASC"] > datetime(year=year, month=1, day=1)]
    for col in ["ESCMAE", "PARTO", "RACACOR", "GESTACAO", "LOCNASC"]:
        df = df[df[col] != '']
        df[col] = df[col].astype(int)
        df = df[df[col] != 9]
    df["ESCMAE"] = df["ESCMAE"].map({2: 1, 3: 1, 4: 2, 5: 3})
    df = df[df["GESTACAO"] > 5]
    df = df[(df["LOCNASC"] == 1) | (df["LOCNASC"] == 2)]
    return df


def determine_cesarian_ratio(df, variable, metrics):
    """
    Given a dataframe and variables to measure specific ratios on will identify the ratio of births that came
    from c-sections.
    :param df: pandas data frame
    :param variable: the variable metric in the data to check rations on
    :param metrics: the values corresponding to the variable that we want to measure cesarian births on
    :return: a json formatted dictionary with the relative ratios
    """
    data = {}
    variable_df = df[variable]
    num_entries = df.shape[0]
    for metric, name in metrics.items():
        metric_df = df[variable_df == metric]
        num_in_metric = metric_df.shape[0]
        num_cesarians = metric_df[metric_df["PARTO"] == 2].shape[0]
        data[name] = {
            "y": num_cesarians,
            "y%": str(round((100 * float(num_cesarians) / num_in_metric) if num_in_metric else 0, 2)),
            "n": num_in_metric - num_cesarians,
            "n%": str(round((100 * float(num_in_metric - num_cesarians) / num_in_metric) if num_in_metric else 0, 2)),
            "t": num_in_metric,
            "t%": str(round((100 * float(num_in_metric) / num_entries) if num_in_metric else 0, 2))
        }
    return data


def determine_cesarian_ratios(df, write_file=None):
    """
    Given a dataframe, will determine the ratio of each subdivision in race and education and print this as a json
    object.
    :param df: the pandas dataframe
    """
    race_entry_meanings = {1: "White", 2: "Black", 3: "Amarela", 4: "Parda", 5: "Indigenous"}
    education_entry_meanings = {1: "Up to 7 years", 2: "8 to 11 years", 3: "12 years and over"}
    ratio_data = {
        "Race": determine_cesarian_ratio(df, "RACACOR", race_entry_meanings),
        "Education": determine_cesarian_ratio(df, "ESCMAE", education_entry_meanings)
    }
    print_or_write(json.dumps(ratio_data, indent=4), write_file)


def calculate_poission_reg(df, dependent_var, independent_vars, write_file=None):
    """
    Will call on statsmodel module to apply a poisson regression on a Generalized Linear Model.
    :param df: pandas dataframe
    :param dependent_var: the dependent column we want to measure independent_vars on
    :param independent_vars: other columns we want to measure the influence the `dependent_var`
    :param write_file: the file to write to, optionally
    """
    df = df[independent_vars + [dependent_var]]
    independent_vars_string = ' + '.join(independent_vars)
    expr = f"""{dependent_var} ~ {independent_vars_string}"""
    y, X = dmatrices(expr, df, return_type='dataframe')
    poisson_training_results = sm.GLM(y, X, family=sm.families.Poisson()).fit()
    print_or_write(poisson_training_results.summary(), write_file)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--redownload", action="store_true")
    parser.add_argument("--poisson_file")
    parser.add_argument("--ratio_file")
    args = vars(parser.parse_args())
    if args["redownload"]:
        download_sinasc_2017_data()
    poisson_file = args.get("poisson_file")
    ratio_file = args.get("ratio_file")
    br_states = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI',
                 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
    state_dfs = [None]*len(br_states)
    for i, state_code in enumerate(br_states):
        print_or_write(f"cleaning data for state {state_code}, {i}/{len(br_states)}", poisson_file)
        print_or_write(f"cleaning data for state {state_code}, {i}/{len(br_states)}", ratio_file)
        state_dfs[i] = clean_data(read_data_from_state(state_code))
        determine_cesarian_ratios(state_dfs[i], ratio_file)
        calculate_poission_reg(state_dfs[i], "PARTO", ["ESCMAE", "RACACOR", "LOCNASC"], poisson_file)
        print()
    country_df = pd.concat(state_dfs)
    determine_cesarian_ratios(country_df, ratio_file)
    calculate_poission_reg(country_df, "PARTO", ["ESCMAE", "RACACOR", "LOCNASC"], poisson_file)
