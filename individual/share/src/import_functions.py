#!usr/bin/env python3
#
# Author:   RR, TH

''' functions used in the import step'''

import datetime
import io
import re
import pandas as pd
import numpy as np


def read_p046957_file(input_file, original_crid_col,
                      notnull="", isnull="", drop_col="",
                      drop_col_val=(), add_skip=1,
                      original_crid_mixed=False):
    ''' returns a pandas dataframe,
        report produced data, and FOIA request number
        after reading in an excel file
        in the format of FOIA number 46957 (Nov. 2016 complaints)
        collects report produced data, FOIA request number,
        adds in a corrected CRID column due to row splitting,
        and removes metadata in order to find the actual header row,
        also removes null columns or data that doesn't pertain to
        the correct specified criteria.
    '''

    df = pd.read_excel(input_file, rows=20)

    col_list = df.columns.tolist()
    report_produced_date = [x for x in col_list
                            if isinstance(x, datetime.datetime)]
    col_list = [x for x in col_list if x not in report_produced_date]
    FOIA_request = [x for x in col_list if 'FOIA' in x][0]

    skip = np.where(df.iloc[:, 0].str.contains('Number', na=False))[0][0] \
        + add_skip

    df = pd.read_excel(input_file, skiprows=skip)

    df = df.dropna(how='all', axis=(0, 1))

    df.insert(0, 'CRID',
              (pd.to_numeric(df[original_crid_col],
                             errors='coerce')
               .fillna(method='ffill')
               .astype(int)))

    if notnull:
        df = df[df[notnull].notnull()]
    if isnull:
        df = df[df[isnull].isnull()]
    if drop_col_val:
        df = df[df[drop_col_val[0]] != drop_col_val[1]]
    if drop_col:
        df.drop(drop_col, axis=1, inplace=True)

    if original_crid_mixed:
        df = df[df[original_crid_col] != df['CRID'].astype(str)]
    else:
        df.drop(original_crid_col, axis=1, inplace=True)
    df.dropna(thresh=2, inplace=True)

    df = df.dropna(how='all', axis=(0, 1))

    return df, report_produced_date, FOIA_request


def standardize_columns(cols):
    ''' returns a list of column names that are standardized
        according to the column_dictionary file that
        contains all potential column names (first column)
        and their standardized values (second column)
    '''
    try:
        col_df = pd.read_csv("hand/column_dictionary.csv")
    except:
        print("Column dictionary not in directory.")
        col_df = pd.DataFrame()
    if not isinstance(cols, list):
        cols = cols.tolist()
    col_dict = dict(zip(col_df.ix[:, 0], col_df.ix[:, 1]))
    new_cols = [col_dict[col] for col in cols]
    return new_cols


def collect_metadata(df, infile, outfile, notes=0):
    ''' returns pandas dataframe of metadata about the input dataframe
        this includes unique values and non null values in each column,
        as well as the input and output file name, and any other notes
    '''
    buf = io.StringIO()
    df.info(buf=buf)
    s = buf.getvalue()
    info_values = [re.split("\\s\\s+", x) for x in s.split("\n")]
    info_values = [x for x in info_values if len(x) > 1]
    metadata_df = pd.DataFrame(info_values)
    metadata_df["In File"] = infile
    metadata_df["Out File"] = outfile
    metadata_df.columns = [
        "Column_Name", "Column_Info",
        "Original_Dataset", "Output_Dataset"
        ]

    metadata_df['Non_Null_Count'], metadata_df['Object_Type'] = \
        metadata_df['Column_Info'].str.split(' ', 1).str
    metadata_df["Object_Type"] = \
        metadata_df["Object_Type"].str.replace("non-null ", "")

    uniques_df = df.apply(lambda x: len(x.unique())).reset_index()
    uniques_df.columns = ["Column_Name", "Unique_Count"]
    metadata_df["Unique_Count"] = uniques_df["Unique_Count"]
    cols = [
        "Original_Dataset", "Output_Dataset",
        "Column_Name", "Non_Null_Count",
        "Unique_Count", "Object_Type"
        ]

    if isinstance(notes, pd.Series):
        metadata_df = metadata_df.join(notes.reset_index(drop=True))
        cols.append('Notes')
    metadata_df = metadata_df[cols]

    return metadata_df
