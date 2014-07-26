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

    def __init__(self, project_dir=None, config_text=None):
        self.cp = ConfigParser.SafeConfigParser()

        self.subs = {}
        self.files = []

        config_files = ["genderiser.cfg"]
        if project_dir is not None:
            self.project_dir = project_dir
            config_files.extend(glob.glob(os.path.join(project_dir, "*.cfg")))
        self.cp.read(config_files)
        
        if config_text is not None:
            self.cp.readfp(StringIO.StringIO(config_text.replace("\\n", "\n")))

        self.create_subs()

        self.variable_regex = re.compile(self.cp.get("main", "variable_regex"))

    def create_subs(self):
        for surname, gender in self.cp.items("characters"):
            if gender not in self.cp.options("genders"):
                raise GenderiserError("%r is not listed in the genders configuration section." % gender)

            if gender not in self.cp.sections():
                raise GenderiserError("No configuration section found for gender %r." % gender)

            for key, value in self.cp.items(gender):
                if "_" in key and key.startswith(surname): # special variable for this character
                    self.subs[key] = value
                elif "_" in key: # special variable for a different character
                    continue
                else: # generic word
                    self.subs["%s_%s" % (surname, key)] = value

    def find_files(self):
        if not self.project_dir:
            raise GenderiserError("No project directory specified.")

        if self.cp.has_section("files"):

            for filename in self.cp.get("files", "files").split(","):
                self.files.append(filename.strip())

            if self.cp.has_option("files", "glob"):
                self.files.extend(glob.glob(self.cp.get("files", "glob")))

        if not self.files:
            raise GenderiserError("No files found.")

    def replace(self, output_dir=None, preview=False):
        self.find_files()

        if output_dir is None:
            output_dir = os.path.join(self.project_dir, "output")
        
        if not preview and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        def var_sub(m):
            surname, word = m.groups()
            key = "%s_%s" % (surname.lower(), word.lower())
            replacement = self.subs.get(key)
            if replacement:
                if surname == surname.capitalize():
                    return replacement.capitalize()
                return replacement
            else:
                return "UNKNOWN"

        for filename in self.files:
            with open(os.path.join(self.project_dir, filename), "r") as infile:
                text = infile.read()
                text = self.variable_regex.sub(var_sub, text)

                # print a preview to stdout
                if preview is not None:
                    print text

                # otherwise try to write to a file
                elif output_dir is not None:
                    outfilename = os.path.join(output_dir, filename)

                    outfiledir = os.path.dirname(outfilename)
                    
                    if not os.path.exists(outfiledir):
                        os.makedirs(outfiledir)

                    with open(outfilename, "w") as outfile:
                        outfile.write(text)

    def substitutions(self):
        print ",".join("%s:%s" % (k, v) for (k, v) in sorted(self.subs.iteritems()))

    def missing(self):
        self.find_files()
        variables_used = set()

        for filename in self.files:
            with open(os.path.join(self.project_dir, filename), "r") as infile:
                for surname, word in self.variable_regex.findall(infile.read()):
                    variables_used.add("%s_%s" % (surname, word))

        missing_variables = variables_used - set(self.subs) - set(s.capitalize() for s in self.subs)

        print ",".join(m for m in missing_variables)

    @classmethod
    def create_from(cls, args):
        return cls(args.project_dir, args.config)

    def process(self, args):
        if args.substitutions:
            self.substitutions()

        else:
            if args.missing:
                self.missing()

            else:
                output_dir = args.output_dir if not args.preview else None
                self.replace(output_dir, args.preview)


def main(args=None):
    parser = argparse.ArgumentParser(description="Replace placeholder variables with gendered words in text files")
    parser.add_argument("-o", "--output-dir", help="Directory to which modified files will be written. By default a directory named 'output' will be created in the project directory.")

    parser.add_argument("project_dir", help="Project directory to process", nargs="?", default=None)
    parser.add_argument("-c", "--config", help="String containing project config. To be used from an external replacement program with -s. Newlines must be escaped with literal \\n.", default=None)

    action = parser.add_mutually_exclusive_group(required=False)
    action.add_argument("-s", "--substitutions", help="Suppress all other output and print a list of substitutions.", action="store_true")
    action.add_argument("-p", "--preview", help="Suppress all other output and print the modified file contents to standard output.", action="store_true")
    action.add_argument("-m", "--missing", help="Suppress all other output and print a list of variables for which no replacements could be found.", action="store_true")

    args = parser.parse_args(args)

    if not (args.project_dir or args.config):
        parser.print_usage()
        print "genderiser.py: error: one of project_dir and -c/--config is required"
        return 1

    elif not (args.project_dir or args.substitutions):
        parser.print_usage()
        print "genderiser.py: error: one of project_dir and -s/--substitutions is required"
        return 1

    gen = Genderiser.create_from(args)
    gen.process(args)


if __name__ == "__main__":
    returnval = main()
    if returnval:
        sys.exit(returnval)
