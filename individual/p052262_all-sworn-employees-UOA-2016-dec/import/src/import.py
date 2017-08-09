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
        'input_file':
        'input/FOIA_P052262_-_11221-FOIA-P052262-AllSwornEmployeesWithUOA.xlsx',
        'output_file': 'output/all-sworn-units.csv.gz',
        'metadata_file': 'output/metadata_all-sworn-units.csv.gz'
        }

    assert args['input_file'].startswith('input/'),\
        "input_file is malformed: {}".format(args['input_file'])
    assert (args['output_file'].startswith('output/') and
            args['output_file'].endswith('.csv.gz')),\
        "output_file is malformed: {}".format(args['output_file'])

    return setup.do_setup(script_path, args)


cons, log = get_setup()

notes_df = pd.read_excel(cons.input_file, sheetname=0)
notes = '\n'.join(notes_df.ix[:, 0].dropna())
cons.write_yamlvar('Notes', notes)

df = pd.read_excel(cons.input_file, sheetname=1)
df.columns = standardize_columns(df.columns)
df.to_csv(cons.output_file, **cons.csv_opts)

meta_df = collect_metadata(df, cons.input_file, cons.output_file)
meta_df.to_csv(cons.metadata_file, **cons.csv_opts)
