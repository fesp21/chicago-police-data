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
        'input_file': 'input/10655-FOIA-P046360-TRRdata.xlsx',
        'output_file': 'output/trr-officers.csv.gz',
        'metadata_file': 'output/metadata_trr-officers.csv.gz',
        'main_sheet': 'Sheet1',
        'star_sheet': 'Star #',
        'notes_sheet': 'Notes',
        'drop_column': 'SUBJECT_CB_NO',
        'main_keep_columns': [
            'TRR_REPORT_ID', 'POLAST', 'POFIRST', 'POGNDR',
            'PORACE', 'POAGE', 'APPOINTED_DATE', 'UNITASSG',
            'UNITDETAIL', 'ASSGNBEAT', 'RANK', 'DUTYSTATUS',
            'POINJURED', 'MEMBER_IN_UNIFORM'
            ]
        }

    assert args['input_file'].startswith('input/'),\
        "input_file is malformed: {}".format(args['input_file'])
    assert (args['output_file'].startswith('output/') and
            args['output_file'].endswith('.csv.gz')),\
        "output_file is malformed: {}".format(args['output_file'])

    return setup.do_setup(script_path, args)


cons, log = get_setup()

notes_df = pd.read_excel(cons.input_file, sheetname=cons.notes_sheet,
                         header=None)
notes = '\n'.join(notes_df.ix[notes_df[0].isin([cons.main_sheet,
                                                cons.star_sheet]),
                              1].dropna())
cons.write_yamlvar('Notes', notes)

main_df = pd.read_excel(cons.input_file, sheetname=cons.main_sheet)
main_df = main_df.drop(cons.drop_column, axis=1)
main_df = main_df[cons.main_keep_columns]
main_df.columns = standardize_columns(main_df.columns)

star_df = pd.read_excel(cons.input_file, sheetname=cons.star_sheet)
star_df.columns = standardize_columns(star_df.columns)

df = main_df.merge(star_df,
                   how='outer',
                   on=list(set(main_df.columns) &
                           set(star_df.columns)))

assert (main_df.shape[0] == df.shape[0] and
        star_df.shape[0] == df.shape[0]),\
        print('Incorrect row counts, check merging')

df.to_csv(cons.output_file, **cons.csv_opts)

meta_df = collect_metadata(df, cons.input_file, cons.output_file)
meta_df.to_csv(cons.metadata_file, **cons.csv_opts)
