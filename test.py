import unittest
import sys
import StringIO
from genderiser import Genderiser, main

class TestGenderiser(unittest.TestCase):
    def setUp(self):
        self.stdout = StringIO.StringIO()
        sys.stdout = self.stdout

        self.expected_alice = "You know a man called John Smith. He has a sister called Mary Jones."

        self.expected_subs = {
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

        self.expected_subs_str = "jones_name:Mary,jones_person:woman,jones_sibling:sister,jones_their:her,jones_theirs:hers,jones_them:her,jones_themselves:herself,jones_they:she,smith_name:John,smith_person:man,smith_sibling:brother,smith_their:his,smith_theirs:his,smith_them:him,smith_themselves:himself,smith_they:he"
    
    def last_out(self, strip=True):
        out = self.stdout.getvalue().strip()
        self.stdout = StringIO.StringIO()
        sys.stdout = self.stdout
        return out

    def test_config(self):
        g = Genderiser("example")
        self.assertEquals(g.subs, self.expected_subs)

    def test_parsing(self):        
        main(["-p", "example"])
        self.assertEquals(self.last_out(), self.expected_alice)

    def test_not_missing(self):
        main(["-m", "example"])
        self.assertEquals(self.last_out(), "")

    def test_subs(self):
        main(["-s", "example"])
        self.assertEquals(self.last_out(), self.expected_subs_str)

    def test_pass_text_config(self):
        text_config = """
[characters]
smith = male
jones = female

[male]
sibling = brother
person = man
smith_name = John
jones_name = Mark

[female]
sibling = sister
person = woman
smith_name = Jane
jones_name = Mary
        """.replace("\n","\\n")
        
        main(["-s", "-c", text_config])
        
        self.assertEquals(self.last_out(), self.expected_subs_str)

    # TODO: bad config and input tests


if __name__ == "__main__":
    unittest.main()
