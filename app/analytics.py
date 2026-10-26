from datetime import datetime,date
from statistics import median
from app.storage import STAGES

def metrics(applications,events,vacancies,as_of=None,talent_pool=None):
    today=as_of or date.today()
    reached={s:{e['application_id'] for e in events if e['stage']==s} for s in STAGES}
    funnel=[]
    for i,s in enumerate(STAGES):
        denom=len(reached[STAGES[i-1]]) if i else len(applications)
        funnel.append({'Stage':s,'Applications ever reached':len(reached[s]),'Previous stage denominator':denom,'Conversion %':round(100*len(reached[s])/denom,1) if denom else None})
    times={};hire_days=[];fill_days=[];vacancy_rows=[]
    for e in events:
        key=(e['application_id'],e['stage']);d=datetime.fromisoformat(e['occurred']).date()
        times[key]=min(times.get(key,d),d)
    hired_by_vacancy={}
    for a in applications:
        end=times.get((a['id'],'Hired'));start=times.get((a['id'],'Applied'))
        if start and end:
            hire_days.append((end-start).days)
            hired_by_vacancy.setdefault(a['vacancy_id'],[]).append(end)
    for v in vacancies:
        opened=date.fromisoformat(v['opened']);ends=hired_by_vacancy.get(v['vacancy_id'],[])
        duration=(min(ends)-opened).days if ends else None
        if duration is not None:fill_days.append(duration)
        vacancy_rows.append({'Vacancy':v['title'],'Status':'Filled' if ends else 'Open','Days to first accepted offer':duration,'Open age days':None if ends else (today-opened).days,'Applications':sum(a['vacancy_id']==v['vacancy_id'] for a in applications)})
    sources=[]
    for source in sorted({a['source'] for a in applications}):
        ids={a['id'] for a in applications if a['source']==source}
        hires=len(ids&reached['Hired'])
        sources.append({'Source':source,'Applications':len(ids),'Accepted offers':hires,'Hire conversion %':round(hires/len(ids)*100,1)})
    return {'funnel':funnel,'sources':sources,'vacancies':vacancy_rows,'active_vacancies':sum(v['Status']=='Open' for v in vacancy_rows),'candidates':len(talent_pool) if talent_pool is not None else len({a['candidate_id'] for a in applications}),'applications':len(applications),'median_time_to_hire':median(hire_days) if hire_days else None,'hire_n':len(hire_days),'median_time_to_fill':median(fill_days) if fill_days else None,'fill_n':len(fill_days)}
