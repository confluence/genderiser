#!/usr/bin/env python

import re
import os
import glob
import sys
import ConfigParser
import StringIO
import argparse

class GenderiserError(Exception):
    pass

class Genderiser(object):

    def __init__(self):
        self.cp = ConfigParser.SafeConfigParser()
        self.subs = {}
        self.missing = set()

    def read_config(self, project_dir=None, config_text=None):
        files = ["genderiser.cfg"]
        if project_dir is not None:
            files.extend(glob.glob(os.path.join(project_dir, "*.cfg")))
        self.cp.read(files)
        
        if config_text is not None:
            self.cp.readfp(StringIO.StringIO(config_text))
        
        for surname, gender in self.cp.items("characters"):
            if gender not in self.cp.options("genders"):
                raise ValueError("%r is not listed in the genders configuration section." % gender)

            if gender not in self.cp.sections():
                raise ValueError("No configuration section found for gender %r." % gender)

            for key, value in self.cp.items(gender):
                if "_" in key and key.startswith(surname): # special variable for this character
                    self.subs[key] = value
                elif "_" in key: # special variable for a different character
                    continue
                else: # generic word
                    self.subs["%s_%s" % (surname, key)] = value

    def replace(self, project_dir, output_dir=None, preview=False):
        files = []

        for filename in self.cp.get("files", "files").split(","):
            files.append(filename.strip())

        if self.cp.has_option("files", "glob"):
            files.extend(glob.glob(self.cp.get("files", "glob")))

        if output_dir is None:
            output_dir = os.path.join(project_dir, "output")
        
        if not preview and os.path.exists(output_dir):
            os.makedirs(output_dir)

        variable_regex = self.cp.get("main", "variable_regex")
        key_error_mode = self.cp.get("main", "key_error_mode")

        VAR = re.compile(variable_regex)

        def var_sub(m):
            surname, word = m.groups()
            key = "%s_%s" % (surname.lower(), word.lower())
            replacement = self.subs.get(key)
            if replacement:
                if surname == surname.capitalize():
                    return replacement.capitalize()
                return replacement
            elif key_error_mode == "quiet":
                return word
            else:
                return "UNKNOWN"

        for i, filename in enumerate(files):
            with open(os.path.join(project_dir, filename), "r") as infile:
                text = infile.read()
                text = VAR.sub(var_sub, text)

                # print a preview to stdout
                if preview is not None:
                    preview.write(text)

                # otherwise try to write to a file
                elif output_dir is not None:
                    outfilename = os.path.join(output_dir, filename)

                    new_file_dir = os.path.dirname(filename)
                    if not os.path.exists(new_file_dir):
                        os.makedirs(new_file_dir)

                    with open(outfilename, "w") as outfile:
                        outfile.write(text)

    def subs_as_text(self):
        return ",".join("%s:%s" % (k, v) for (k, v) in self.subs.iteritems())

    def missing_as_text(self):
        return ",".join(m for m in self.missing)

    def from_args(self, args):
        self.read_config(args.dir, args.config)

        if args.substitutions:
            print self.subs_as_text()

        elif args.missing:
            print self.missing_as_text()

        elif args.dir:
            output_dir = args.output_dir if not args.no_output else None
            preview = sys.stdout if args.preview else None
            self.replace(args.dir, output_dir, preview)
        else:
            raise GenderiserError("No project specified and nothing to do.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace placeholder variables with gendered words in text files")
    parser.add_argument("dir", help="Project directory to process", nargs="?", default=None)
    parser.add_argument("-o", "--output-dir", default="output", help="Directory to which modified files will be written. By default a directory named 'output' will be created in the project directory.")
    parser.add_argument("-c", "--config", help="String containing custom config to be used. May be used in addition to or instead of a project directory.", default=None)
    parser.add_argument("-s", "--substitutions", help="Suppress all other output and print a list of substitutions.", action="store_true")
    parser.add_argument("-p", "--preview", help="Suppress all other output and print the modified file contents to standard output.", action="store_true")
    parser.add_argument("-m", "--missing", help="Suppress all other output and print a list of variables for which no replacements could be found.", action="store_true")

    args = parser.parse_args()

    gen = Genderiser()
    gen.from_args(args)


        
    
