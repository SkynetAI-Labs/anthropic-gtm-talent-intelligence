import sys
import os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import streamlit as st
from app.talent_mapping import load_candidates,load_config,load_vacancies,search_candidates,ROOT
from app.matching_engine import assess
from app.storage import connect,seed,applications,events,update,STAGES,TERMINAL,REVIEWS
from app.analytics import metrics

st.set_page_config(page_title='GTM Talent Intelligence | SkynetAI-Labs',page_icon='◈',layout='wide')
st.markdown('''<style>
.block-container{padding-top:4.5rem;max-width:1450px}h1{letter-spacing:-1.5px}div[data-testid="stMetric"]{background:#152238;border:1px solid #29415b;padding:18px;border-radius:12px} .eyebrow{color:#58d4ba;font-size:12px;letter-spacing:3px;font-weight:700} .subtitle{color:#a9b9cd;font-size:17px}section[data-testid="stSidebar"]{border-right:1px solid #29415b} [data-testid="stAppDeployButton"],[data-testid="stMainMenu"],#MainMenu{display:none!important} footer{display:none!important}
</style>''',unsafe_allow_html=True)
candidates=load_candidates();config=load_config();vacancies=load_vacancies()
public_demo=os.environ.get('GTM_PUBLIC_DEMO')=='1'
if public_demo:
    if 'demo_connection' not in st.session_state:
        st.session_state.demo_connection=connect(':memory:')
    conn=st.session_state.demo_connection
else:
    conn=connect()
seed(conn,candidates)
apps=applications(conn);history=events(conn);report=metrics(apps,history,vacancies,talent_pool=candidates)
with st.sidebar:
    st.markdown('### ◈ SKYNETAI-LABS')
    st.caption('RECRUITMENT INTELLIGENCE')
    st.link_button('Adam Baig · LinkedIn','https://www.linkedin.com/in/adambaiguk')
    page=st.radio('Workspace',['Start here','Part 1 · GTM strategy','Part 2 · Talent mapping','Part 3 · Candidate matching','Part 4 · Pipeline & analytics','Part 5 · Executive case study'])
    st.divider()
    st.caption('Independent recruitment case study')
    st.caption(f"{report['active_vacancies']} open of {len(vacancies)} hypothetical vacancies · {len(candidates)} mapped profiles")
    st.caption('Five parts · One recruitment workflow')
st.markdown('<div class="eyebrow">GTM TALENT INTELLIGENCE / EMEA</div>',unsafe_allow_html=True)
st.title(page)
st.markdown('<p class="subtitle">Commercial hiring insight, grounded in recruitment judgment.</p>',unsafe_allow_html=True)


if page=='Start here':
    st.caption('Independent, AI-assisted portfolio demonstration using fictional candidates and simulated results.')
    st.subheader('Recruit commercial talent with evidence and judgment')
    st.write('**By Adam Baig** · 20+ years in recruitment, applied to an EMEA commercial hiring challenge.')
    left,right=st.columns(2)
    with left:
        st.markdown('### The problem')
        st.write('Enterprise AI hiring needs commercially credible people who can navigate complex customers, explain value and work with technical teams. Job titles alone do not establish those capabilities.')
    with right:
        st.markdown('### My approach')
        st.write('Calibrate the role, map direct and adjacent talent, investigate evidence gaps and keep hiring managers informed through a clear pipeline. Use tools to support recruiter judgment at each step.')
    st.markdown('### The first 90 days · proposed priorities')
    cols=st.columns(3)
    for col,title,body in zip(cols,['Days 1–30 · Calibrate','Days 31–60 · Build','Days 61–90 · Refine'],[
        'Learn the business, agree role priorities and evidence standards, and establish a pipeline baseline.',
        'Validate market maps, test outreach and run structured screens with regular hiring-manager reviews.',
        'Refine sourcing allocation, support closing and agree next-quarter priorities using evidence and candidate feedback.']):
        with col:
            st.markdown('**'+title+'**');st.write(body)

    st.markdown('### Explore the case study')
    st.write('**Part 1** explains the market strategy. **Part 2** maps talent. **Part 3** makes candidate evidence and gaps visible. **Part 4** tracks the pipeline. **Part 5** brings the business case together.')
    st.write('The simulation follows 50 mapped prospects, 30 applications and five single-seat searches. Six offers lead to four accepted offers, one declined offer and one pending decision. ')

elif page=='Part 4 · Pipeline & analytics':
    overview_tab,pipeline_tab=st.tabs(['Executive overview','Recruitment pipeline'])
    with overview_tab:
        cols=st.columns(4)
        for col,(label,value) in zip(cols,[('Open vacancies',f"{report['active_vacancies']} of {len(vacancies)}"),('People sourced',report['candidates']),('Applications',report['applications']),('Accepted offers',report['hire_n'])]):col.metric(label,value)
        st.caption(f"{len(candidates)} mapped prospects → {report['applications']} applications. Prospects enter the process only after engagement and agreement. Hired means accepted offer; each vacancy has one seat.")
        cols=st.columns(4)
        for col,stage in zip(cols,STAGES[1:5]):col.metric(stage+' · ever reached',next(r['Applications ever reached'] for r in report['funnel'] if r['Stage']==stage))
        left,right=st.columns([1.4,1])
        with left:
            st.subheader('Application progression')
            frame=pd.DataFrame(report['funnel'])
            st.bar_chart(frame.set_index('Stage')['Applications ever reached'],color='#58d4ba',sort=False)
        with right:
            st.subheader('Speed & interpretation')
            st.metric('Median time-to-hire',f"{report['median_time_to_hire']} days" if report['hire_n'] else 'No completed hires')
            st.caption(f"Application entry → accepted offer. Completed sample: {report['hire_n']} applications.")
            st.metric('Median time-to-fill',f"{report['median_time_to_fill']} days" if report['fill_n'] else 'No filled vacancies')
            st.caption(f"Vacancy opening → first accepted offer. Completed sample: {report['fill_n']} vacancies.")
            offers=next(x['Applications ever reached'] for x in report['funnel'] if x['Stage']=='Offer')
            pending=sum(a['stage']=='Offer' for a in apps)
            declined=sum(any(e['application_id']==a['id'] and e['stage']=='Offer' for e in history) and a['stage']=='Withdrawn' for a in apps)
            st.write(f"**Offer outcomes:** {report['hire_n']} accepted · {declined} declined · {pending} pending, from {offers} offers extended.")
        st.subheader('Vacancy-level activity')
        st.dataframe(pd.DataFrame(report['vacancies']),hide_index=True,width='stretch')
        with st.expander('Funnel definitions and conversion denominators'):
            st.dataframe(frame,hide_index=True)
            st.write('Cohort: 30 seeded applications plus local stage updates; the 50-person mapped prospect pool is tracked separately. Counts represent applications ever reaching each stage, including later withdrawals/rejections. Sequential stages prevent skipped-stage distortion. This is not a period-based performance comparison.')
        st.subheader('Sourcing-channel performance · simulated')
        st.dataframe(pd.DataFrame(report['sources']),hide_index=True,width='stretch')
        st.caption('Source is attributed at application entry. Small simulated samples do not establish channel effectiveness.')

    with pipeline_tab:
        if public_demo: st.caption('Changes stay in your current demo session.')
        vacancy=st.selectbox('Vacancy',['All']+list(config['roles']),format_func=lambda v:v if v=='All' else config['roles'][v]['title'])
        subset=[a for a in apps if vacancy=='All' or a['vacancy_id']==vacancy]
        st.dataframe(pd.DataFrame(subset).rename(columns={'id':'Application','candidate_id':'Candidate','vacancy_id':'Vacancy','source':'Source','stage':'Current stage','review':'Recruiter review','notes':'Notes'}),hide_index=True,width='stretch')
        aid=st.selectbox('Application to review',[a['id'] for a in subset])
        current=next(a for a in subset if a['id']==aid)
        st.caption(f"{current['candidate_id']} → {config['roles'][current['vacancy_id']]['title']}")
        with st.form('review'):
            review=st.selectbox('Human review status',REVIEWS,index=REVIEWS.index(current['review']))
            allowed=[current['stage']]
            if current['stage'] in STAGES[:-1]:allowed += [STAGES[STAGES.index(current['stage'])+1]]+TERMINAL
            stage=st.selectbox('Pipeline stage',allowed)
            notes=st.text_area('Recruiter notes · fictional information only',value=current['notes'])
            reason=st.text_input('Human-reviewed closure reason (required for rejection or withdrawal)')
            submitted=st.form_submit_button('Save recruiter review')
            if submitted:
                try:
                    update(conn,aid,stage,review,notes,reason);st.success('Review saved to the local demonstration database.');st.rerun()
                except ValueError as exc:st.error(str(exc))
        st.subheader('Application history')
        st.dataframe(pd.DataFrame([e for e in history if e['application_id']==aid]),hide_index=True,width='stretch')
        st.caption('Each change appends an event. Closed applications cannot be reopened in this version. Notes can still be updated.')

elif page=='Part 2 · Talent mapping':
    c1,c2,c3=st.columns([2,1,1])
    query=c1.text_input('Search talent',placeholder='Skill, title, industry or fictional ID')
    role=c2.selectbox('Current role',['All']+sorted({c['current_title'] for c in candidates}))
    minimum=c3.number_input('Minimum years of relevant experience',min_value=0,max_value=40,value=0)
    c1,c2=st.columns(2)
    skills=c1.multiselect('Required evidenced skills',sorted({s for c in candidates for s in c['skills']}))
    markets=c2.multiselect('Market filter',sorted({c['market'] for c in candidates}))
    found=search_candidates(candidates,query,'' if role=='All' else role,skills,minimum,markets)
    st.subheader(f'{len(found)} fictional profiles')
    display=[{'ID':c['candidate_id'],'Current role':c['current_title'],'Industry':c['industry'],'Years':c['years_experience'],'Market':c['market'],'Skills':', '.join(c['skills']),'Availability (weeks)':c['availability_weeks'],'Source':c['source_category']} for c in found]
    st.dataframe(pd.DataFrame(display),hide_index=True,width='stretch')
    st.download_button('Download filtered fictional profiles',pd.DataFrame(display).to_csv(index=False),'fictional-talent-pool.csv','text/csv')
    if found:
        selected=st.selectbox('Inspect profile',[c['candidate_id'] for c in found]);c=next(c for c in found if c['candidate_id']==selected)
        st.write(f"**{c['current_title']}** · {c['industry']} · {c['market']}")
        st.write(c['professional_experience'])
        st.write('Transferable capabilities: '+(', '.join(c['transferable_skills']) or 'Not evidenced'))
        st.write(f"Methodology: {c['methodology']} · Enterprise exposure: {c['enterprise_exposure']}")
        st.dataframe(pd.DataFrame([{'Competency':skill,'Evidence to verify':note} for skill,note in c['evidence'].items()]),hide_index=True,width='stretch')

elif page=='Part 3 · Candidate matching':
    vid=st.selectbox('Hypothetical vacancy',list(config['roles']),format_func=lambda v:config['roles'][v]['title'])
    role=config['roles'][vid]
    assessed=[(c,assess(c,role,config)) for c in candidates]
    ranked=sorted(assessed,key=lambda pair:pair[1]['score'],reverse=True)
    st.dataframe(pd.DataFrame([{'Candidate':c['candidate_id'],'Current role':c['current_title'],'Evidence score':a['score'],'Match category':a['category'],'Mandatory gaps':', '.join(a['mandatory_gaps']),'Evidence coverage %':a['coverage']} for c,a in ranked]),hide_index=True,width='stretch')
    options=[c['candidate_id'] for c,a in ranked]
    default=next((c['candidate_id'] for c,a in ranked if c['current_title']==role['title'] and a['unknown'] and a['category']=='Closest Match'),
                 next((c['candidate_id'] for c,a in ranked if c['current_title']==role['title'] and a['unknown']),options[0]))
    cid=st.selectbox('Review candidate',options,index=options.index(default),key='candidate_'+vid,format_func=lambda cid: next(f"{c['candidate_id']} · {c['current_title']} · {c['years_experience']} years · {c['industry']}" for c,a in ranked if c['candidate_id']==cid))

    c,a=next(pair for pair in ranked if pair[0]['candidate_id']==cid)
    st.write(f"**Reviewing {c['candidate_id']}** — {c['current_title']}, {c['years_experience']} relevant years in {c['industry']}.")
    st.caption('Job title describes the current role. The assessment reflects the specific evidence available below; unverified competencies are screening topics.')
    left,right=st.columns([1,2])
    with left:
        st.metric('Evidence score / 100',a['score']);st.write('**'+a['category']+'**')
        st.write('**Score components**');st.dataframe(pd.DataFrame([{'Component':k,'Points':v} for k,v in a['components'].items()]),hide_index=True,width='stretch')
        reviews=[x for x in apps if x['candidate_id']==cid and x['vacancy_id']==vid]
        st.write('Recruiter status: '+(reviews[0]['review'] if reviews else 'No application in this vacancy'))
    with right:
        st.subheader('Evidence supporting assessment')
        for skill,note in a['evidence'].items():st.write(f'**{skill}** — {note}')
        st.write('**Missing or unverified competencies:** '+(', '.join(a['unknown']) or 'None in this illustrative profile'))
        st.write('**Mandatory evidence gaps:** '+(', '.join(a['mandatory_gaps']) or 'None'))
        st.subheader('Suggested screening questions')
        for q in a['questions']:st.write('• '+q)
        if not a['questions']:st.write('Validate the examples, scope and outcomes in a structured human interview.')
    with st.expander('Scoring rules and limitations'):
        st.dataframe(pd.DataFrame([{'Competency':k,'Weight within competencies (%)':v,'Required evidence':'Mandatory' if k in role['mandatory'] else 'Additional'} for k,v in role['weights'].items()]),hide_index=True,width='stretch')
        st.caption(f"Illustrative experience benchmark: {role['min_years']} relevant years; consider equivalent evidence. Rules version {config['version']}.")
        st.write('75 points: weighted competency evidence. 15: relevant experience against the illustrative benchmark, capped at full credit. 10: direct industry context. Exact ≥85 plus all mandatory evidence, experience benchmark and direct context; Closest ≥65; Transferable ≥45; otherwise insufficient evidence. No evidenced competencies always means insufficient evidence. Missing evidence earns no points but is not a confirmed lack of ability. Categories are rule labels, not validated predictions. Broad industry and years benchmarks require calibration and may disadvantage adjacent talent; inspect the evidence and never use scores for automatic rejection.')


else:
    number='01' if page=='Part 1 · GTM strategy' else '05'
    file=next((ROOT/'docs').glob(f'lab-{number}*/README.md'))
    body=file.read_text(encoding='utf-8-sig').split('\n',1)[1].lstrip()
    if number=='01':
        roles,rest=body.split('### EMEA market focus',1)
        markets,approach=rest.split('### My seven-step operating approach',1)
        role_col,market_col=st.columns([1.1,1])
        with role_col: st.markdown(roles)
        with market_col: st.markdown('### EMEA market focus'+markets)
        st.markdown('### My seven-step operating approach'+approach)
        with st.expander('Research notes'):
            st.markdown((ROOT/'docs/lab-01-gtm-strategy/research-notes.md').read_text(encoding='utf-8-sig'))
    else:
        st.markdown(body)

st.divider()
st.caption('Independent case study · Fictional data and simulated results · Human decisions throughout · No Anthropic affiliation or endorsement')
if not public_demo: conn.close()
