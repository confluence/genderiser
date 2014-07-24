#!/usr/bin/env python

import re
import os
import ConfigParser
import argparse

class Genderiser(object):

    def __init__(self):
        self.cp = ConfigParser.SafeConfigParser()
        self.substitutions = {}

    def read_config(self, *files):
        self.cp.read(files)
        
        for surname, gender in self.cp.items('characters'):
            if gender not in self.cp.options('genders'):
                raise ValueError('%r is not listed in the genders configuration section.' % gender)

            if gender not in self.cp.sections():
                raise ValueError('No configuration section found for gender %r.' % gender)

            for key, value in self.cp.items(gender):
                if '_' in key and key.startswith(surname): # special variable for this character
                    self.substitutions[key] = value
                elif '_' in key: # special variable for a different character
                    continue
                else: # generic word
                    self.substitutions['%s_%s' % (surname, key)] = value

    def parse(self, *files):
        output_dir = self.cp.get('main', 'output_dir')
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        variable_regex = self.cp.get('main', 'variable_regex')
        key_error_mode = self.cp.get('main', 'key_error_mode')

        VAR = re.compile(variable_regex)

        def var_sub(m):
            surname, word = m.groups()
            sub = self.substitutions.get('%s_%s' % (surname.lower(), word.lower()))
            if sub:
                if surname != surname.lower():
                    return sub.capitalize()
                return sub
            elif key_error_mode == 'quiet':
                return word
            else:
                return 'UNKNOWN'

        for filename in files:
            with open(filename, 'r') as infile:
                outfilename = os.path.join(output_dir, os.path.basename(filename))
                with open(outfilename, 'w') as outfile:
                    for line in infile:
                        line = VAR.sub(var_sub, line)
                        outfile.write(line)

    @classmethod
    def launch_from_args(cls, args):
        pass
        # process the args here
         

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace placeholder variables with gendered words in text files")
    parser.add_argument("dir", help="Directory of files to process")
    parser.add_argument("-d", "--config-dir", help="Directory with your custom configuration files. By default the directory with files to be processed will be used.")
    parser.add_argument("-c", "--config", help="String containing custom config to be used. Replaces the custom config directory.")
    # todo: list subs only
    parser.add_argument("-v", "--verbose", help="Turn on verbose output", action="count")

    args = parser.parse_args()
    
