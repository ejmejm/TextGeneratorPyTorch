#!/usr/bin/env python3

import sys
import subprocess

print('Starting download...')

subprocess.call(['python3', 'generate.py', sys.argv[1], \
		sys.argv[2], sys.argv[3], sys.argv[4]])

print('Parsing data...')

subprocess.call(['python3', 'format_data.py'])

print('Deleting temporary intermediate files...')

subprocess.call(['rm', '-rf', 'tmp_output_dump'])
