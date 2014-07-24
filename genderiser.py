#!/usr/bin/env python

import re
import ConfigParser

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
        output_dir = self.cp.get('default', 'output_dir')
        
        # do the replacements


