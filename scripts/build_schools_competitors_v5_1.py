#!/usr/bin/env python3
import csv, json, math, time, urllib.parse, urllib.request
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'public/data'; DOCS=ROOT/'docs'; LOGS=ROOT/'logs'; PROC=ROOT/'processed_data'
TARGET={'10011','10010','10003','10014','10012','10013'}
TODAY='2026-06-11'

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def writej(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
def fetch(url, data=None):
    req=urllib.request.Request(url, data=data, headers={'User-Agent':'Hermes-HGL-v5.1-schools-competitors/1.0'})
    with urllib.request.urlopen(req,timeout=120) as r: return r.read().decode('utf-8')
def fetch_json(url): return json.loads(fetch(url))
def socrata(domain,res,where=None,limit=50000):
    out=[]; off=0
    while True:
        params={'$limit':str(limit),'$offset':str(off)}
        if where: params['$where']=where
        url=f'https://{domain}/resource/{res}.json?'+urllib.parse.urlencode(params)
        try: rows=fetch_json(url)
        except Exception as e:
            (LOGS/f'v5_1_fetch_error_{res}.log').write_text(str(e),encoding='utf-8'); return out
        out.extend(rows)
        if len(rows)<limit: break
        off+=limit
    return out
def bounds(gj):
    xs=[]; ys=[]
    def walk(c):
        if isinstance(c,list) and len(c)>=2 and isinstance(c[0],(int,float)) and isinstance(c[1],(int,float)):
            xs.append(c[0]); ys.append(c[1])
        elif isinstance(c,list):
            for x in c: walk(x)
    for f in gj['features']: walk(f['geometry']['coordinates'])
    return min(xs)-0.011,min(ys)-0.0073,max(xs)+0.011,max(ys)+0.0073
def fnum(x):
    try: return float(x)
    except Exception: return None
def in_bbox(lon,lat,b): return b[0]<=lon<=b[2] and b[1]<=lat<=b[3]
def zip_guess(lon,lat): return 'buffer/unknown'
def clean(s): return ' '.join(str(s or '').split())
def key(lon,lat,name): return (round(lat,5),round(lon,5),clean(name).lower()[:50])
def overpass(b):
    s,w,n,e=b[1],b[0],b[3],b[2]
    q=f'''[out:json][timeout:60];(
      node["amenity"~"school|kindergarten|childcare"]({s},{w},{n},{e});
      way["amenity"~"school|kindergarten|childcare"]({s},{w},{n},{e});
      relation["amenity"~"school|kindergarten|childcare"]({s},{w},{n},{e});
    );out center tags;'''
    try:
        return json.loads(fetch('https://overpass-api.de/api/interpreter', urllib.parse.urlencode({'data':q}).encode()))
    except Exception as e:
        (LOGS/'v5_1_overpass_error.log').write_text(str(e),encoding='utf-8'); return {'elements':[]}
def add_school(rows, r):
    if r.get('latitude') is None or r.get('longitude') is None: return
    rows.append(r)
def is_competitor(name, typ, tags):
    txt=' '.join([name,typ,json.dumps(tags).lower()]).lower()
    terms=['preschool','pre-school','nursery','montessori','child care','childcare','daycare','early childhood','kindergarten','bilingual','dual language','mandarin','spanish','language']
    excluded=['high school','middle school','college','university','driving','dance','dancing','music school','business school','law school']
    return any(t in txt for t in terms) and not any(bad in txt for bad in excluded)
def main():
    b=bounds(load(DATA/'hgl_zip_market_enriched.geojson'))
    schools=[]; comps=[]
    # DOE official school locations: include schools with PK/K/elementary in bbox.
    where=f"latitude between {b[1]} and {b[3]} and longitude between {b[0]} and {b[2]}"
    for r in socrata('data.cityofnewyork.us','wg9x-4ke6',where=where):
        lat=fnum(r.get('latitude')); lon=fnum(r.get('longitude'))
        if lat is None or lon is None or not in_bbox(lon,lat,b): continue
        grades=clean(r.get('grades_final_text') or r.get('grades_text'))
        if not any(x in grades for x in ['PK','0K','01','02','03','04','05']): continue
        name=clean(r.get('location_name'))
        rec={'site_id':'DOE-'+clean(r.get('location_code') or r.get('system_code')),'site_name':name,'site_type':clean(r.get('location_category_description') or 'School'),'provider_type':'NYC DOE / public school','address':clean(r.get('primary_address_line_1')),'latitude':lat,'longitude':lon,'zip_code':zip_guess(lon,lat),'age_focus':grades,'language_offer_if_known':'Not specified in source','public_or_private':'Public','source_name':'NYC Open Data 2019-2020 School Locations','source_url':'https://data.cityofnewyork.us/Education/2019-2020-School-Locations/wg9x-4ke6','retrieval_date':TODAY,'confidence_level':'High','notes':'Official DOE school location record; included when PK/K/elementary grades are listed.'}
        add_school(schools,rec)
    # OSM schools/preschools/childcare.
    for el in overpass(b).get('elements',[]):
        tags=el.get('tags',{}); lat=el.get('lat') or el.get('center',{}).get('lat'); lon=el.get('lon') or el.get('center',{}).get('lon')
        lat=fnum(lat); lon=fnum(lon)
        if lat is None or lon is None: continue
        name=clean(tags.get('name') or tags.get('operator') or 'Unnamed school/preschool')
        amen=clean(tags.get('amenity') or 'school')
        if amen not in ['school','kindergarten','childcare']:
            continue
        addr=clean(' '.join([tags.get('addr:housenumber',''),tags.get('addr:street','')])) or clean(tags.get('addr:full'))
        age='Early childhood / preschool likely' if amen in ['kindergarten','childcare'] or 'preschool' in name.lower() or 'nursery' in name.lower() else 'School-age / verify early-childhood relevance'
        rec={'site_id':'OSM-'+str(el.get('id')),'site_name':name,'site_type':amen.title(),'provider_type':clean(tags.get('operator:type') or tags.get('operator') or 'Public/private not specified'),'address':addr,'latitude':lat,'longitude':lon,'zip_code':clean(tags.get('addr:postcode') or zip_guess(lon,lat)),'age_focus':age,'language_offer_if_known':clean(tags.get('language') or tags.get('isced:level') or 'Not specified in source'),'public_or_private':clean(tags.get('operator:type') or tags.get('ownership') or 'Unknown'),'source_name':'OpenStreetMap Overpass amenity school/kindergarten/childcare','source_url':'https://www.openstreetmap.org/'+('node' if el.get('type')=='node' else 'way')+'/'+str(el.get('id')),'retrieval_date':TODAY,'confidence_level':'Medium','notes':'OSM public POI; verify program details before client claims.'}
        add_school(schools,rec)
        if is_competitor(name,amen,tags):
            comps.append({'competitor_id':'COMP-'+str(el.get('id')),'competitor_name':name,'competitor_type':amen.title() if amen!='school' else 'School / early education provider','address':addr,'latitude':lat,'longitude':lon,'zip_code':rec['zip_code'],'age_focus':age,'language_positioning_if_known':rec['language_offer_if_known'],'art_or_specialty_positioning_if_known':clean(tags.get('description') or tags.get('school:type') or 'Not specified in source'),'public_or_private_if_known':rec['public_or_private'],'source_name':rec['source_name'],'source_url':rec['source_url'],'retrieval_date':TODAY,'confidence_level':'Medium','notes':'Competitor relevance inferred from public POI name/type/tags; verify offering and enrollment market fit.'})
    # Deduplicate schools and competitors.
    sd={}
    for r in schools:
        k=key(r['longitude'],r['latitude'],r['site_name'])
        if k not in sd or r['source_name'].startswith('NYC Open Data'): sd[k]=r
    cd={}
    for r in comps:
        k=key(r['longitude'],r['latitude'],r['competitor_name'])
        if k not in cd: cd[k]=r
    schools=list(sd.values()); comps=list(cd.values())
    def gj_school(rows): return {'type':'FeatureCollection','name':'schools_preschools_v5_1','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[r['longitude'],r['latitude']]},'properties':{k:v for k,v in r.items() if k not in ['longitude','latitude']}} for r in rows]}
    def gj_comp(rows): return {'type':'FeatureCollection','name':'competitors_v5_1','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[r['longitude'],r['latitude']]},'properties':{k:v for k,v in r.items() if k not in ['longitude','latitude']}} for r in rows]}
    writej(DATA/'schools_preschools.geojson',gj_school(schools)); writej(DATA/'competitors.geojson',gj_comp(comps))
    for fname,rows in [('schools_preschools.csv',schools),('competitors.csv',comps)]:
        keys=sorted({k for r in rows for k in r.keys()})
        with (PROC/fname).open('w',newline='',encoding='utf-8') as fh:
            w=csv.DictWriter(fh,fieldnames=keys); w.writeheader(); w.writerows(rows)
    school_types=Counter(r['site_type'] for r in schools); comp_types=Counter(r['competitor_type'] for r in comps)
    (DOCS/'schools_preschools_data_report.md').write_text('\n'.join(['# Schools / Preschools Data Report','',f'- Records: {len(schools)}','- Sources attempted: NYC Open Data DOE school locations; OpenStreetMap Overpass school/kindergarten/childcare POIs.','- Google/business listings were not used as sole proof.','', '## Count by type', *[f'- {k}: {v}' for k,v in school_types.items()], '', '## Limitations','- OSM program attributes may be incomplete; verify age focus/language offerings before client claims.','- DOE records are official school locations but not all are preschool providers.'])+'\n',encoding='utf-8')
    (DOCS/'competitor_data_report.md').write_text('\n'.join(['# Competitor Data Report','',f'- Records: {len(comps)}','- Competitor relevance limited to early education / preschool / childcare / school-like providers; generic unrelated art studios are not default competitors.','- Sources attempted: OSM public POIs, NYC DOE school source context, local repo scan.','', '## Count by type', *[f'- {k}: {v}' for k,v in comp_types.items()], '', '## Limitations','- Competitor classification is conservative and should be verified against provider websites/directories before outreach or final market claims.'])+'\n',encoding='utf-8')
    (LOGS/'v5_1_schools_competitors_status.json').write_text(json.dumps({'schools':len(schools),'competitors':len(comps),'school_types':dict(school_types),'competitor_types':dict(comp_types)},indent=2),encoding='utf-8')
    print(json.dumps({'schools':len(schools),'competitors':len(comps)},indent=2))
if __name__=='__main__': main()
