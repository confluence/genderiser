import unittest
import os
from genderiser import Genderiser

class TestGenderiser(unittest.TestCase):
    def test_config(self):
        expected_substitutions = {
            'jones_name': 'Mary',
            'jones_person': 'woman',
            'jones_sibling': 'sister',
            'jones_their': 'her',
            'jones_theirs': 'hers',
            'jones_them': 'her',
            'jones_themselves': 'herself',
            'jones_they': 'she',
            'smith_name': 'John',
            'smith_person': 'man',
            'smith_sibling': 'brother',
            'smith_their': 'his',
            'smith_theirs': 'his',
            'smith_them': 'him',
            'smith_themselves': 'himself',
            'smith_they': 'he',
        }

        g = Genderiser()
        g.read_config('config', os.path.join('example','config'))
        self.assertEqual(g.substitutions, expected_substitutions)

    def test_parsing(self):
        expected_output = "You know a man called John Smith. He has a sister called Mary Jones."
        
        g = Genderiser()
        g.read_config('config', os.path.join('example','config'))
        output = "".join(line for line in g.replace(None, os.path.join('example','Alice.txt'))).strip()
        self.assertEqual(output, expected_output)


if __name__ == '__main__':
    unittest.main()
