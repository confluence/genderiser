#!/usr/bin/env python

import unittest
import sys
import StringIO
import tempfile
import shutil
import errno
import os
from genderiser import Genderiser, main, GenderiserError

class TestGenderiser(unittest.TestCase):
    def setUp(self):
        self.stdout = StringIO.StringIO()
        sys.stdout = self.stdout

    def last_out(self, strip=True):
        out = self.stdout.getvalue()
        self.stdout = StringIO.StringIO()
        sys.stdout = self.stdout
        return out

    def test_preview(self):        
        main(["-p", "example"])
        expected_preview = """Alice.txt:
----------
You know a man called John Smith. He has a sister called Mary Jones.

Alice.odt:
----------
You know a man called John Smith. He has a sister called Mary Jones.

Alice.docx:
-----------
You know a man called John Smith. He has a sister called Mary Jones.

"""
        self.assertEquals(self.last_out(), expected_preview)

    def test_nothing_missing(self):
        main(["-m", "example"])
        self.assertEquals(self.last_out(), "\n")

    def test_bad_output_dir(self):
        self.assertRaises(GenderiserError, main, ["-o", "example", "example"])

    def test_subs(self):
        main(["-s", "example"])
        self.assertEquals(self.last_out(), "jones_child:daughter,jones_grandparent:grandmother,jones_name:Mary,jones_parent:mother,jones_parentsibling:aunt,jones_person:woman,jones_sibling:sister,jones_siblingchild:niece,jones_spouse:wife,jones_their:her,jones_theirs:hers,jones_them:her,jones_themselves:herself,jones_they:she,jones_youngperson:girl,smith_child:son,smith_grandparent:grandfather,smith_name:John,smith_parent:father,smith_parentsibling:uncle,smith_person:man,smith_sibling:brother,smith_siblingchild:nephew,smith_spouse:husband,smith_their:his,smith_theirs:his,smith_them:him,smith_themselves:himself,smith_they:he,smith_youngperson:boy\n")

    def test_missing_subs(self):
        try:
            test_project = tempfile.mkdtemp()

            with open(os.path.join(test_project, "test.cfg"), "w") as badconfig:
                badconfig.write("""
[files]
files=Alice.txt

[characters]
jones = female

[male]
jones_name = Mark

[female]
smith_name = Jane
jones_name = Mary
            """)
            
            with open(os.path.join(test_project, "Alice.txt"), "w") as alice:
                alice.write("You know a smith_person called smith_name Smith. Smith_they has a jones_sibling called jones_name Jones.")

            # TODO: change this temporary file into a context?
            
            main(["-m", test_project])

            self.assertEquals(self.last_out(), "smith_name,Smith_they,smith_person\n")
        finally:
            try:
                shutil.rmtree(test_project)
            except OSError as exc:
                if exc.errno != errno.ENOENT:
                    raise
        
    # TODO:
    # Same input and output dir
    # Various kinds of bad input
    # Bad file format


if __name__ == "__main__":
    unittest.main()
