#!/usr/bin/env python

import re
import os
import sys
import glob
import ConfigParser
import StringIO
import argparse

class Genderiser(object):

    def __init__(self):
        self.cp = ConfigParser.SafeConfigParser()
        self.substitutions = {}

    def read_config(self, *files, **kwargs):
        if 'text' in kwargs:
            self.cp.readfp(StringIO.StringIO(kwargs['text']))
        else:
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

    def replace(self, *files, **kwargs):
        output_dir = kwargs.get('output_dir', 'output')
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

    def subs_as_text(self):
        pass
         

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace placeholder variables with gendered words in text files")
    parser.add_argument("dir", help="Directory of files to process")
    parser.add_argument("-d", "--config-dir", help="Directory with your custom configuration files. By default the directory with files to be processed will be used.")
    parser.add_argument("-o", "--output-dir", default="output", help="Directory to which modified files will be written.")
    parser.add_argument("-c", "--config", help="String containing custom config to be used. Replaces the custom config directory.")
    parser.add_argument("-s", "--subs-only", help="Don't process any files; just output a list of substitutions", action="store_true")
    parser.add_argument("-v", "--verbose", help="Turn on verbose output", action="count")

    args = parser.parse_args()

    gen = Genderiser()

    if args.config:
        gen.read_config(text=args.config)
    elif args.config_dir:
        gen.read_config('config', os.path.join(args.config_dir,'config'))
    elif args.dir:
        gen.read_config('config', os.path.join(args.dir,'config'))
    elif not args.subs_only:
        print "No project directory specified. Exiting."
        sys.exit(1)

    if args.subs_only:
        print gen.subs_as_text()
    elif args.dir:
        files = glob.glob(os.path.join(args.dir, '*.txt'))
        gen.replace(output_dir, *files, **{'output_dir': args.output_dir})
    
