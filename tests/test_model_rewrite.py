import unittest
from unittest.mock import patch
from app.services import rewrite_studio_service as service


class TestModelRewrite(unittest.TestCase):
    @patch.dict('os.environ', {'HULEX_REWRITE_PROVIDER': 'ollama'}, clear=True)
    @patch.object(service, '_model_rewrite', return_value='The team finished 42 tasks.')
    def test_revision(self, model):
        result = service.refine_text('The team completed 42 tasks.', 'Natural', 'Balanced')
        self.assertEqual(result['mode'], 'model_rewrite')
        self.assertEqual(result['rewritten_text'], 'The team finished 42 tasks.')

    @patch.dict('os.environ', {'HULEX_REWRITE_PROVIDER': 'ollama'}, clear=True)
    @patch.object(service, '_model_rewrite', return_value='The team completed 42 tasks.')
    def test_unchanged_rejected(self, model):
        with self.assertRaises(service.RewriteUnavailable):
            service.refine_text('The team completed 42 tasks.', 'Natural', 'Balanced')
        self.assertEqual(model.call_count, 2)

    def test_number_change(self):
        self.assertIsNotNone(service._revision_issue('Completed 42 tasks.', 'Finished 43 tasks.', 'Balanced'))

    def test_shorter(self):
        self.assertIsNotNone(service._revision_issue('We completed the task.', 'We have completed the task.', 'Shorter'))
