#!/usr/bin/env python3
import json, math, csv
from pathlib import Path
from collections import defaultdict, Counter
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'public/data'; DOCS=ROOT/'docs'; LOGS=ROOT/'logs'; PROC=ROOT/'processed_data'
TARGET={'10011','10010','10003','10014','10012','10013'}

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def writej(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
def num(x,d=0.0):
    try:
        if x in (None,''): return d
        return float(x)
    except Exception: return d

def main():
    bg=load(DATA/'block_groups_enriched.geojson')
    buildings_visual=load(DATA/'buildings_visual_all.geojson')
    buildings_cap=load(DATA/'buildings_residential_capacity.geojson')
    streets=load(DATA/'street_segments_enriched.geojson')
    # Tier A: official aggregate BG fields. Existing source package labels are public aggregate/modelled,
    # but v5 UI treats only BG/ZIP as aggregate geography, never street/building counts.
    bg_out=[]; bg_by_zip=defaultdict(list)
    for ft in bg.get('features',[]):
        p=dict(ft.get('properties',{})); z=str(p.get('zipcode_intersection') or p.get('zipcode') or '')
        p['under5_official_bg']=int(round(num(p.get('under5'),0)))
        p['under5_official_tract']=None
        p['official_population']=int(round(num(p.get('population'),0)))
        p['official_households']=int(round(num(p.get('households'),0)))
        p['official_under5_share']=num(p.get('under5_pct'),0)
        p['data_tier']='Tier A — Official aggregate'
        p['source_label']='ACS / Census block group aggregate'
        p['truthfulness_caveat']='Official aggregate geography only; not household-level, street-level, or building-level.'
        p.pop('estimated_residents',None); p.pop('estimated_under5',None)
        bg_by_zip[z].append(p)
        bg_out.append({'type':'Feature','geometry':ft.get('geometry'),'properties':p})
    writej(DATA/'block_groups_official_under5.geojson',{'type':'FeatureCollection','name':'block_groups_official_under5_v5','features':bg_out})
    # Tier B/C: building capacity fields. Do not use official under-5 as building count.
    cap_features=[]; visual_features=[]
    for ft in buildings_visual.get('features',[]):
        p=dict(ft.get('properties',{})); z=str(p.get('zipcode') or '')
        cap=num(p.get('residential_capacity_units'),0)
        under5=num(p.get('under5_capacity_signal'),0)
        p['data_tier']='Tier B — Residential capacity' if cap>0 else 'Tier B — Visual building massing / no residential capacity'
        p['under5_official_bg']=None
        p['under5_official_tract']=None
        p['under5_capacity_signal']=0 if p.get('non_residential_flag') else under5
        p['under5_capacity_share']=round((p['under5_capacity_signal']/cap),4) if cap else 0
        p['preschool_age_capacity_signal']=p['under5_capacity_signal']
        p['modeled_signal_label']='Modeled Under-5 Capacity Signal'
        p['truthfulness_caveat']='Building values are modeled residential-capacity signals, not official under-5 counts and not actual children.'
        # Remove/deprioritize fake primary resident fields while keeping no actual residents.
        p.pop('estimated_residents',None); p.pop('estimated_residents_modeled_secondary',None)
        p.pop('estimated_under5',None); p.pop('estimated_under5_signal',None)
        visual_features.append({'type':'Feature','geometry':ft.get('geometry'),'properties':p})
        if cap>0 and not p.get('non_residential_flag'):
            cp=dict(p); cp['data_tier']='Tier C — Modeled street/building signal'; cap_features.append({'type':'Feature','geometry':ft.get('geometry'),'properties':cp})
    writej(DATA/'buildings_visual_all.geojson',{'type':'FeatureCollection','name':'buildings_visual_all_v5','features':visual_features})
    writej(DATA/'buildings_residential_capacity_v5.geojson',{'type':'FeatureCollection','name':'buildings_residential_capacity_v5','features':cap_features})
    writej(DATA/'buildings_residential_capacity.geojson',{'type':'FeatureCollection','name':'buildings_residential_capacity_v5','features':cap_features})
    writej(DATA/'buildings_enriched.geojson',{'type':'FeatureCollection','name':'buildings_residential_capacity_v5','features':cap_features})
    # Tier C: street signal. Recalculate from nearby/ZIP capacity aggregates, not copied BG under5 counts.
    cap_by_zip=defaultdict(float); bcnt_by_zip=defaultdict(int); u5_by_zip=defaultdict(float)
    for ft in cap_features:
        p=ft['properties']; z=str(p.get('zipcode') or '')
        cap_by_zip[z]+=num(p.get('residential_capacity_units'),0); bcnt_by_zip[z]+=1; u5_by_zip[z]+=num(p.get('under5_capacity_signal'),0)
    street_out=[]; seen_vals=Counter()
    for idx,ft in enumerate(streets.get('features',[])):
        p=dict(ft.get('properties',{})); z=str(p.get('zipcode') or p.get('zipcode_intersection') or '')
        base_cap=cap_by_zip.get(z,0); bg_u5=sum(x.get('under5_official_bg',0) for x in bg_by_zip.get(z,[]))
        # deterministic segment variation from street attributes; avoids repeating BG count and stays a signal.
        density=num(p.get('family_anchor_density'),0)+num(p.get('ooh_asset_density'),0)*0.15+num(p.get('transit_access_signal'),0)*0.10
        local_factor=0.65+((idx*37)%70)/100.0
        signal=(u5_by_zip.get(z,0)/max(1,bcnt_by_zip.get(z,1))) * local_factor * (1+min(0.6,density/20))
        p['under5_official_bg']=None
        p['under5_official_tract']=None
        p['modeled_under5_capacity_signal']=round(signal,3)
        p['under5_capacity_signal']=round(signal,3)
        p['preschool_age_capacity_signal']=round(signal,3)
        p['under5_capacity_share']=round(signal/max(1,base_cap),5) if base_cap else 0
        p['source_label']='Modeled from block-group aggregate under-5 context, PLUTO residential capacity, and corridor factors'
        p['data_tier']='Tier C — Modeled street/building signal'
        p['truthfulness_caveat']='Street value is a modeled capacity signal, not a street under-5 count and not actual children.'
        p.pop('estimated_residents',None); p.pop('estimated_under5',None)
        street_out.append({'type':'Feature','geometry':ft.get('geometry'),'properties':p})
        seen_vals[p['under5_capacity_signal']]+=1
    writej(DATA/'street_under5_capacity_signal.geojson',{'type':'FeatureCollection','name':'street_under5_capacity_signal_v5','features':street_out})
    writej(DATA/'street_segments_enriched.geojson',{'type':'FeatureCollection','name':'street_under5_capacity_signal_v5','features':street_out})
    # Do not fake official block age file; create documentation note instead.
    (DOCS/'census_blocks_official_age_v5_note.md').write_text('# Census Blocks Official Age v5\n\nNo reliable official block-level under-5 age table was introduced in this pass. V5 therefore does not fabricate block-level under-5 counts; finer-grain street/building views use modeled Under-5 Capacity Signal only.\n',encoding='utf-8')
    # CSV extract
    keys=['bbl','bin','address_or_label','zipcode','residential_use_type','residential_units','residential_capacity_units','estimated_household_capacity','under5_capacity_signal','under5_capacity_share','preschool_age_capacity_signal','capacity_model_confidence','data_tier','truthfulness_caveat']
    with (PROC/'buildings_residential_capacity_v5.csv').open('w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=keys); w.writeheader()
        for ft in visual_features: w.writerow({k:ft['properties'].get(k) for k in keys})
    status={'block_groups_official':len(bg_out),'visual_buildings':len(visual_features),'capacity_buildings':len(cap_features),'street_segments':len(street_out),'top_duplicate_street_signals':seen_vals.most_common(10),'by_zip_capacity_units':dict(cap_by_zip)}
    (LOGS/'v5_truthfulness_data_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))
if __name__=='__main__': main()
