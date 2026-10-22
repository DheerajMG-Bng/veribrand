"""Usage: python -m backend.scripts.smoke_test BASE_URL [--ai]. Creates disposable smoke drafts."""
import argparse
import sys
import httpx

def run(base_url, ai=False):
    with httpx.Client(base_url=base_url.rstrip('/'),timeout=120,follow_redirects=True) as client:
        def request(method,path,body=None,role='creator',expected=200):
            response=client.request(method,path,json=body,headers={'X-Role':role})
            if response.status_code!=expected:
                raise AssertionError(f'{method} {path}: expected {expected}, got {response.status_code}: {response.text[:200]}')
            return response.json()
        assert request('GET','/api/health')['status']=='ok'
        print('PASS health')
        assert len(request('GET','/api/knowledge'))==19
        assert len(request('GET','/api/samples'))==11
        for path in ['/','/contents/1','/knowledge']:
            response=client.get(path)
            assert response.status_code==200 and '<div id="root">' in response.text,f'UI missing: {path}'
        print('PASS knowledge, samples, frontend and SPA deep links')
        draft=request('POST','/api/contents',dict(title='Smoke test · terminology and risk',channel='social',text='AcmeHydrate is guaranteed to cure fatigue.'))
        cid=draft['id']
        def post(action,body=None,role='creator'):
            return request('POST',f'/api/contents/{cid}/{action}',body or {},role)
        review=post('review',{'use_ai':False})
        for f in review['content']['findings']:
            decision={'decision':'accepted'} if f['replacement'] is not None else {'decision':'rejected','reason':'Smoke test: verify explicit human override and Reviewer routing.'}
            request('POST',f"/api/findings/{f['id']}/decision",decision)
        applied=post('apply')
        assert applied['versions'][0]['version_no']==2
        assert applied['versions'][0]['text'].startswith('Acme Hydrate')
        review=post('review',{'use_ai':False})
        for f in review['content']['findings']:
            request('POST',f"/api/findings/{f['id']}/decision",{'decision':'rejected','reason':'Smoke test: retain claim only to exercise Reviewer sign-off.'})
        assert post('submit')['status']=='in_review'
        request('POST',f'/api/contents/{cid}/approve',{},expected=403)
        assert post('approve',role='manager')['status']=='pending_reviewer'
        assert post('reviewer-signoff',{'reason':'Automated smoke test on fictional data; not a publication approval.'},'reviewer')['status']=='approved'
        print('PASS create -> review -> decide -> apply -> re-review -> submit -> Manager -> Reviewer -> approved')
        assert post('return',{'comment':'Smoke test: exercise the return workflow.'},'manager')['status']=='changes_requested'
        post('versions',{'text':'Acme Hydrate is available in 500 ml, 1 L and 5 L packs.'})
        clean=post('review',{'use_ai':False})
        assert clean['findings']==[]
        post('submit')
        assert post('approve',role='manager')['status']=='approved'
        post('comments',{'text':'Smoke test completed.'})
        audit=request('GET',f'/api/contents/{cid}/audit')
        assert {'returned','reviewer_signed_off','decisions_applied','comment_added'}<={r['action'] for r in audit}
        diff=request('GET',f'/api/contents/{cid}/diff?from=1&to=3')
        assert diff['before']!=diff['after']
        print('PASS return -> new version -> review -> resubmit -> approve; comments, audit, and diff')
        if ai:
            sample=request('GET','/api/samples')[10]
            item=request('POST','/api/contents',dict(title='Smoke test · optional AI',channel=sample['channel'],text=sample['text']))
            result=request('POST',f"/api/contents/{item['id']}/review",{'use_ai':True})
            print(f"AI review: status={result['ai_status']}, model={result['model_used']}, cached={result['cached']}")
            assert result['ai_status']=='ok','AI unavailable; rule workflow still passed.'
        print(f'PASS all smoke checks at {base_url}; created content #{cid}')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('base_url')
    parser.add_argument('--ai',action='store_true')
    args=parser.parse_args()
    try:
        run(args.base_url,args.ai)
    except (AssertionError,httpx.HTTPError) as error:
        print(f'FAIL: {error}')
        sys.exit(1)
