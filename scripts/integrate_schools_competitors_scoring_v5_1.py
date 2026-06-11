#!/usr/bin/env python3
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'public/data'; DOCS=ROOT/'docs'; LOGS=ROOT/'logs'
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
    return (sum(x for x,y in arr)/len(arr), sum(y for x,y in arr)/len(arr))
def count_near(lon,lat,points,r=250): return sum(1 for x,y,p in points if hav(lon,lat,x,y)<=r)
def main():
    schools=pts(load(DATA/'schools_preschools.geojson')); comps=pts(load(DATA/'competitors.geojson'))
    streets=load(DATA/'street_under5_capacity_signal.geojson'); buildings=load(DATA/'buildings_residential_capacity_v5.geojson')
    for gj,kind in [(streets,'street'),(buildings,'building')]:
        for ft in gj.get('features',[]):
            p=ft.get('properties',{}); c=centroid(ft.get('geometry',{})) or p.get('centroid')
            if not c or c[0] is None: continue
            lon,lat=c[0],c[1]
            sc=count_near(lon,lat,schools,250); cc=count_near(lon,lat,comps,250)
            if kind=='street':
                p['preschool_school_anchor_count_250m']=sc; p['competitor_count_250m']=cc
                p['school_preschool_anchor_density']=round(sc/2.5,3); p['competitor_density']=round(cc/2.5,3)
                p['proximity_to_preschool_cluster']=min(10,sc*2); p['proximity_to_competitor_cluster']=min(10,cc*2)
                base=float(p.get('hgl_street_opportunity_score') or p.get('hgl_opportunity_score') or 0)
                demand=min(1,sc/5)*0.7; pressure=min(1,cc/5)*0.35
                p['hgl_street_opportunity_score']=round(max(0,min(10,base+demand-pressure)),2)
                p['school_competitor_scoring_note']='Schools/preschools add family-corridor relevance; competitors indicate demand concentration but subtract competition pressure.'
            else:
                p['nearby_preschool_count_250m']=sc; p['nearby_competitor_count_250m']=cc
                p['preschool_access_signal']=min(10,sc*2); p['competitor_pressure_signal']=min(10,cc*2)
                base=float(p.get('hgl_building_opportunity_score') or 0)
                p['hgl_building_opportunity_score']=round(max(0,min(10,base+min(0.6,sc*0.12)-min(0.4,cc*0.10))),2)
                p['hgl_opportunity_score']=p['hgl_building_opportunity_score']
                p['school_competitor_scoring_note']='Nearby preschools raise access/family relevance; nearby competitors add demand evidence but reduce net opportunity through pressure.'
    writej(DATA/'street_under5_capacity_signal.geojson',streets); writej(DATA/'street_segments_enriched.geojson',streets)
    writej(DATA/'buildings_residential_capacity_v5.geojson',buildings); writej(DATA/'buildings_residential_capacity.geojson',buildings); writej(DATA/'buildings_enriched.geojson',buildings)
    (DOCS/'schools_competitors_scoring_integration.md').write_text('\n'.join(['# Schools / Competitors Scoring Integration','', '- Street inputs added: preschool_school_anchor_count_250m, competitor_count_250m, competitor_density, school_preschool_anchor_density, proximity_to_preschool_cluster, proximity_to_competitor_cluster.', '- Building inputs added: nearby_preschool_count_250m, nearby_competitor_count_250m, preschool_access_signal, competitor_pressure_signal.', '- Schools/preschools increase family relevance and child-serving corridor relevance.', '- Competitors indicate demand concentration but also competition pressure; scores apply a smaller negative pressure adjustment against the positive demand-context signal.', '- All scores remain modeled decision-support signals, not enrollment, child, or household facts.'])+'\n',encoding='utf-8')
    (LOGS/'v5_1_scoring_integration_status.json').write_text(json.dumps({'schools':len(schools),'competitors':len(comps),'streets':len(streets.get('features',[])),'buildings':len(buildings.get('features',[]))},indent=2),encoding='utf-8')
    print('scoring integrated')
if __name__=='__main__': main()
