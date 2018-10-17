from __future__ import print_function

import os
import pickle
import sys
import pandas as pd

PYTHON_3 = sys.version_info >= (3, 0)

def read():
    sample_freq = 20
    curr_count = 0
    data_list = []
    df = pd.DataFrame(columns=['headline'])   
    for ls in os.listdir('tmp_output_dump'):
        if ls.endswith('.pkl'):
            with open('tmp_output_dump/' + ls, 'rb') as f:
                if PYTHON_3:
                    data = pickle.load(f, encoding='latin1')
                else:
                    data = pickle.load(f)
                for datum in data:
                    if curr_count == sample_freq:
                        df.loc[datum['ts']] = datum['title']
                        curr_count = 0
                    else:
                        curr_count += 1
    df.to_csv('reuters_ts_headline.csv')

if __name__ == '__main__':
    read()
