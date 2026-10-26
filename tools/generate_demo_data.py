from pathlib import Path
import csv,json,random
root=Path(__file__).resolve().parents[1]
roles=[
('V01','Enterprise Account Executive',8,{'enterprise sales':25,'discovery':15,'negotiation':15,'stakeholder management':15,'pipeline management':10,'AI literacy':10,'MEDDPICC':10},['enterprise sales','negotiation']),
('V02','Business Development Representative',1,{'prospecting':30,'qualification':25,'communication':20,'CRM':15,'AI literacy':10},['prospecting','communication']),
('V03','Sales Engineer',4,{'technical discovery':25,'API integration':25,'solution design':20,'communication':15,'AI literacy':15},['technical discovery','solution design']),
('V04','Account Manager',4,{'account planning':25,'customer adoption':25,'negotiation':20,'stakeholder management':20,'AI literacy':10},['account planning','stakeholder management']),
('V05','Sales Leadership',10,{'sales leadership':25,'coaching':20,'forecasting':20,'enterprise sales':15,'stakeholder management':10,'AI literacy':10},['sales leadership','coaching'])]
config={'version':'1.0','thresholds':{'exact':85,'closest':65,'transferable':45},'experience_weight':15,'competency_weight':75,'industry_weight':10,'direct_industries':['AI and machine learning','Enterprise SaaS','Cloud technology','Enterprise software'],'roles':{}}
for rid,title,years,weights,mandatory in roles:
 config['roles'][rid]={'title':title,'min_years':years,'weights':weights,'mandatory':mandatory}
(root/'config/scoring.json').write_text(json.dumps(config,indent=2))
industries=['Enterprise SaaS','AI and machine learning','Cloud technology','Cybersecurity','Enterprise software','Technical consulting','Industrial technology']
markets=['London','Dublin','Paris','Berlin','Amsterdam','Dubai','Johannesburg']
sources=['Referral','Public job board','Industry event','Talent community','Direct sourcing']
rng=random.Random(42); rows=[]
for i in range(50):
 rid,title,minimum,weights,mandatory=roles[i%5]; variant=i//5
 skills=list(weights)
 if variant%4==1: skills=skills[1:]
 if variant%4==2: skills=skills[:3]
 if variant%4==3: skills=skills[:1]+['communication','stakeholder management','discovery']
 skills=list(dict.fromkeys(skills)); unknown=['AI literacy'] if i%6==0 else []
 skills=[s for s in skills if s not in unknown]
 evidence={s:f'Fictional interview note: described a practical example of {s} in a simulated commercial assignment.' for s in skills}
 years=max(0,minimum+variant%5-2)
 rows.append({'candidate_id':f'FIC-{i+1:03}','current_title':title,'industry':industries[(i+variant)%7],'years_experience':years,'market':markets[(i*3+variant)%7],'skills':'|'.join(skills),'unknown_skills':'|'.join(unknown),'evidence':json.dumps(evidence),'methodology':['MEDDPICC','SPIN','Challenger','Not evidenced'][i%4],'enterprise_exposure':['Yes','No','Unknown'][i%3],'transferable_skills':'|'.join(s for s in skills if s in ['communication','stakeholder management','negotiation','discovery','coaching']),'availability_weeks':str(i%9),'source_category':sources[i%5],'fictional':'True'})
with (root/'data/fictional_candidates.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (root/'data/sample_vacancies.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['vacancy_id','title','opened','market','fictional']);w.writeheader();w.writerows({'vacancy_id':r[0],'title':r[1],'opened':'2026-09-01','market':'EMEA','fictional':'True'} for r in roles)
(root/'app/__init__.py').write_text('')
(root/'.streamlit/config.toml').write_text('[theme]\nbase="dark"\nprimaryColor="#58d4ba"\nbackgroundColor="#0c1422"\nsecondaryBackgroundColor="#152238"\ntextColor="#edf3fa"\n[server]\nheadless=true\n[browser]\ngatherUsageStats=false\n')
(root/'.gitignore').write_text('.venv/\n__pycache__/\n.pytest_cache/\n*.sqlite3\n*.sqlite3-*\n.env\n.streamlit/secrets.toml\n')

from pathlib import Path
import csv,json
r=Path(__file__).resolve().parents[1];p=r/'data/fictional_candidates.csv'
with p.open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
cfg=json.loads((r/'config/scoring.json').read_text())
examples={'enterprise sales':'Managed a fictional six-stakeholder enterprise evaluation through procurement and an accepted commercial proposal.','discovery':'Mapped the fictional customer workflow, business problem and success criteria before presenting a solution.','negotiation':'Balanced contract scope, procurement concerns and implementation timing in a simulated negotiation.','stakeholder management':'Built a fictional stakeholder map spanning an executive sponsor, IT reviewers and business users.','pipeline management':'Reviewed a simulated opportunity pipeline weekly and removed deals without a credible next step.','AI literacy':'Explained model limitations, evaluation requirements and human oversight for a fictional AI use case.','MEDDPICC':'Documented a fictional opportunity with metrics, decision criteria, buying process and an internal champion.','prospecting':'Prioritised 30 fictional target accounts using an explicit industry-use-case hypothesis.','qualification':'Qualified a simulated inbound enquiry against need, decision process and agreed next action.','communication':'Presented a concise fictional customer briefing and adapted the explanation for technical and commercial audiences.','CRM':'Maintained simulated contact history, next actions and stage hygiene in a fictional CRM exercise.','technical discovery':'Translated a fictional customer requirement into integration constraints and measurable evaluation criteria.','API integration':'Outlined authentication, request handling, error recovery and evaluation for a fictional API integration.','solution design':'Designed a fictional retrieval-assisted workflow and explained reliability and data-handling trade-offs.','account planning':'Created a fictional account plan linking stakeholder objectives to adoption and renewal milestones.','customer adoption':'Investigated low usage in a fictional account and proposed onboarding plus value-measurement actions.','sales leadership':'Set role expectations and reviewed a fictional team operating plan against commercial priorities.','coaching':'Used a simulated call review to identify a discovery gap and agree a specific coaching action.','forecasting':'Challenged a fictional forecast using deal evidence, dates and explicit assumptions.'}
for i,c in enumerate(rows):
 role=cfg['roles'][f'V{i%5+1:02}']
 if i<5:
  c['skills']='|'.join(role['weights']);c['unknown_skills']='';c['years_experience']=str(role['min_years']+2);c['industry']='Enterprise SaaS'
 skills=c['skills'].split('|')
 c['evidence']=json.dumps({s:f"Fictional scenario {i+1:02}: {examples[s]}" for s in skills})
 c['enterprise_exposure']='Yes' if 'enterprise sales' in skills else 'Unknown'
 c['methodology']='MEDDPICC' if 'MEDDPICC' in skills else 'Not evidenced'
 c['professional_experience']=f"Fictional profile with {c['years_experience']} relevant years in {c['industry']}; current remit: {c['current_title']}. All claims are synthetic and unverified."
with p.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)

# Role-specific interview prompts and reviewed rule version.
reviewed_prompts = {'V01': ['Walk me through an enterprise deal you personally closed: who controlled budget, which decision criteria mattered and what almost stopped the deal?', 'How would you qualify an AI use case before involving technical colleagues, and when would you advise a customer not to proceed?', 'Describe a procurement or commercial negotiation where you protected value while giving the customer a credible route to agreement.'], 'V02': ['Choose a fictional target account: which buying signals and business problem would justify your outreach?', 'How would you distinguish curiosity about AI from a qualified opportunity worth an account executive’s time?', 'Tell me how you changed an outreach sequence after low response rates, and which measures showed the change helped.'], 'V03': ['A customer wants to connect an LLM to internal knowledge: what would you clarify about data access, evaluation and failure modes before proposing a design?', 'Describe a proof of concept you supported: what success criteria did you agree, and how did you handle results that missed them?', 'Explain an API integration trade-off to a commercial sponsor without overstating reliability or promising capabilities you have not tested.'], 'V04': ['Describe an account where usage was healthy but business value was unclear: how did you uncover the gap?', 'How would you build an adoption plan across an executive sponsor, IT stakeholders and end users with competing priorities?', 'Tell me about a renewal or expansion at risk: what evidence changed your plan and what did you personally do?'], 'V05': ['Walk me through a forecast you challenged: what deal evidence changed your view and how did you communicate the risk?', 'Describe how you coached a strong seller whose discovery or qualification was weak; what changed in their behaviour?', 'With limited hiring capacity, how would you choose between adding prospecting, account executive and technical pre-sales capacity?']}
cfg=json.loads((r/'config/scoring.json').read_text())
for k,qs in reviewed_prompts.items(): cfg['roles'][k]['screening_questions']=qs
cfg['version']='1.1'
(r/'config/scoring.json').write_text(json.dumps(cfg,indent=2),encoding='utf-8')

import re
# Candidate evidence: retain substance without repeated scenario labels.
p=r/'data/fictional_candidates.csv'
with p.open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
for c in rows:
 evidence=json.loads(c['evidence']);evidence={k:re.sub(r'^Fictional scenario \d+: ','',v) for k,v in evidence.items()}
 if c['candidate_id']=='FIC-026':
  skills=c['skills'].split('|');skills=[x for x in skills if x!='AI literacy'];skills.append('enterprise sales');c['skills']='|'.join(skills);c['unknown_skills']='AI literacy'
  evidence.pop('AI literacy',None);evidence['enterprise sales']='Led a six-stakeholder enterprise evaluation through procurement and an agreed commercial proposal.';c['enterprise_exposure']='Yes'
 c['evidence']=json.dumps(evidence)
 c['professional_experience']=f"{c['years_experience']} relevant years in {c['industry']}; current remit: {c['current_title']}."
with p.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
