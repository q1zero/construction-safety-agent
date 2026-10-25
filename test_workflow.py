import unittest
from workflow import STAGES, create_session, submit, export_markdown

class WorkflowTests(unittest.TestCase):
    def test_out_of_order_stage_is_rejected_without_mutating_state(self):
        session = create_session('Example only')
        with self.assertRaises(ValueError):
            submit(session, {'stage': 'outline', 'data': {'sections': ['example']}}, 'reviewer')
        self.assertEqual(session['stages'], [])

    def test_review_and_required_fields_are_enforced(self):
        session = create_session('Example only')
        for payload, reviewer in [({'stage': 'risk_intake', 'data': {}}, 'reviewer'),
                                   ({'stage': 'risk_intake', 'data': {'work_description': 'x',
                                     'assessed_risk': 'human supplied'}}, '')]:
            with self.assertRaises(ValueError):
                submit(session, payload, reviewer)

    def test_incomplete_session_cannot_export(self):
        with self.assertRaises(ValueError):
            export_markdown(create_session('Example only'))

    def test_complete_session_exports_supplied_evidence_and_reviewer(self):
        session = create_session('Example only — no real site instructions')
        for key, _, fields in STAGES:
            session = submit(session, {'stage': key, 'data': {field: ['REVIEWED EXAMPLE']
                             for field in fields}}, 'Example reviewer')
        self.assertEqual(session['status'], 'reviewed')
        report = export_markdown(session)
        self.assertIn('Example reviewer', report)
        self.assertIn('REVIEWED EXAMPLE', report)
        with self.assertRaises(ValueError):
            submit(session, {}, 'reviewer')

if __name__ == '__main__':
    unittest.main()
