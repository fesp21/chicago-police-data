import pandas as pd
import __main__

from import_functions import standardize_columns, collect_metadata
import setup


def get_setup():
    ''' encapsulates args.
        calls setup.do_setup() which returns constants and logger
        constants contains args and a few often-useful bits in it
        including constants.write_yamlvar()
        logger is used to write logging messages
    '''
    script_path = __main__.__file__
    args = {
        'input_files': [
                        'input/Part_1.xlsx',
                        'input/Part_2.xlsx',
                        'input/Part_3.xlsx',
                        'input/Part_4.xlsx',
                        'input/Part_5.xlsx',
                        'input/Part_6.xlsx'
                       ],
        'output_file': 'output/awards.csv.gz',
        'metadata_file': 'output/metadata_awards.csv.gz'
        }

    assert all(input_file.startswith('input/')
               for input_file in args['input_files']),\
        "An input_file is malformed: {}".format(args['input_files'])
    assert (args['output_file'].startswith('output/') and
            args['output_file'].endswith('.csv.gz')),\
        "output_file is malformed: {}".format(args['output_file'])

    return setup.do_setup(script_path, args)


cons, log = get_setup()

data_df = pd.DataFrame()
meta_df = pd.DataFrame()

column_names = []
total_rows = 0

for input_file in cons.input_files:
    if column_names:
        df = pd.read_excel(input_file, header=None)
    else:
        df = pd.read_excel(input_file)
        column_names = standardize_columns(df.columns)

    total_rows += df.shape[0]

    df.columns = column_names

    data_df = (data_df
               .append(df)
               .reset_index(drop=True))

    meta_df = (meta_df
               .append(collect_metadata(df, input_file, cons.output_file))
               .reset_index(drop=True))

assert total_rows == data_df.shape[0],\
        print(('Total Rows ({0}) must equal '
               'appended rows ({1})').format(total_rows, data_df.shape[0]))

data_df.to_csv(cons.output_file, **cons.csv_opts)

meta_df.to_csv(cons.metadata_file, **cons.csv_opts)
