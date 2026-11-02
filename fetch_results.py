#!/usr/bin/env python3
"""Fetch civicAPI server-side so GitHub Pages browsers do not encounter CORS."""
import json, pathlib, urllib.request, datetime, concurrent.futures, time
ROOT=pathlib.Path(__file__).resolve().parent
IDS={'STexas': '87438', 'SMichigan': '87214', 'SAlaska': '86916', 'SIowa': '87151', 'SMaine': '87188', 'SOhiospecial': '87527', 'SNewHampshire': '87283', 'SKansas': '87162', 'SNorthCarolina': '87346', 'GWisconsin': '87491', 'GGeorgia': '87088', 'GNevada': '87260', 'GOhio': '87365', 'GAlaska': '148898', 'GKansas': '87163', 'HAZ06': '86922', 'HCA22': '86971', 'HCO08': '87017', 'HIA01': '87147', 'HNJ07': '87296', 'HNY17': '87319', 'HPA07': '87382', 'HPA08': '87383', 'HVA02': '87462', 'HWI03': '87485'
'HWI03': '87485', 'MQuestion3': '179840'}
}
now=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
try: old=json.loads((ROOT/'results.json').read_text())
except (OSError,ValueError): old={}
def get(item):
    name,rid=item
    url='https://civicapi.org/api/v2/race/'+rid
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'DDD-Election-Dashboard/1.0','Accept':'application/json'})
        with urllib.request.urlopen(req,timeout=22) as response: data=json.load(response)
        if not isinstance(data,dict) or not isinstance(data.get('candidates'),list): raise ValueError('Unexpected API response')
        # Do not publish enormous county map data. Keep the race-level candidates only.
        return name,{'race_id':rid,'fetched_at':now(),'data':{'candidates':data['candidates'],'test_data':data.get('test_data',False),'election_name':data.get('election_name'),'last_updated':data.get('last_updated')}}
    except Exception as exc:
        previous=old.get('races',{}).get(name)
        if previous and previous.get('race_id')==rid and previous.get('data'):
            previous['error']='Latest update failed; showing last successful snapshot'
            return name,previous
        return name,{'race_id':rid,'error':str(exc)[:180]}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    races=dict(pool.map(get,IDS.items()))
(ROOT/'results.json').write_text(json.dumps({'updated_at':now(),'races':races},ensure_ascii=False,separators=(',',':'))+'\n')
print('Loaded',sum(bool(v.get('data')) for v in races.values()),'of',len(races),'races')
