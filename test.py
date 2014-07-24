import unittest
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
        g.read_config('config', 'example/config')
        self.assertEqual(g.substitutions, expected_substitutions)

    def test_parsing(self):
        g = Genderiser()
        g.read_config('config', 'example/config')
        g.parse('example/Alice.txt')


if __name__ == '__main__':
    unittest.main()
