import unittest
from StringIO import StringIO
from genderiser import Genderiser

class TestGenderiser(unittest.TestCase):
    def test_substitutions(self):
        expected_substitutions = {
            'jones_sibling': 'sister',
            'smith_sibling': 'brother',
            'smith_them': 'him',
            'smith_they': 'he',
            'smith_their': 'his',
            'smith_name': 'John',
            'jones_their': 'her',
            'jones_themselves': 'herself',
            'jones_they': 'she',
            'jones_theirs': 'hers',
            'jones_them': 'her',
            'jones_name': 'Mary',
            'smith_themselves': 'himself',
            'smith_theirs': 'his',
        }
        g = Genderiser()
        g.read_config('config', 'example/config')
        self.assertEqual(g.substitutions, expected_substitutions)


if __name__ == '__main__':
    unittest.main()
