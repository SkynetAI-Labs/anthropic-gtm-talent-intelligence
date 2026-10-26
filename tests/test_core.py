import copy
from datetime import date
import pytest
from app.talent_mapping import load_candidates,load_config,load_vacancies,search_candidates,validate_candidates
from app.matching_engine import assess
from app.storage import connect,seed,applications,events,update
from app.analytics import metrics

@pytest.fixture
def c():return load_candidates()[0]
@pytest.fixture
def cfg():return load_config()
@pytest.fixture
def db(tmp_path):
    con=connect(tmp_path/'test.sqlite3');seed(con,load_candidates());yield con;con.close()

def test_seed_consistency():
    rows=load_candidates();assert len(rows)==50;assert len({c['candidate_id'] for c in rows})==50
    assert len(load_vacancies())==5
    assert len({c['industry'] for c in rows})==7

@pytest.mark.parametrize('kind',['duplicate','real','negative','conflict','orphan'])
def test_invalid_records(c,kind):
    rows=[c]
    if kind=='duplicate':rows.append(copy.deepcopy(c))
    if kind=='real':c['fictional']='False'
    if kind=='negative':c['years_experience']=-1
    if kind=='conflict':c['unknown_skills']=c['skills'][:1]
    if kind=='orphan':c['evidence']['invention']='unmatched'
    with pytest.raises(ValueError):validate_candidates(rows)

def test_search_combines_filters():
    rows=load_candidates();found=search_candidates(rows,query='enterprise',role='Enterprise Account Executive',skills=['negotiation'],min_years=8,markets=['London','Paris','Berlin','Dublin','Amsterdam','Dubai','Johannesburg'])
    assert found
    assert all(c['current_title']=='Enterprise Account Executive' and c['years_experience']>=8 and 'negotiation' in c['skills'] for c in found)
    assert not search_candidates(rows,query='no-such-profile')

def full_candidate(c,role):
    c=copy.deepcopy(c);c.update(skills=list(role['weights']),unknown_skills=[],evidence={s:'Specific fictional example' for s in role['weights']},years_experience=role['min_years'],industry='Enterprise SaaS');return c

def test_exact_and_components(c,cfg):
    role=cfg['roles']['V01'];c=full_candidate(c,role);a=assess(c,role,cfg)
    assert a['score']==100 and a['category']=='Exact Match'
    assert sum(a['components'].values())==100

def test_mandatory_unknown_prevents_exact(c,cfg):
    role=cfg['roles']['V01'];c=full_candidate(c,role);c['evidence']['negotiation']=''
    a=assess(c,role,cfg);assert a['category']!='Exact Match';assert 'negotiation' in a['mandatory_gaps'];assert a['questions']

def test_missing_experience_and_all_evidence(c,cfg):
    c.update(years_experience=None,evidence={})
    a=assess(c,cfg['roles']['V01'],cfg);assert a['category']=='Insufficient evidence';assert a['components']['Relevant experience']==0

def test_personal_fields_do_not_affect_score(c,cfg):
    role=cfg['roles']['V01'];a=assess(c,role,cfg);altered=copy.deepcopy(c)
    altered.update(market='Other',name='Other',nationality='Other',age=59,gender='Other')
    assert assess(altered,role,cfg)==a

@pytest.mark.parametrize('score,expected',[(85,'Exact Match'),(84.9,'Closest Match'),(65,'Closest Match'),(64.9,'Transferable Skills Match'),(45,'Transferable Skills Match'),(44.9,'Insufficient evidence')])
def test_category_boundaries(c,cfg,score,expected):
    role={'weights':{'sales':100},'mandatory':['sales'],'min_years':1}
    c=full_candidate(c,role)
    cfg=copy.deepcopy(cfg);cfg.update(competency_weight=score,experience_weight=0,industry_weight=0)
    assert assess(c,role,cfg)['category']==expected

def test_seed_idempotent_and_progression(db):
    assert len(applications(db))==30;seed(db,load_candidates());assert len(applications(db))==30
    a=next(a for a in applications(db) if a['stage']=='Applied')
    with pytest.raises(ValueError):update(db,a['id'],'Shortlisted','Reviewed','')
    with pytest.raises(ValueError):update(db,a['id'],'Screened','Not reviewed','')
    n=len(events(db));update(db,a['id'],'Screened','Reviewed','Fictional note')
    assert len(events(db))==n+1
    assert next(x for x in applications(db) if x['id']==a['id'])['notes']=='Fictional note'

def test_closure_requires_reason(db):
    a=next(a for a in applications(db) if a['stage']=='Applied')
    with pytest.raises(ValueError):update(db,a['id'],'Rejected','Reviewed','')
    update(db,a['id'],'Rejected','Reviewed','','Fictional review reason')
    with pytest.raises(ValueError):update(db,a['id'],'Screened','Reviewed','')

def test_dates_cannot_go_back(db):
    a=next(a for a in applications(db) if a['stage']=='Applied')
    with pytest.raises(ValueError):update(db,a['id'],'Screened','Reviewed','',occurred='2025-01-01T00:00:00')

def test_known_analytics_fixture():
    apps=[{'id':'A','candidate_id':'C','vacancy_id':'V','source':'Referral'},{'id':'B','candidate_id':'C','vacancy_id':'V2','source':'Referral'}]
    ev=[{'application_id':'A','stage':'Applied','occurred':'2026-01-02T00:00:00'},{'application_id':'B','stage':'Applied','occurred':'2026-01-02T00:00:00'}]
    ev += [{'application_id':'A','stage':s,'occurred':d+'T00:00:00'} for s,d in [('Screened','2026-01-03'),('Shortlisted','2026-01-04'),('Interview','2026-01-05'),('Offer','2026-01-09'),('Hired','2026-01-12')]]
    vacancies=[{'vacancy_id':'V','title':'One','opened':'2026-01-01'},{'vacancy_id':'V2','title':'Two','opened':'2026-01-01'}]
    m=metrics(apps,ev,vacancies,date(2026,1,20))
    assert m['candidates']==1 and m['applications']==2 and m['active_vacancies']==1
    assert m['median_time_to_hire']==10 and m['median_time_to_fill']==11
    assert m['funnel'][1]['Conversion %']==50 and m['sources'][0]['Hire conversion %']==50
    assert m['vacancies'][1]['Open age days']==19

def test_empty_metrics():
    m=metrics([],[],[]);assert m['median_time_to_hire'] is None and m['median_time_to_fill'] is None

def test_streamlit_pages():
    from streamlit.testing.v1 import AppTest
    at=AppTest.from_file(__import__('pathlib').Path(__file__).resolve().parents[1]/'app/dashboard.py',default_timeout=60).run()
    assert not at.exception
    for page in ['Part 1 · GTM strategy','Part 2 · Talent mapping','Part 3 · Candidate matching','Part 4 · Pipeline & analytics','Part 4 · Pipeline & analytics','Part 5 · Executive case study']:
        at.sidebar.radio[0].set_value(page).run();assert not at.exception
    at.sidebar.radio[0].set_value('Part 2 · Talent mapping').run()
    at.text_input[0].set_value('no-such-profile').run();assert not at.exception
    assert any('0 fictional profiles' in s.value for s in at.subheader)



def test_all_match_categories_represented(cfg):
    categories={assess(c,r,cfg)['category'] for c in load_candidates() for r in cfg['roles'].values()}
    assert {'Exact Match','Closest Match','Transferable Skills Match','Insufficient evidence'}<=categories

def test_seed_has_open_and_filled_searches(db):
    m=metrics(applications(db),events(db),load_vacancies())
    assert m['active_vacancies']==1 and m['hire_n']==4


def test_streamlit_filter_and_review(tmp_path,monkeypatch):
    from streamlit.testing.v1 import AppTest
    import app.storage as storage
    real_connect=storage.connect
    monkeypatch.setattr(storage,'connect',lambda:real_connect(tmp_path/'ui.sqlite3'))
    path=__import__('pathlib').Path(__file__).resolve().parents[1]/'app/dashboard.py'
    at=AppTest.from_file(path,default_timeout=60).run()
    at.sidebar.radio[0].set_value('Part 2 · Talent mapping').run()
    at.text_input[0].set_value('FIC-001').run()
    assert any('1 fictional profiles'==s.value for s in at.subheader)
    at.sidebar.radio[0].set_value('Part 4 · Pipeline & analytics').run()
    # A025 is an open application at entry in the revised seed.
    at.selectbox[1].set_value('A025').run()
    at.selectbox[2].set_value('Reviewed')
    at.selectbox[3].set_value('Screened')
    at.text_area[0].set_value('Fictional UI verification note')
    at.button[0].click().run()
    assert not at.exception
    con=real_connect(tmp_path/'ui.sqlite3')
    row=con.execute("SELECT * FROM applications WHERE id='A025'").fetchone()
    assert row['stage']=='Screened' and row['review']=='Reviewed' and row['notes']=='Fictional UI verification note'
    con.close()


def test_recruitment_cohort_and_offer_outcomes(db):
    rows=applications(db);hist=events(db)
    m=metrics(rows,hist,load_vacancies(),talent_pool=load_candidates())
    assert m['candidates']==50 and m['applications']==30
    assert [r['Applications ever reached'] for r in m['funnel']]==[30,24,16,10,6,4]
    assert sum(a['stage']=='Offer' for a in rows)==1
    assert sum(a['stage']=='Withdrawn' for a in rows)==1
    assert len({a['vacancy_id'] for a in rows if a['stage']=='Hired'})==4
    assert m['median_time_to_hire']==24


def test_role_specific_questions_for_complete_profiles(c,cfg):
    for role in cfg['roles'].values():
        questions=assess(full_candidate(c,role),role,cfg)['questions']
        assert len(questions)>=3 and questions[:3]==role['screening_questions']
    assert len({q for r in cfg['roles'].values() for q in r['screening_questions']})==15


def test_prevent_offering_against_filled_single_seat(db):
    a=next(a for a in applications(db) if a['stage']=='Interview' and a['vacancy_id']=='V02')
    with pytest.raises(ValueError,match='already filled'):
        update(db,a['id'],'Offer','Reviewed','')


def test_opening_and_gap_example():
    from streamlit.testing.v1 import AppTest
    at=AppTest.from_file(__import__('pathlib').Path(__file__).resolve().parents[1]/'app/dashboard.py',default_timeout=60).run()
    assert at.title[0].value=='Start here'
    at.sidebar.radio[0].set_value('Part 3 · Candidate matching').run()
    assert not at.exception
    assert float(at.metric[0].value)<100
    assert len(at.json)==0
    at.sidebar.radio[0].set_value('Part 2 · Talent mapping').run()
    assert len(at.json)==0


def test_selected_example_has_coherent_gap(cfg):
    candidate=next(c for c in load_candidates() if c['candidate_id']=='FIC-026')
    result=assess(candidate,cfg['roles']['V01'],cfg)
    assert 'enterprise sales' in result['matched']
    assert result['unknown']==['AI literacy']
    assert result['category']=='Closest Match'
    assert all('Fictional scenario' not in evidence for evidence in result['evidence'].values())
    assert not any('illustrative 8-year benchmark' in q or 'Please give a specific example demonstrating' in q for q in result['questions'])


def test_concise_strategy_and_single_part_four():
    from streamlit.testing.v1 import AppTest
    path=__import__('pathlib').Path(__file__).resolve().parents[1]/'app/dashboard.py'
    at=AppTest.from_file(path,default_timeout=60).run()
    assert len([p for p in at.sidebar.radio[0].options if p.startswith('Part 4')])==1
    at.sidebar.radio[0].set_value('Part 1 · GTM strategy').run()
    assert not at.exception
    assert any(x.label=='Research notes' for x in at.expander)
    at.sidebar.radio[0].set_value('Part 4 · Pipeline & analytics').run()
    assert [x.label for x in at.tabs]==['Executive overview','Recruitment pipeline']
    at.sidebar.radio[0].set_value('Part 5 · Executive case study').run()
    displayed=' '.join(x.value for x in at.markdown)
    for phrase in ['independently audited','requires separate approval','Do not delay','Adam reports']:
        assert phrase not in displayed


def test_public_visitors_have_independent_pipelines():
    from streamlit.testing.v1 import AppTest
    path=__import__('pathlib').Path(__file__).resolve().parents[1]/'streamlit_app.py'
    first=AppTest.from_file(path,default_timeout=60).run()
    second=AppTest.from_file(path,default_timeout=60).run()
    assert not first.exception and not second.exception
    one=first.session_state['demo_connection'];two=second.session_state['demo_connection']
    assert one is not two
    update(one,'A025','Screened','Reviewed','Session-specific demonstration note')
    first.run()
    assert not first.exception
    assert one.execute("SELECT stage FROM applications WHERE id='A025'").fetchone()[0]=='Screened'
    assert two.execute("SELECT stage FROM applications WHERE id='A025'").fetchone()[0]=='Applied'
