import unittest
import sys
import StringIO
from genderiser import Genderiser, main

class TestGenderiser(unittest.TestCase):
    def setUp(self):
        self.stdout = StringIO.StringIO()
        sys.stdout = self.stdout

        self.expected_alice = "You know a man called John Smith. He has a sister called Mary Jones."

        self.expected_subs = {"smith_their": "his", "jones_sibling": "sister", "smith_they": "he", "smith_name": "John", "jones_they": "she", "smith_themselves": "himself", "jones_person": "woman", "smith_sibling": "brother", "jones_their": "her", "jones_themselves": "herself", "smith_them": "him", "jones_theirs": "hers", "jones_name": "Mary", "jones_them": "her", "smith_theirs": "his", "smith_person": "man"}

        self.expected_subs_str = "jones_child:daughter,jones_grandparent:grandmother,jones_name:Mary,jones_parent:mother,jones_parentsibling:aunt,jones_person:woman,jones_sibling:sister,jones_siblingchild:niece,jones_spouse:wife,jones_their:her,jones_theirs:hers,jones_them:her,jones_themselves:herself,jones_they:she,jones_youngperson:girl,smith_child:son,smith_grandparent:grandfather,smith_name:John,smith_parent:father,smith_parentsibling:uncle,smith_person:man,smith_sibling:brother,smith_siblingchild:nephew,smith_spouse:husband,smith_their:his,smith_theirs:his,smith_them:him,smith_themselves:himself,smith_they:he,smith_youngperson:boy"
    
    def last_out(self, strip=True):
        out = self.stdout.getvalue().strip()
        self.stdout = StringIO.StringIO()
        sys.stdout = self.stdout
        return out

    def test_preview(self):        
        main(["-p", "example"])
        self.assertEquals(self.last_out(), self.expected_alice)

    def test_nothing_missing(self):
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
smith_name = John
jones_name = Mark

[female]
smith_name = Jane
jones_name = Mary
        """.replace("\n","\\n")
        
        main(["-s", "-c", text_config])
        
        self.assertEquals(self.last_out(), self.expected_subs_str)

    # TODO: bad config and input tests


if __name__ == "__main__":
    unittest.main()
