#!/usr/bin/env python3
import csv, json, math, urllib.parse, urllib.request
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'public/data'; DOCS=ROOT/'docs'; LOGS=ROOT/'logs'; PROC=ROOT/'processed_data'
TODAY='2026-06-11'
CATS=['Parks / playgrounds','Libraries','Child activity','Pediatric / health','Family retail / grocery','Museums / culture','Community centers','Transit / corridors','Birthday / camp / event']

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def writej(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
def fetch(url,data=None):
    req=urllib.request.Request(url,data=data,headers={'User-Agent':'Hermes-HGL-v5.2-family-anchors/1.0'})
    with urllib.request.urlopen(req,timeout=120) as r: return r.read().decode('utf-8')
def bounds(gj):
    xs=[]; ys=[]
    def walk(c):
        if isinstance(c,list) and len(c)>=2 and isinstance(c[0],(int,float)) and isinstance(c[1],(int,float)): xs.append(c[0]); ys.append(c[1])
        elif isinstance(c,list):
            for x in c: walk(x)
    for f in gj['features']: walk(f['geometry']['coordinates'])
    return min(xs)-0.011,min(ys)-0.0073,max(xs)+0.011,max(ys)+0.0073
def overpass(b):
    s,w,n,e=b[1],b[0],b[3],b[2]
    q=f'''[out:json][timeout:90];(
      node["leisure"~"playground|park|fitness_centre|sports_centre"]({s},{w},{n},{e});way["leisure"~"playground|park|fitness_centre|sports_centre"]({s},{w},{n},{e});relation["leisure"~"playground|park"]({s},{w},{n},{e});
      node["amenity"~"library|childcare|kindergarten|clinic|doctors|dentist|pharmacy|community_centre|place_of_worship|arts_centre|theatre|school"]({s},{w},{n},{e});way["amenity"~"library|childcare|kindergarten|clinic|doctors|dentist|pharmacy|community_centre|place_of_worship|arts_centre|theatre|school"]({s},{w},{n},{e});
      node["shop"~"toys|baby_goods|books|supermarket|convenience|clothes|department_store|chemist"]({s},{w},{n},{e});way["shop"~"toys|baby_goods|books|supermarket|convenience|clothes|department_store|chemist"]({s},{w},{n},{e});
      node["tourism"~"museum|gallery|attraction"]({s},{w},{n},{e});way["tourism"~"museum|gallery|attraction"]({s},{w},{n},{e});
      node["railway"="station"]({s},{w},{n},{e});node["public_transport"="station"]({s},{w},{n},{e});
    );out center tags;'''
    try: return json.loads(fetch('https://overpass-api.de/api/interpreter', urllib.parse.urlencode({'data':q}).encode()))
    except Exception as e: (LOGS/'v5_2_overpass_error.log').write_text(str(e),encoding='utf-8'); return {'elements':[]}
def fnum(x):
    try: return float(x)
    except Exception: return None
def in_bbox(lon,lat,b): return b[0]<=lon<=b[2] and b[1]<=lat<=b[3]
def clean(x): return ' '.join(str(x or '').split())
def classify(tags,name):
    amen=clean(tags.get('amenity')).lower(); leisure=clean(tags.get('leisure')).lower(); shop=clean(tags.get('shop')).lower(); tourism=clean(tags.get('tourism')).lower(); railway=clean(tags.get('railway')).lower(); pt=clean(tags.get('public_transport')).lower(); txt=' '.join([name,amen,leisure,shop,tourism,clean(tags.get('healthcare')),clean(tags.get('description'))]).lower()
    if leisure in ['playground','park'] or 'playground' in txt or 'park' in txt: return 'Parks / playgrounds', leisure or 'park/open space'
    if amen=='library' or shop=='books': return 'Libraries' if amen=='library' else 'Family retail / grocery', amen or shop
    if amen in ['childcare','kindergarten'] or any(t in txt for t in ['toddler','kids gym','children','play space','camp','birthday']): return 'Child activity', amen or 'child activity'
    if amen in ['clinic','doctors','dentist','pharmacy'] or shop in ['chemist'] or any(t in txt for t in ['pediatric','paediatric','children\'s dentist','speech therapy','occupational therapy']): return 'Pediatric / health', amen or shop or 'health'
    if shop in ['toys','baby_goods','supermarket','convenience','clothes','department_store'] or any(t in txt for t in ['target','whole foods','trader joe','baby','toy']): return 'Family retail / grocery', shop or 'family retail/grocery'
    if tourism in ['museum','gallery','attraction'] or amen in ['arts_centre','theatre']: return 'Museums / culture', tourism or amen
    if amen in ['community_centre','place_of_worship']: return 'Community centers', amen
    if railway=='station' or pt=='station' or any(t in txt for t in ['subway','station']): return 'Transit / corridors', railway or pt or 'station'
    if any(t in txt for t in ['party','birthday','camp','event']): return 'Birthday / camp / event', 'event/camp'
    return None, None
def relevance(cat):
    m={
      'Parks / playgrounds':('High','High','Strong indicator of under-5 recreation and caregiver trips.'),
      'Libraries':('Medium-High','High','Early literacy and children programming context.'),
      'Child activity':('High','High','Direct parent-child activity context.'),
      'Pediatric / health':('Medium','High','Family health errand context.'),
      'Family retail / grocery':('Medium','Medium-High','Parent/caregiver errand context.'),
      'Museums / culture':('Medium','Medium','Family education/culture context.'),
      'Community centers':('Medium','Medium','Community family-program context where publicly listed.'),
      'Transit / corridors':('Low-Medium','Medium','Pickup/drop-off and stroller corridor context.'),
      'Birthday / camp / event':('Medium-High','High','Young-child events/camp/party context.')}
    return m.get(cat,('Medium','Medium','Family-relevant public context.'))
def main():
    b=bounds(load(DATA/'hgl_zip_market_enriched.geojson'))
    school_pts={(round(ft['geometry']['coordinates'][1],5),round(ft['geometry']['coordinates'][0],5)) for ft in load(DATA/'schools_preschools.geojson').get('features',[])} if (DATA/'schools_preschools.geojson').exists() else set()
    comp_pts={(round(ft['geometry']['coordinates'][1],5),round(ft['geometry']['coordinates'][0],5)) for ft in load(DATA/'competitors.geojson').get('features',[])} if (DATA/'competitors.geojson').exists() else set()
    rows=[]; seen={}
    old=load(DATA/'hgl_family_anchors.geojson') if (DATA/'hgl_family_anchors.geojson').exists() else {'features':[]}
    for ft in old.get('features',[]):
        if not ft.get('geometry'): continue
        lon,lat=ft['geometry']['coordinates']; p=ft.get('properties',{}); name=clean(p.get('anchor_name') or p.get('name') or p.get('site_name') or 'Existing family anchor')
        cat=clean(p.get('anchor_category') or 'Community centers')
        if cat not in CATS: cat='Community centers'
        u5,parent,note=relevance(cat)
        rows.append({'anchor_id':'OLD-'+str(len(rows)+1),'anchor_name':name,'anchor_category':cat,'anchor_subcategory':clean(p.get('anchor_subcategory') or p.get('anchor_type') or cat),'address_or_intersection':clean(p.get('address_or_intersection') or p.get('address') or ''),'latitude':lat,'longitude':lon,'zip_code':clean(p.get('zip_code') or p.get('zipcode') or 'buffer/unknown'),'source_name':'Existing local family anchor data','source_url':'local repo public/data/hgl_family_anchors.geojson','retrieval_date':TODAY,'confidence_level':'Medium','relevance_to_under5':u5,'relevance_to_parent_caregiver':parent,'relevance_to_hgl':note,'duplicate_of_school_layer':False,'duplicate_of_competitor_layer':False,'notes':'Existing public-context anchor carried forward.'})
    for el in overpass(b).get('elements',[]):
        tags=el.get('tags',{}); lat=fnum(el.get('lat') or el.get('center',{}).get('lat')); lon=fnum(el.get('lon') or el.get('center',{}).get('lon'))
        if lat is None or lon is None or not in_bbox(lon,lat,b): continue
        name=clean(tags.get('name') or tags.get('operator') or tags.get('brand') or 'Unnamed public anchor')
        cat,sub=classify(tags,name)
        if not cat: continue
        coord=(round(lat,5),round(lon,5)); dup_school=coord in school_pts; dup_comp=coord in comp_pts
        # Do not duplicate schools/preschools/competitors as family-anchor markers; they are used in scoring via their own layers.
        if dup_school or dup_comp: continue
        k=(coord,name.lower()[:60],cat)
        if k in seen: continue
        seen[k]=1
        addr=clean(' '.join([tags.get('addr:housenumber',''),tags.get('addr:street','')])) or clean(tags.get('addr:full'))
        u5,parent,note=relevance(cat)
        rows.append({'anchor_id':'FA-V5-2-'+str(len(rows)+1).zfill(4),'anchor_name':name,'anchor_category':cat,'anchor_subcategory':sub,'address_or_intersection':addr,'latitude':lat,'longitude':lon,'zip_code':clean(tags.get('addr:postcode') or 'buffer/unknown'),'source_name':'OpenStreetMap Overpass public POI','source_url':'https://www.openstreetmap.org/'+('node' if el.get('type')=='node' else 'way')+'/'+str(el.get('id')),'retrieval_date':TODAY,'confidence_level':'Medium','relevance_to_under5':u5,'relevance_to_parent_caregiver':parent,'relevance_to_hgl':note,'duplicate_of_school_layer':False,'duplicate_of_competitor_layer':False,'notes':'Public/commercial/community context signal; verify details before claims.'})
    feats=[{'type':'Feature','geometry':{'type':'Point','coordinates':[r['longitude'],r['latitude']]},'properties':{k:v for k,v in r.items() if k not in ['longitude','latitude']}} for r in rows]
    gj={'type':'FeatureCollection','name':'family_anchors_expanded_v5_2','features':feats}
    writej(DATA/'family_anchors_expanded.geojson',gj); writej(DATA/'hgl_family_anchors.geojson',gj)
    keys=['anchor_id','anchor_name','anchor_category','anchor_subcategory','address_or_intersection','latitude','longitude','zip_code','source_name','source_url','retrieval_date','confidence_level','relevance_to_under5','relevance_to_parent_caregiver','relevance_to_hgl','duplicate_of_school_layer','duplicate_of_competitor_layer','notes']
    with (PROC/'family_anchors_expanded.csv').open('w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=keys); w.writeheader(); w.writerows(rows)
    counts=Counter(r['anchor_category'] for r in rows); zips=Counter(r['zip_code'] for r in rows)
    md=['# Family Anchors Expansion Report','', 'Label: Family-Relevant Public Anchors / 亲子家庭相关公共场景点','',f'- Total records: {len(rows)}','- Sources attempted: existing local anchors; OpenStreetMap Overpass POIs for parks/playgrounds, libraries, childcare, pediatric/clinic/pharmacy, family retail/grocery, museums/culture, community centers, transit stations/corridors, event/camp-style venues.', '- Schools/preschools and competitors are not duplicated as anchor markers when coordinates match; their proximity is integrated as related context in scoring.', '', '## Count by category']
    md += [f'- {k}: {counts.get(k,0)}' for k in CATS]
    md += ['', '## Limitations','- OSM/public POI completeness varies by category.','- These are public context signals, not home addresses or individual family data.','- Provider/program details should be verified before client claims.']
    (DOCS/'family_anchors_expansion_report.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    status={'total':len(rows),'by_category':dict(counts),'by_zip':dict(zips),'zero_categories':[c for c in CATS if counts.get(c,0)==0]}
    (LOGS/'v5_2_family_anchor_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))
if __name__=='__main__': main()
