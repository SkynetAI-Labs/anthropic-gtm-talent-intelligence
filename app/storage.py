import sqlite3
from datetime import datetime,timedelta,date
from app.talent_mapping import ROOT
STAGES=['Applied','Screened','Shortlisted','Interview','Offer','Hired']
TERMINAL=['Withdrawn','Rejected']
REVIEWS=['Not reviewed','Needs clarification','Reviewed']

def connect(path=None):
    conn=sqlite3.connect(path or ROOT/'data/pipeline-v2.sqlite3',check_same_thread=False)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS applications(id TEXT PRIMARY KEY,candidate_id TEXT NOT NULL,vacancy_id TEXT NOT NULL,source TEXT NOT NULL,stage TEXT NOT NULL,review TEXT NOT NULL DEFAULT 'Not reviewed',notes TEXT NOT NULL DEFAULT '',UNIQUE(candidate_id,vacancy_id));
    CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,application_id TEXT NOT NULL REFERENCES applications(id),stage TEXT NOT NULL,occurred TEXT NOT NULL,reason TEXT NOT NULL DEFAULT '');
    ''')
    return conn

def seed(conn,candidates):
    if conn.execute('SELECT COUNT(*) FROM applications').fetchone()[0]: return
    # Fifty mapped prospects; thirty enter an application process.
    # Six offers: four accepted, one declined, one pending on the fifth vacancy.
    for i,c in enumerate(candidates[:30]):
        if i==5: c=candidates[49]  # A second leadership candidate for the fifth search.
        aid=f'A{i+1:03}'
        vid=f'V{i+1:02}' if i<4 else ('V05' if i<6 else f'V{i%5+1:02}')
        last=5 if i<4 else 4 if i<6 else 3 if i<10 else 2 if i<16 else 1 if i<24 else 0
        conn.execute('INSERT INTO applications(id,candidate_id,vacancy_id,source,stage,review) VALUES(?,?,?,?,?,?)',
                     (aid,c['candidate_id'],vid,c['source_category'],STAGES[last],'Reviewed' if last else 'Not reviewed'))
        start=datetime(2026,9,3)+timedelta(days=i%12)
        for j in range(last+1):
            conn.execute('INSERT INTO events(application_id,stage,occurred) VALUES(?,?,?)',
                         (aid,STAGES[j],(start+timedelta(days=[0,3,7,12,20,24][j])).isoformat()))
        if i==4:
            conn.execute("UPDATE applications SET stage='Withdrawn' WHERE id=?",(aid,))
            conn.execute('INSERT INTO events(application_id,stage,occurred,reason) VALUES(?,?,?,?)',
                         (aid,'Withdrawn',(start+timedelta(days=22)).isoformat(),
                          'Simulated offer declined: candidate preferred another opportunity after recruiter discussion.'))
        elif i in (13,19):
            conn.execute("UPDATE applications SET stage='Rejected' WHERE id=?",(aid,))
            conn.execute('INSERT INTO events(application_id,stage,occurred,reason) VALUES(?,?,?,?)',
                         (aid,'Rejected',(start+timedelta(days=[0,3,7,12,20,24][last]+1)).isoformat(),
                          'Simulated recruiter-reviewed closure: role-specific evidence not established after screening.'))
    conn.commit()

def applications(conn):
    return [dict(r) for r in conn.execute('SELECT * FROM applications ORDER BY id')]
def events(conn):
    return [dict(r) for r in conn.execute('SELECT * FROM events ORDER BY occurred,id')]
def update(conn,aid,stage,review,notes,reason='',occurred=None):
    row=conn.execute('SELECT * FROM applications WHERE id=?',(aid,)).fetchone()
    if row is None: raise ValueError('Application not found')
    if review not in REVIEWS: raise ValueError('Invalid review status')
    if stage not in STAGES+TERMINAL: raise ValueError('Invalid stage')
    if stage!=row['stage']:
        if row['stage'] in TERMINAL or row['stage']=='Hired': raise ValueError('Closed applications cannot progress')
        if stage in TERMINAL:
            if review!='Reviewed' or not reason.strip(): raise ValueError('Closure requires human review and a reason')
        elif STAGES.index(stage)!=STAGES.index(row['stage'])+1:
            raise ValueError('Progress one stage at a time')
        if review!='Reviewed': raise ValueError('Progression requires recruiter review')
        if stage in ('Offer','Hired') and conn.execute(
            "SELECT 1 FROM applications WHERE vacancy_id=? AND stage='Hired' AND id<>?",
            (row['vacancy_id'],aid)).fetchone():
            raise ValueError('This single-seat vacancy is already filled; review other applications for closure')
        timestamp=occurred or datetime.now().isoformat(timespec='seconds')
        previous=conn.execute('SELECT MAX(occurred) FROM events WHERE application_id=?',(aid,)).fetchone()[0]
        parsed=datetime.fromisoformat(timestamp)
        if parsed>datetime.now() or (previous and parsed<datetime.fromisoformat(previous)):
            raise ValueError('Stage date must follow the previous event and cannot be in the future')
        conn.execute('INSERT INTO events(application_id,stage,occurred,reason) VALUES(?,?,?,?)',(aid,stage,timestamp,reason.strip()))
    conn.execute('UPDATE applications SET stage=?,review=?,notes=? WHERE id=?',(stage,review,notes.strip(),aid))
    conn.commit()

