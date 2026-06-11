#!/usr/bin/env python3
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'public/data'; DOCS=ROOT/'docs'; LOGS=ROOT/'logs'
CATS=['Parks / playgrounds','Libraries','Child activity','Pediatric / health','Family retail / grocery','Museums / culture','Community centers','Transit / corridors','Birthday / camp / event']
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def writej(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
def pts(gj): return [(ft['geometry']['coordinates'][0],ft['geometry']['coordinates'][1],ft['properties']) for ft in gj.get('features',[]) if ft.get('geometry')]
def hav(lon1,lat1,lon2,lat2):
    R=6371000; p1=math.radians(lat1); p2=math.radians(lat2); dphi=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    a=math.sin(dphi/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))
def centroid(geom):
    arr=[]
    def walk(c):
        if isinstance(c,list) and len(c)>=2 and isinstance(c[0],(int,float)) and isinstance(c[1],(int,float)): arr.append((c[0],c[1]))
        elif isinstance(c,list):
            for x in c: walk(x)
    walk(geom.get('coordinates',[]))
    if not arr: return None
    return (sum(x for x,y in arr)/len(arr),sum(y for x,y in arr)/len(arr))
def near(lon,lat,points,r): return [(x,y,p,hav(lon,lat,x,y)) for x,y,p in points if hav(lon,lat,x,y)<=r]
def nearest(lon,lat,points):
    best=None
    for x,y,p in points:
        d=hav(lon,lat,x,y)
        if best is None or d<best[3]: best=(x,y,p,d)
    return best
def main():
    anchors=pts(load(DATA/'family_anchors_expanded.geojson'))
    streets=load(DATA/'street_under5_capacity_signal.geojson'); buildings=load(DATA/'buildings_residential_capacity_v5.geojson'); ooh=load(DATA/'ooh_assets_expanded_v4.geojson')
    for gj,kind in [(streets,'street'),(buildings,'building'),(ooh,'ooh')]:
        for ft in gj.get('features',[]):
            p=ft.get('properties',{}); c=ft.get('geometry',{}).get('coordinates') if ft.get('geometry',{}).get('type')=='Point' else None
            if not c: c=centroid(ft.get('geometry',{})) or p.get('centroid')
            if not c or c[0] is None: continue
            lon,lat=c[0],c[1]
            n100=near(lon,lat,anchors,100); n250=near(lon,lat,anchors,250)
            counts={cat:sum(1 for _,_,ap,_ in n250 if ap.get('anchor_category')==cat) for cat in CATS}
            if kind=='street':
                p['family_anchor_count_100m']=len(n100); p['family_anchor_count_250m']=len(n250)
                p['playground_count_250m']=counts['Parks / playgrounds']; p['library_count_250m']=counts['Libraries']; p['child_activity_count_250m']=counts['Child activity']; p['pediatric_anchor_count_250m']=counts['Pediatric / health']; p['family_retail_count_250m']=counts['Family retail / grocery']; p['cultural_family_anchor_count_250m']=counts['Museums / culture']
                p['family_anchor_density_score']=round(min(10,len(n250)/4),2)
                base=float(p.get('hgl_street_opportunity_score') or 0); p['hgl_street_opportunity_score']=round(min(10,base+min(0.8,len(n250)*0.03)),2)
            elif kind=='building':
                best=nearest(lon,lat,anchors); p['nearest_family_anchor_distance']=round(best[3],1) if best else None
                p['family_anchor_count_250m']=len(n250); p['under5_family_context_score']=round(min(10,(counts['Parks / playgrounds']+counts['Child activity']*2+counts['Libraries']+counts['Pediatric / health'])/2),2); p['parent_caregiver_context_score']=round(min(10,len(n250)/4),2)
                base=float(p.get('hgl_building_opportunity_score') or 0); p['hgl_building_opportunity_score']=round(min(10,base+min(0.5,len(n250)*0.02)),2); p['hgl_opportunity_score']=p['hgl_building_opportunity_score']
            else:
                best=nearest(lon,lat,anchors); p['family_anchor_count_250m']=len(n250); p['nearest_family_anchor_type']=best[2].get('anchor_category') if best else None; p['family_context_relevance_score']=round(min(10,len(n250)/3),2)
                base=float(p.get('hgl_relevance_score') or 0); p['hgl_relevance_score']=round(min(10,base+min(0.6,len(n250)*0.025)),2)
    writej(DATA/'street_under5_capacity_signal.geojson',streets); writej(DATA/'street_segments_enriched.geojson',streets)
    writej(DATA/'buildings_residential_capacity_v5.geojson',buildings); writej(DATA/'buildings_residential_capacity.geojson',buildings); writej(DATA/'buildings_enriched.geojson',buildings)
    writej(DATA/'ooh_assets_expanded_v4.geojson',ooh); writej(DATA/'ooh_assets_expanded.geojson',ooh)
    (DOCS/'family_anchors_scoring_integration_v5_2.md').write_text('\n'.join(['# Family Anchors Scoring Integration v5.2','', '- Street fields added: family_anchor_count_100m, family_anchor_count_250m, playground_count_250m, library_count_250m, child_activity_count_250m, pediatric_anchor_count_250m, family_retail_count_250m, cultural_family_anchor_count_250m, family_anchor_density_score.', '- Building fields added: nearest_family_anchor_distance, family_anchor_count_250m, under5_family_context_score, parent_caregiver_context_score.', '- OOH fields added: family_anchor_count_250m, nearest_family_anchor_type, family_context_relevance_score.', '- Family anchors improve context relevance but do not replace residential capacity or official aggregate demographic data.', '- These are public context signals, not household or individual family data.'])+'\n',encoding='utf-8')
    (LOGS/'v5_2_family_scoring_status.json').write_text(json.dumps({'anchors':len(anchors),'streets':len(streets.get('features',[])),'buildings':len(buildings.get('features',[])),'ooh':len(ooh.get('features',[]))},indent=2),encoding='utf-8')
    print('family scoring integrated')
if __name__=='__main__': main()
