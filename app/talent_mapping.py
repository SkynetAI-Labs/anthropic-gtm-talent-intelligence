from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
def load_config():
    return json.loads((ROOT/'config/scoring.json').read_text())
def load_candidates():
    with (ROOT/'data/fictional_candidates.csv').open(encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    for c in rows:
        c['years_experience']=int(c['years_experience'])
        c['availability_weeks']=int(c['availability_weeks'])
        for k in ('skills','unknown_skills','transferable_skills'):
            c[k]=[x for x in c[k].split('|') if x]
        c['evidence']=json.loads(c['evidence'])
    validate_candidates(rows)
    return rows
def load_vacancies():
    with (ROOT/'data/sample_vacancies.csv').open(encoding='utf-8') as f:
        return list(csv.DictReader(f))
def validate_candidates(rows):
    ids=set()
    for c in rows:
        if not c['candidate_id'].startswith('FIC-') or c['candidate_id'] in ids:
            raise ValueError('Candidate identifiers must be unique fictional IDs')
        ids.add(c['candidate_id'])
        if str(c.get('fictional')).lower()!='true': raise ValueError('Only fictional profiles allowed')
        years=c.get('years_experience')
        if years is not None and (not isinstance(years,(int,float)) or isinstance(years,bool) or not 0<=years<=60):
            raise ValueError('Invalid experience')
        if set(c.get('skills',[])) & set(c.get('unknown_skills',[])):
            raise ValueError('A competency cannot be evidenced and unknown')
        if set(c.get('evidence',{}))-set(c.get('skills',[])):
            raise ValueError('Evidence references an undeclared skill')
def search_candidates(rows,query='',role='',skills=(),min_years=0,markets=()):
    q=query.strip().lower()
    return [c for c in rows if
        (not q or q in ' '.join([c['candidate_id'],c['current_title'],c['industry'],*c['skills']]).lower())
        and (not role or c['current_title']==role)
        and set(skills)<=set(c['skills'])
        and (c['years_experience'] or 0)>=min_years
        and (not markets or c['market'] in markets)]
