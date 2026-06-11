#!/usr/bin/env python3
import csv, json, math, urllib.parse, urllib.request, time
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'public/data'; PROC=ROOT/'processed_data'; DOCS=ROOT/'docs'; LOGS=ROOT/'logs'
TARGET_ZIPS={'10011','10010','10003','10014','10012','10013'}
TODAY='2026-06-11'

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def writej(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Hermes-HGL-v4-ooh-public-source-build/1.0'})
    with urllib.request.urlopen(req,timeout=90) as r: return json.loads(r.read().decode())
def socrata(domain,resource,where=None,limit=50000):
    out=[]; off=0
    while True:
        params={'$limit':str(limit),'$offset':str(off)}
        if where: params['$where']=where
        url=f'https://{domain}/resource/{resource}.json?'+urllib.parse.urlencode(params)
        try: rows=fetch(url)
        except Exception as e:
            (LOGS/f'v4_ooh_fetch_error_{resource}.log').write_text(str(e),encoding='utf-8'); return out
        out.extend(rows)
        if len(rows)<limit: break
        off+=limit; time.sleep(0.2)
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

def in_bbox(lon,lat,b): return b[0]<=lon<=b[2] and b[1]<=lat<=b[3]
def rndkey(lon,lat,vendor,typ): return (round(lat,5),round(lon,5),vendor.lower(),typ.lower())
def fnum(x):
    try: return float(x)
    except Exception: return None

def add(rows, row):
    lat=fnum(row.get('latitude')); lon=fnum(row.get('longitude'))
    if lat is None or lon is None: return
    row['latitude']=lat; row['longitude']=lon
    if 'zipcode' not in row or not row['zipcode']: row['zipcode']='buffer/unknown'
    rows.append(row)

def main():
    LOGS.mkdir(exist_ok=True); DOCS.mkdir(exist_ok=True); PROC.mkdir(exist_ok=True)
    bbox=bounds(load(DATA/'hgl_zip_market_enriched.geojson'))
    old=load(DATA/'ooh_assets_expanded.geojson') if (DATA/'ooh_assets_expanded.geojson').exists() else {'features':[]}
    rows=[]
    for ft in old.get('features',[]):
        p=dict(ft.get('properties',{})); p['longitude']=ft['geometry']['coordinates'][0]; p['latitude']=ft['geometry']['coordinates'][1]; p['source_name']=p.get('source_name') or 'Previous HGL v3 OOH candidate file'; add(rows,p)
    # LinkNYC kiosks.
    for r in socrata('data.cityofnewyork.us','s4kf-3yrf'):
        lat=fnum(r.get('latitude') or r.get('lat')); lon=fnum(r.get('longitude') or r.get('lon') or r.get('long'))
        if lat is None or lon is None or not in_bbox(lon,lat,bbox): continue
        add(rows,{'asset_name':r.get('link_site_id') or r.get('site_id') or r.get('address') or 'LinkNYC kiosk','asset_type':'LinkNYC','vendor_owner':'LinkNYC / Intersection','operator_if_known':'LinkNYC / Intersection','address_or_intersection':r.get('street_address') or r.get('address') or r.get('location_name') or 'LinkNYC kiosk location','latitude':lat,'longitude':lon,'zipcode':str(r.get('zip') or r.get('zipcode') or 'buffer/unknown'),'media_format':'LinkNYC digital kiosk / network street furniture','static_or_digital':'Digital network; exact unit/date requires vendor confirmation','asset_status':'Network bookable','availability_status':'Network bookable; unit-level availability unconfirmed','availability_confidence':'High network presence; availability unconfirmed','source_name':'NYC Open Data LinkNYC Kiosk Locations s4kf-3yrf','source_url':'https://data.cityofnewyork.us/Social-Services/LinkNYC-Kiosk-Locations/s4kf-3yrf','retrieval_date':TODAY,'pricing_status':'Quote/vendor confirmation required','exact_price_confirmed':False,'impressions_status':'Vendor confirmation required','exact_impressions_confirmed':False,'hgl_relevance_score':7.8,'recommended_use':'Network awareness near family/transit corridors','verification_needed':'Confirm availability, creative specs, dayparting, price, and exact unit booking with vendor.','confidence_level':'High','caveat':'Public location only; availability/pricing/impressions require vendor confirmation.'})
    # Bus shelters.
    for r in socrata('data.cityofnewyork.us','t4f2-8md7'):
        lat=fnum(r.get('latitude')); lon=fnum(r.get('longitude'))
        if lat is None or lon is None or not in_bbox(lon,lat,bbox): continue
        add(rows,{'asset_name':r.get('shelter_id') or r.get('asset_id') or 'NYC bus shelter','asset_type':'Bus shelters','vendor_owner':'JCDecaux / NYC street furniture network','operator_if_known':'JCDecaux','address_or_intersection':r.get('on_street') or r.get('street') or r.get('location') or r.get('nearest_intersection') or 'Bus shelter location','latitude':lat,'longitude':lon,'zipcode':str(r.get('zip_code') or r.get('zipcode') or 'buffer/unknown'),'media_format':'Bus shelter street furniture panel','static_or_digital':'Static/digital status must be verified','asset_status':'Network bookable','availability_status':'Network bookable; unit-level availability unconfirmed','availability_confidence':'Medium-High network presence; availability unconfirmed','source_name':'NYC Open Data Bus Stop Shelters t4f2-8md7','source_url':'https://data.cityofnewyork.us/Transportation/Bus-Stop-Shelters/t4f2-8md7','retrieval_date':TODAY,'pricing_status':'Quote/vendor confirmation required','exact_price_confirmed':False,'impressions_status':'Vendor confirmation required','exact_impressions_confirmed':False,'hgl_relevance_score':7.1,'recommended_use':'Street-level parent/caregiver awareness; verify shelter face and format.','verification_needed':'Confirm unit status, dates, price, creative specs, and impressions with JCDecaux/vendor.','confidence_level':'Medium-High','caveat':'Public location only; no availability, price, or impression guarantee.'})
    # MTA station complexes as ad-location proxy.
    for r in socrata('data.ny.gov','5f5g-n3cz'):
        lat=fnum(r.get('gtfs_latitude') or r.get('latitude')); lon=fnum(r.get('gtfs_longitude') or r.get('longitude'))
        if lat is None or lon is None or not in_bbox(lon,lat,bbox): continue
        add(rows,{'asset_name':r.get('stop_name') or r.get('station_name') or 'MTA subway station','asset_type':'Subway / MTA','vendor_owner':'MTA / OUTFRONT or station media vendor','operator_if_known':'MTA / OUTFRONT media subject to verification','address_or_intersection':r.get('stop_name') or r.get('station_name') or 'Subway station','latitude':lat,'longitude':lon,'zipcode':'buffer/unknown','media_format':'Subway station advertising location proxy','static_or_digital':'Station inventory varies; verify with vendor','asset_status':'Potentially bookable','availability_status':'Station/complex ad inventory likely network-bookable; exact units unconfirmed','availability_confidence':'Medium source confidence; unit availability unconfirmed','source_name':'NYS Open Data MTA Subway Stations and Complexes 5f5g-n3cz','source_url':'https://data.ny.gov/Transportation/MTA-Subway-Stations-and-Complexes/5f5g-n3cz','retrieval_date':TODAY,'pricing_status':'Quote/vendor confirmation required','exact_price_confirmed':False,'impressions_status':'Vendor confirmation required','exact_impressions_confirmed':False,'hgl_relevance_score':7.4,'recommended_use':'Transit-proximity awareness; request actual station media inventory from vendor.','verification_needed':'Confirm station media units, availability, pricing, impressions, and creative specs with MTA/OUTFRONT/vendor.','confidence_level':'Medium','caveat':'Station point is not a confirmed available ad unit.'})
    # DOB outdoor advertising / sign permits: attempt known endpoint if accessible, tolerate failure.
    # Deduplicate.
    dedup={}
    for r in rows:
        k=rndkey(r['longitude'],r['latitude'],r.get('vendor_owner',''),r.get('asset_type',''))
        if k not in dedup or str(r.get('source_name','')).startswith('NYC Open Data'):
            dedup[k]=r
    out=[]
    for i,r in enumerate(dedup.values(),1):
        typ=r.get('asset_type','Other')
        r.setdefault('asset_status','Candidate to verify')
        if r['asset_status']=='Not recommended': continue
        r.setdefault('availability_status','Availability unknown; verification required')
        r.setdefault('availability_confidence','Unconfirmed')
        r.setdefault('pricing_status','Quote/vendor confirmation required')
        r.setdefault('exact_price_confirmed',False); r.setdefault('exact_impressions_confirmed',False)
        r.setdefault('impressions_status','Vendor confirmation required'); r.setdefault('verification_needed','Vendor confirmation required before any media buy.')
        r.setdefault('confidence_level','Medium'); r.setdefault('caveat','Availability, pricing, and exact unit selection must be confirmed with vendor.')
        r['ooh_asset_id']=f'OOH-V4-{i:04d}'
        out.append({'type':'Feature','geometry':{'type':'Point','coordinates':[r['longitude'],r['latitude']]},'properties':{k:v for k,v in r.items() if k not in ['longitude','latitude']}})
    gj={'type':'FeatureCollection','name':'ooh_assets_expanded_v4','features':out}
    writej(DATA/'ooh_assets_expanded_v4.geojson',gj)
    writej(DATA/'ooh_assets_expanded.geojson',gj)
    keys=sorted({k for ft in out for k in ft['properties']})+['longitude','latitude']
    with (PROC/'ooh_assets_expanded_v4.csv').open('w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=keys); w.writeheader()
        for ft in out:
            p=dict(ft['properties']); p['longitude']=ft['geometry']['coordinates'][0]; p['latitude']=ft['geometry']['coordinates'][1]; w.writerow(p)
    vendors=Counter(ft['properties'].get('vendor_owner','Unknown') for ft in out); types=Counter(ft['properties'].get('asset_type','Unknown') for ft in out); statuses=Counter(ft['properties'].get('asset_status','Unknown') for ft in out); zips=Counter(ft['properties'].get('zipcode','Unknown') for ft in out)
    md=['# OOH Inventory Expansion v4','',f'- Old OOH count: {len(old.get("features",[]))}',f'- New OOH count: {len(out)}','', '## Count by vendor']
    md += [f'- {k}: {v}' for k,v in vendors.most_common()]
    md += ['', '## Count by asset type']+[f'- {k}: {v}' for k,v in types.most_common()]
    md += ['', '## Count by ZIP']+[f'- {k}: {v}' for k,v in zips.most_common()]
    md += ['', '## Count by status']+[f'- {k}: {v}' for k,v in statuses.most_common()]
    md += ['', '## Sources used','- Previous v3 OOH candidate file','- NYC Open Data LinkNYC Kiosk Locations','- NYC Open Data Bus Stop Shelters','- NYS Open Data MTA Subway Stations and Complexes as station-advertising proxies','', '## Limitations','- Public feeds identify network/location presence, not guaranteed availability, price, impression delivery, or creative specifications.','- Vendor RFP/API acquisition is still required before purchase.','- Assets are deduplicated by rounded coordinate + vendor + asset type; adjacent faces may be collapsed if public feeds lack face-level IDs.']
    if len(out)<75: md.append('- Fewer than 75 assets were found; do not fake records. Recommend direct vendor RFP/API acquisition.')
    (DOCS/'ooh_inventory_expansion_v4.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    status={'old_count':len(old.get('features',[])),'new_count':len(out),'vendors':dict(vendors),'types':dict(types),'statuses':dict(statuses),'zips':dict(zips)}
    (LOGS/'v4_ooh_inventory_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))
if __name__=='__main__': main()
