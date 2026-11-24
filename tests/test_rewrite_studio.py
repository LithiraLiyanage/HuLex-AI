"""Run from project root: cd backend; python -m unittest discover -s ../tests -v"""
import unittest
from app.services.rewrite_studio_service import local_polish


class TestLocalPolish(unittest.TestCase):
    def test_reduces_padding(self):
        result = local_polish('In order to write clearly, we should practice.', 'Natural', 'Balanced')
        self.assertEqual(result, 'To write clearly, we should practice.')

    def test_preserves_numbers(self):
        text = 'It is important to note that 2026 had 42 participants.'
        result = local_polish(text, 'Natural', 'Balanced')
        self.assertIn('2026', result)
        self.assertIn('42', result)

    def test_plain_text_unchanged(self):
        text = 'The team delivered the report on Friday.'
        self.assertEqual(local_polish(text, 'Natural', 'Balanced'), text)


if __name__ == '__main__':
    unittest.main()
