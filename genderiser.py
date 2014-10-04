#!/usr/bin/env python

import re
import zipfile
import os
import glob
import sys
import ConfigParser
import StringIO
import argparse
import tempfile

class GenderiserError(Exception):
    pass


class FileHelper(object):
    def __init__(self, inpath, inputdir):
        self.inpath = inpath
        self.inputdir = inputdir
        self.filename = os.path.relpath(inpath, inputdir)

        self.text = None

    def read(self):
        raise NotImplementedError()

    def plain_text(self):
        raise NotImplementedError()
        
    def write(self, outputdir):
        raise NotImplementedError()

    @classmethod
    def get_helper(cls, inpath, inputdir):
        if zipfile.is_zipfile(inpath):
            with zipfile.ZipFile(inpath, "r") as zipped_infile:
                filelist = zipped_infile.infolist()

            for ziphelper in (OdtFileHelper, DocxFileHelper):
                if ziphelper.CONTENTFILE in [f.filename for f in filelist]:
                    return ziphelper(inpath, inputdir)
            raise GenderiserError("Unable to detect file type of %r." % inpath)
        else:
            return TextFileHelper(inpath, inputdir)
             


class TextFileHelper(FileHelper):
    def read(self):
        with open(self.inpath, "r") as infile:
            self.text = infile.read()

    def plain_text(self):
        return self.text
        
    def write(self, outputdir):
        outpath = os.path.join(outputdir, self.filename)
        
        outfiledir = os.path.dirname(outpath)                
        if not os.path.exists(outfiledir):
            os.makedirs(outfiledir)

        with open(outpath, "w") as outfile:
            outfile.write(self.text)


class ZippedXMLFileHelper(FileHelper):
    XML_TAG = re.compile("<[^>]*>")

    def read(self):
        with zipfile.ZipFile(self.inpath, "r") as zipped_infile:
            self.text = zipped_infile.read(self.CONTENTFILE)

    def plain_text(self):
        return self.XML_TAG.sub("", self.text)
        
    def write(self, outputdir):
        outpath = os.path.join(outputdir, self.filename)
        
        outfiledir = os.path.dirname(outpath)                
        if not os.path.exists(outfiledir):
            os.makedirs(outfiledir)

        # Surprisingly hard. Decompress the zip, overwrite content.xml, recompress the zip to a new location.

        unzipped_tempdir = tempfile.mkdtemp()

        with zipfile.ZipFile(self.inpath, "r") as zipped_infile:
            zipped_infile.extractall(unzipped_tempdir)
            filelist = zipped_infile.infolist()

        with open(os.path.join(unzipped_tempdir, self.CONTENTFILE), "w") as outfile:
            outfile.write(self.text)

        with zipfile.ZipFile(outpath, "w") as zipped_outfile:
            for fileinfo in filelist:
                filepath = fileinfo.filename
                datapath = os.path.join(unzipped_tempdir, filepath)
                zipped_outfile.write(datapath, filepath)


class OdtFileHelper(ZippedXMLFileHelper):
    CONTENTFILE = "content.xml"


class DocxFileHelper(ZippedXMLFileHelper):
    CONTENTFILE = "word/document.xml"


class Genderiser(object):

    builtin_config = """
[main]
# The regular expression to be used for variables. Must contain at least two groups: one for the character identifier and one for the word identifier. The default regular expression matches variables of the form surname_word:
variable_regex = ([A-Za-z]+)_([A-Za-z]+)

[genders]
# This section lists valid genders. Each key must be the name of a section in which a word list for a gender is defined. Values are ignored.
male =
female =

[male]
# Pronouns
they = he
them = him
their = his
theirs = his
themselves = himself
# Common gendered words
person = man
youngperson = boy
parent = father
grandparent = grandfather
sibling = brother
siblingchild = nephew
parentsibling = uncle
child = son
spouse = husband

[female]
# Pronouns
they = she
them = her
their = her
theirs = hers
themselves = herself
# Common gendered words
person = woman
youngperson = girl
parent = mother
grandparent = grandmother
sibling = sister
siblingchild = niece
parentsibling = aunt
child = daughter
spouse = wife
"""

    def __init__(self, project_dir=None, config_text=None):
        self.cp = ConfigParser.SafeConfigParser()

        self.subs = {}
        self.files = []

        # Read the default config
        self.cp.readfp(StringIO.StringIO(self.builtin_config))

        # Read config files from the project directory
        if project_dir is not None:
            self.project_dir = project_dir
            self.cp.read(glob.glob(os.path.join(project_dir, "*.cfg")))

        # Read config from commandline parameter
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
                if key.startswith("%s_" % surname): # special variable for this character
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
                self.files.append(FileHelper.get_helper(os.path.join(self.project_dir, filename), self.project_dir))

            if self.cp.has_option("files", "glob"):
                expanded = glob.glob(os.path.join(self.project_dir, self.cp.get("files", "glob")))
                for filepath in expanded:
                    self.files.append(FileHelper.get_helper(filepath, self.project_dir))

        if not self.files:
            raise GenderiserError("No files found.")

    def replace(self, output_dir=None, preview=False):
        self.find_files()

        if output_dir is None:
            output_dir = os.path.join(self.project_dir, "output")

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

        for filehelper in self.files:
            # Read content
            filehelper.read()

            # Replace variables
            filehelper.text = self.variable_regex.sub(var_sub, filehelper.text)

            # Print a preview to stdout
            if preview:
                print "%s:" % filehelper.filename
                print "-" * (len(filehelper.filename) + 1)
                print filehelper.plain_text().strip()
                print ""

            # Otherwise try to write to a file
            elif output_dir is not None:
                filehelper.write(output_dir)

    def substitutions(self):
        print ",".join("%s:%s" % (k, v) for (k, v) in sorted(self.subs.iteritems()))

    def missing(self):
        self.find_files()
        variables_used = set()

        for filehelper in self.files:
            filehelper.read()
            for surname, word in self.variable_regex.findall(filehelper.plain_text()):
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
