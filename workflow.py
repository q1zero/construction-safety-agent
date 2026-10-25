"""Six-stage workflow reference. No automatic construction safety decisions."""
import argparse
import json
from pathlib import Path

STAGES = (
    ('risk_intake', 'Work identification and assessed risk', ('work_description', 'assessed_risk')),
    ('clarification', 'Missing information and clarification', ('questions', 'answers')),
    ('checklist', 'Reviewed safety checklist', ('items', 'evidence')),
    ('outline', 'Work plan outline', ('sections',)),
    ('risk_matrix', 'Risk and mitigation matrix', ('rows',)),
    ('wbs_report', 'WBS and report', ('tasks', 'report_sections')),
)

def create_session(description):
    if not description.strip():
        raise ValueError('A work description is required')
    return {'schema_version': 1, 'description': description, 'stages': [], 'status': 'in_progress'}

def submit(session, payload, reviewer):
    """Accept only human-reviewed structured material, one stage at a time."""
    index = len(session['stages'])
    if index >= len(STAGES):
        raise ValueError('All stages are already completed')
    key, title, fields = STAGES[index]
    if not reviewer.strip():
        raise ValueError('A named human reviewer is required')
    if not isinstance(payload, dict) or payload.get('stage') != key:
        raise ValueError('Expected stage: ' + key)
    data = payload.get('data')
    if not isinstance(data, dict) or any(field not in data or not data[field] for field in fields):
        raise ValueError('Required nonempty fields: ' + ', '.join(fields))
    # Copy before changing state so rejected input never advances the workflow.
    result = json.loads(json.dumps(session))
    result['stages'].append({'stage': key, 'title': title, 'data': data, 'reviewer': reviewer})
    if len(result['stages']) == len(STAGES):
        result['status'] = 'reviewed'
    return result

def export_markdown(session):
    if session['status'] != 'reviewed' or len(session['stages']) != len(STAGES):
        raise ValueError('Export requires human review of all six stages')
    lines = ['# Construction Safety Workflow — Research Example', '',
             'This artifact organizes supplied material; it is not a safety certification.', '',
             session['description'], '']
    for item in session['stages']:
        lines += ['## ' + item['title'], '', 'Reviewer: ' + item['reviewer'], '',
                  '```json', json.dumps(item['data'], ensure_ascii=False, indent=2), '```', '']
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session', default='session.json')
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init')
    init.add_argument('--description', required=True)
    stage = commands.add_parser('submit')
    stage.add_argument('--input', required=True)
    stage.add_argument('--reviewer', required=True)
    commands.add_parser('status')
    export = commands.add_parser('export')
    export.add_argument('--output', default='report.md')
    args = parser.parse_args()
    file = Path(args.session)
    if args.command == 'init':
        if file.exists():
            raise SystemExit('Session already exists; choose a new --session path')
        session = create_session(args.description)
    else:
        session = json.loads(file.read_text(encoding='utf-8'))
        if args.command == 'status':
            next_index = len(session['stages'])
            print(json.dumps({'status': session['status'], 'next_stage': STAGES[next_index][0]
                              if next_index < len(STAGES) else None}, indent=2))
            return
        if args.command == 'export':
            Path(args.output).write_text(export_markdown(session), encoding='utf-8')
            return
        session = submit(session, json.loads(Path(args.input).read_text(encoding='utf-8')), args.reviewer)
    file.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
