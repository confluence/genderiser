import unittest
import sys
import StringIO
from genderiser import Genderiser, main

class TestGenderiser(unittest.TestCase):
    def setUp(self):
        self.stdout = StringIO.StringIO()
        sys.stdout = self.stdout
    
    def test_config(self):
        expected_substitutions = {
            "jones_name": "Mary",
            "jones_person": "woman",
            "jones_sibling": "sister",
            "jones_their": "her",
            "jones_theirs": "hers",
            "jones_them": "her",
            "jones_themselves": "herself",
            "jones_they": "she",
            "smith_name": "John",
            "smith_person": "man",
            "smith_sibling": "brother",
            "smith_their": "his",
            "smith_theirs": "his",
            "smith_them": "him",
            "smith_themselves": "himself",
            "smith_they": "he",
        }

        g = Genderiser("example")
        self.assertEqual(g.subs, expected_substitutions)

    def test_parsing(self):
        expected_output = "You know a man called John Smith. He has a sister called Mary Jones."
        
        g = Genderiser("example")
        g.replace(None, preview=True)
        self.assertEqual(self.stdout.getvalue().strip(), expected_output)

    def test_not_missing(self):
        g = Genderiser("example")
        g.missing()
        self.assertEqual(self.stdout.getvalue().strip(), "")

    def test_subs(self):
        g = Genderiser("example")
        g.substitutions()
        self.assertEqual(self.stdout.getvalue().strip(), "jones_name:Mary,jones_person:woman,jones_sibling:sister,jones_their:her,jones_theirs:hers,jones_them:her,jones_themselves:herself,jones_they:she,smith_name:John,smith_person:man,smith_sibling:brother,smith_their:his,smith_theirs:his,smith_them:him,smith_themselves:himself,smith_they:he")

    def test_parameters(self):
        pass

    def test_missing(self):
        pass

    # TODO: bad config tests


if __name__ == "__main__":
    unittest.main()
