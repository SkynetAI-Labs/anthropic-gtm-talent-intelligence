from app.talent_mapping import validate_candidates

def assess(candidate,role,config):
    """Evidence-based demonstration. Geography and personal attributes are not read."""
    validate_candidates([candidate])
    weights=role['weights']
    if sum(weights.values())!=100 or any(w<=0 for w in weights.values()):
        raise ValueError('Role weights must be positive and sum to 100')
    evidence=candidate.get('evidence',{})
    supported={s for s in candidate.get('skills',[]) if str(evidence.get(s,'')).strip()}
    matched=[s for s in weights if s in supported]
    unknown=[s for s in weights if s not in supported]
    mandatory_gaps=[s for s in role['mandatory'] if s not in supported]
    years=candidate.get('years_experience')
    experience=0 if years is None else min(years/role['min_years'],1)
    competency=sum(weights[s] for s in matched)/100
    direct=candidate.get('industry') in config['direct_industries']
    parts={'Competency evidence':round(competency*config['competency_weight'],2),
           'Relevant experience':round(experience*config['experience_weight'],2),
           'Industry context':config['industry_weight'] if direct else 0}
    score=round(sum(parts.values()),1)
    t=config['thresholds']
    if not matched: category='Insufficient evidence'
    elif score>=t['exact'] and not mandatory_gaps and years is not None and years>=role['min_years'] and direct:
        category='Exact Match'
    elif score>=t['closest']: category='Closest Match'
    elif score>=t['transferable']: category='Transferable Skills Match'
    else: category='Insufficient evidence'
    questions=list(role.get('screening_questions',[]))
    gap_prompts={
        'AI literacy':'A customer wants to use AI for an important business workflow. How would you explore value, model limitations and the evidence needed before making a commitment?',
        'enterprise sales':'Walk me through the largest buying group you personally navigated: who decided, what evidence moved the deal forward and what was your contribution?',
        'negotiation':'Describe a commercial concession you challenged or reshaped. What mattered to the customer and what did you protect?',
        'API integration':'How would you investigate an integration that works in a proof of concept but fails under real customer usage?'
    }
    questions += [gap_prompts[s] for s in unknown if s in gap_prompts][:2]
    return {'score':score,'category':category,'components':parts,'matched':matched,'unknown':unknown,
            'mandatory_gaps':mandatory_gaps,'evidence':{s:evidence[s] for s in matched},'questions':questions,
            'coverage':round(len(matched)/len(weights)*100),'rules_version':config['version']}
