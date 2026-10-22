import pytest
from fastapi.testclient import TestClient
from backend.app.db import get_db
from backend.app.main import app
from backend.app.routes.api import limits

@pytest.fixture
def client(db):
    app.dependency_overrides[get_db]=lambda:db
    limits.clear()
    client=TestClient(app)
    yield client
    app.dependency_overrides.clear()

def post(client,path,data=None,role='creator',status=200):
    result=client.post('/api'+path,json=data or {},headers={'X-Role':role})
    assert result.status_code==status,result.text
    return result.json()

def draft(client,text='AcmeHydrate is guaranteed to cure fatigue.'):
    return post(client,'/contents',dict(title='Workflow test',channel='social',text=text))['id']

def test_full_risk_workflow(client):
    cid=draft(client)
    review=post(client,f'/contents/{cid}/review',{'use_ai':False})
    for f in review['content']['findings']:
        decision={'decision':'accepted'} if f['replacement'] is not None else {'decision':'rejected','reason':'Request authorised review of original wording.'}
        post(client,f"/findings/{f['id']}/decision",decision)
    applied=post(client,f'/contents/{cid}/apply')
    assert applied['versions'][0]['version_no']==2
    assert applied['versions'][0]['text'].startswith('Acme Hydrate')
    post(client,f'/contents/{cid}/submit',status=409)
    reviewed=post(client,f'/contents/{cid}/review',{'use_ai':False})
    for f in reviewed['content']['findings']:
        post(client,f"/findings/{f['id']}/decision",{'decision':'rejected','reason':'Escalate retained claim to Reviewer.'})
    assert post(client,f'/contents/{cid}/submit')['status']=='in_review'
    post(client,f'/contents/{cid}/approve',role='creator',status=403)
    assert post(client,f'/contents/{cid}/approve',role='manager')['status']=='pending_reviewer'
    assert post(client,f'/contents/{cid}/reviewer-signoff',{'reason':'Demo only; authorised review recorded.'},role='reviewer')['status']=='approved'
    actions={r['action'] for r in client.get(f'/api/contents/{cid}/audit').json()}
    assert {'content_created','review_completed','finding_decided','version_created','decisions_applied','submitted','manager_approved','reviewer_signed_off'}<=actions

def test_return_revision_resubmit(client):
    cid=draft(client,'Acme Hydrate comes in 1 L packs.')
    post(client,f'/contents/{cid}/review',{'use_ai':False})
    post(client,f'/contents/{cid}/submit')
    assert post(client,f'/contents/{cid}/return',{'comment':'Please include all sizes.'},role='manager')['status']=='changes_requested'
    post(client,f'/contents/{cid}/versions',{'text':'Acme Hydrate comes in 500 ml, 1 L and 5 L packs.'})
    post(client,f'/contents/{cid}/review',{'use_ai':False})
    post(client,f'/contents/{cid}/submit')
    assert post(client,f'/contents/{cid}/approve',role='manager')['status']=='approved'
    diff=client.get(f'/api/contents/{cid}/diff?from=1&to=2').json()
    assert diff['before']!=diff['after']

def test_validation_and_permissions(client):
    post(client,'/contents',{'title':'Too long','channel':'social','text':'a'*5001},status=422)
    post(client,'/contents',{'title':'Role test','channel':'social','text':'Hello'},role='manager',status=403)
    cid=draft(client)
    review=post(client,f'/contents/{cid}/review',{'use_ai':False})
    f=next(f for f in review['content']['findings'] if f['replacement'] is None)
    post(client,f"/findings/{f['id']}/decision",{'decision':'accepted'},status=422)
    post(client,f"/findings/{f['id']}/decision",{'decision':'rejected'},status=422)
    post(client,f'/contents/{cid}/submit',status=409)
    for role in ['manager','reviewer','admin']:
        post(client,f'/findings/{f["id"]}/decision',{'decision':'edited','edited_text':'water'},role=role,status=403)

def test_rate_limit(client):
    cid=draft(client,'Hello Acme Hydrate.')
    for _ in range(10):
        post(client,f'/contents/{cid}/review',{'use_ai':False})
    post(client,f'/contents/{cid}/review',{'use_ai':False},status=429)

def test_cannot_submit_unapplied_fixes(client):
    cid=draft(client,'AcmeHydrate')
    review=post(client,f'/contents/{cid}/review',{'use_ai':False})
    f=review['content']['findings'][0]
    post(client,f"/findings/{f['id']}/decision",{'decision':'accepted'})
    post(client,f'/contents/{cid}/submit',status=409)
    post(client,f'/contents/{cid}/review',{'use_ai':False},status=409)

def test_knowledge_mutation(client):
    data=dict(kind='term',code='T-99',title='Test rule',text='No forbiddenword.',meta={'check':'patterns','patterns':['forbiddenword'],'severity':'medium'})
    post(client,'/knowledge',data,status=403)
    item=post(client,'/knowledge',data,role='admin')
    cid=draft(client,'A forbiddenword here.')
    result=post(client,f'/contents/{cid}/review',{'use_ai':False})
    assert result['findings'][0]['source_code']=='T-99'
    assert client.delete(f"/api/knowledge/{item['id']}",headers={'X-Role':'admin'}).status_code==200

def test_stale_finding_and_workflow_guards(client):
    cid=draft(client,'AcmeHydrate')
    r=post(client,f'/contents/{cid}/review',{'use_ai':False})
    fid=r['content']['findings'][0]['id']
    post(client,f'/contents/{cid}/versions',{'text':'Acme Hydrate'})
    post(client,f'/findings/{fid}/decision',{'decision':'accepted'},status=409)
    post(client,f'/contents/{cid}/reviewer-signoff',{'reason':'Wrong stage'},role='reviewer',status=409)
    post(client,f'/contents/{cid}/review',{'use_ai':False})
    post(client,f'/contents/{cid}/submit')
    post(client,f'/contents/{cid}/versions',{'text':'Changed'},status=409)
    post(client,f'/contents/{cid}/review',{'use_ai':False},status=409)
