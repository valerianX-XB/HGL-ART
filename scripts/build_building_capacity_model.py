#!/usr/bin/env python3
import csv, json, math, time, urllib.parse, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'public/data'; DOCS=ROOT/'docs'; LOGS=ROOT/'logs'; PROC=ROOT/'processed_data'
TARGET_ZIPS={'10011','10010','10003','10014','10012','10013'}
TODAY='2026-06-11'

def load_json(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def write_json(p,obj):
    Path(p).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

def fetch_json(url, retries=3):
    for i in range(retries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Hermes-HGL-v4-public-data-build/1.0'})
            with urllib.request.urlopen(req,timeout=90) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            if i==retries-1: raise
            time.sleep(1+i)

def socrata(resource, where=None, select=None, limit=50000):
    out=[]; offset=0
    while True:
        params={'$limit':str(limit),'$offset':str(offset)}
        if where: params['$where']=where
        if select: params['$select']=select
        url=f'https://data.cityofnewyork.us/resource/{resource}.json?'+urllib.parse.urlencode(params)
        rows=fetch_json(url)
        out.extend(rows)
        if len(rows)<limit: break
        offset+=limit
    return out

def bounds_of_geojson(gj):
    xs=[]; ys=[]
    def walk(c):
        if isinstance(c,(list,tuple)) and len(c)>=2 and isinstance(c[0],(int,float)) and isinstance(c[1],(int,float)):
            xs.append(float(c[0])); ys.append(float(c[1]))
        elif isinstance(c,(list,tuple)):
            for x in c: walk(x)
    for f in gj.get('features',[]): walk(f.get('geometry',{}).get('coordinates',[]))
    return min(xs),min(ys),max(xs),max(ys)

def centroid(coords):
    pts=[]
    def walk(c):
        if isinstance(c,(list,tuple)) and len(c)>=2 and isinstance(c[0],(int,float)) and isinstance(c[1],(int,float)):
            pts.append((float(c[0]),float(c[1])))
        elif isinstance(c,(list,tuple)):
            for x in c: walk(x)
    walk(coords)
    if not pts: return [None,None]
    return [sum(x for x,y in pts)/len(pts), sum(y for x,y in pts)/len(pts)]

def norm_bbl(v):
    if v is None: return None
    s=str(v).strip()
    if not s: return None
    if '.' in s: s=s.split('.')[0]
    return s.zfill(10) if s.isdigit() else s

def num(v, default=0.0):
    try:
        if v in (None,''): return default
        return float(v)
    except Exception: return default

def landuse_label(code):
    m={'1':'Residential one/two family','2':'Residential multi-family walk-up','3':'Residential multi-family elevator','4':'Mixed residential/commercial','5':'Commercial/office','6':'Industrial/manufacturing','7':'Transportation/utility','8':'Public facility/institution','9':'Open space/outdoor recreation','10':'Parking','11':'Vacant land'}
    return m.get(str(code).strip(), str(code or 'Unknown'))

def classify(p):
    units_res=int(round(num(p.get('unitsres'),0)))
    com=num(p.get('comarea'))+num(p.get('officearea'))+num(p.get('retailarea'))
    lu=str(p.get('landuse') or '').strip()
    bc=str(p.get('bldgclass') or '').strip().upper()
    res_bc=bc[:1] in set('ABC DRS') or bc.startswith(('C','D','R','S'))
    # Hotels are commercial even with transient units.
    nonres_bc=bc[:1] in set('E F G H I J K L M N O P Q T U V W Y Z'.split())
    if units_res>0 and (com>0 or lu=='4' or bc.startswith('S')):
        return 'Mixed-use', True, False
    if units_res>0 or lu in {'1','2','3'} or res_bc:
        return 'Residential', False, False
    if lu in {'5','6','7','8','9','10','11'} or nonres_bc or units_res==0:
        return landuse_label(lu) if lu else 'Non-residential', False, True
    return 'Unknown', False, False

def score(vals):
    # Stable, transparent 0-10 score from capacity, under-5 proxy, income, mixed-use/visibility.
    cap=math.log1p(max(0,vals['residential_capacity_units']))/math.log1p(250)
    u5=min(1, vals['under5_capacity_signal']/8.0)
    inc=min(1, max(0, vals.get('income_signal',0)-80000)/170000)
    mixed=0.08 if vals.get('mixed_use_flag') else 0
    if vals.get('non_residential_flag'): return 0.0
    return round(max(0,min(10,(0.45*cap+0.25*u5+0.22*inc+mixed)*10)),2)

def main():
    DOCS.mkdir(exist_ok=True); LOGS.mkdir(exist_ok=True); PROC.mkdir(exist_ok=True)
    zips=load_json(DATA/'hgl_zip_market_enriched.geojson')
    west,south,east,north=bounds_of_geojson(zips)
    # Approx 0.5 mile buffer in Manhattan lat/lon.
    west-=0.011; east+=0.011; south-=0.0073; north+=0.0073
    where=f"latitude between {south} and {north} and longitude between {west} and {east}"
    fields='bbl,zipcode,address,landuse,bldgclass,unitsres,unitstotal,resarea,comarea,officearea,retailarea,numfloors,yearbuilt,lotarea,bldgarea,assesstot,latitude,longitude'
    pluto=socrata('64uk-42ks',where=where,select=fields,limit=50000)
    pluto_by_bbl={norm_bbl(r.get('bbl')):r for r in pluto if norm_bbl(r.get('bbl'))}
    pluto_target=[r for r in pluto if str(r.get('zipcode')) in TARGET_ZIPS]
    target_bbls={norm_bbl(r.get('bbl')) for r in pluto_target if norm_bbl(r.get('bbl'))}
    # Pull building footprints in the buffered bbox and retain those joined to target ZIPs; retain unmatched in bbox as unknown buffer context.
    where_fp=f"within_box(the_geom, {north}, {west}, {south}, {east})"
    fps=socrata('5zhs-2jue',where=where_fp,limit=50000)
    features_visual=[]; features_capacity=[]
    by_zip=defaultdict(lambda:Counter())
    zip_proxy={}
    for f in zips['features']:
        p=f['properties']; hh=max(1,num(p.get('households'),1)); zip_proxy[str(p.get('zipcode'))]={
            'under5_per_hh': num(p.get('under5'),0)/hh,
            'income': num(p.get('median_household_income'),0),
            'zip_score': num(p.get('hgl_opportunity_score'),0)
        }
    used_bbl=set(); unmatched=0
    for fp in fps:
        bbl=norm_bbl(fp.get('base_bbl'))
        p=pluto_by_bbl.get(bbl,{})
        zipc=str(p.get('zipcode') or '')
        if bbl not in target_bbls and zipc not in TARGET_ZIPS:
            continue
        used_bbl.add(bbl)
        zprox=zip_proxy.get(zipc, {'under5_per_hh':0.04,'income':0,'zip_score':0})
        use_type,mixed,nonres=classify(p)
        units_res=int(round(num(p.get('unitsres'),0)))
        resarea=num(p.get('resarea'),0); bldgarea=num(p.get('bldgarea'),0); floors=num(p.get('numfloors'),0)
        if nonres:
            cap_units=0; confidence='None'; method='PLUTO/MapPLUTO or land-use classifies this as non-residential; residential capacity set to 0.'
        elif units_res>0:
            cap_units=units_res; confidence='High'; method='PLUTO/MapPLUTO UnitsRes available; capacity equals residential units, not occupied residents.'
        elif resarea>0:
            cap_units=max(1,round(resarea/850)); confidence='Medium'; method='Residential use detected; capacity estimated from PLUTO ResArea / average unit size.'
        elif bldgarea>0 and use_type in ('Residential','Mixed-use'):
            cap_units=max(1,round((bldgarea*0.75)/850)); confidence='Low'; method='Residential use inferred; capacity estimated from building area fallback.'
        else:
            cap_units=0; confidence='None'; method='No residential capacity detected.'
        under5=round(cap_units*zprox['under5_per_hh'],3)
        preschool=under5
        height=num(fp.get('height_roof'),0) or (floors*3.2 if floors else 12)
        c=centroid(fp['the_geom']['coordinates'])
        base={
            'bin': fp.get('bin') or p.get('bin'), 'bbl': bbl, 'address_or_label': p.get('address') or f"Building {fp.get('bin') or bbl or fp.get('objectid')}",
            'zipcode': zipc or 'buffer/unknown', 'building_height_m': round(height,2), 'roof_height': num(fp.get('height_roof'),None), 'ground_elevation': num(fp.get('ground_elevation'),None),
            'num_floors': floors, 'land_use': landuse_label(p.get('landuse')), 'building_class': p.get('bldgclass') or 'Unknown',
            'units_res': units_res, 'units_total': int(round(num(p.get('unitstotal'),0))), 'residential_units': units_res,
            'residential_capacity_units': cap_units, 'total_units': int(round(num(p.get('unitstotal'),0))), 'residential_floor_area': round(resarea,1),
            'estimated_household_capacity': cap_units, 'under5_capacity_signal': under5, 'preschool_age_capacity_signal': preschool,
            'residential_use_type': use_type, 'mixed_use_flag': bool(mixed), 'non_residential_flag': bool(nonres),
            'com_area': num(p.get('comarea'),0), 'office_area': num(p.get('officearea'),0), 'retail_area': num(p.get('retailarea'),0),
            'year_built': int(round(num(p.get('yearbuilt'),0))) or None, 'lot_area': num(p.get('lotarea'),0), 'bldg_area': bldgarea, 'assess_tot': num(p.get('assesstot'),0),
            'income_signal': zprox['income'], 'estimated_income_signal': zprox['income'], 'centroid': c,
            'capacity_model_confidence': confidence, 'confidence_level': confidence, 'capacity_model_method': method, 'estimate_method': method,
            'source_name':'NYC Building Footprints + NYC PLUTO/MapPLUTO via Socrata', 'source_retrieved': TODAY,
            'caveat':'Residential capacity is modeled from public property/building data. It is not actual residents, children, households, or families.'
        }
        base['hgl_building_opportunity_score']=score(base); base['hgl_opportunity_score']=base['hgl_building_opportunity_score']
        # Secondary deprecated fields retained only for backward compatibility; not displayed as primary UI.
        base['estimated_residents_modeled_secondary']=None if nonres else round(cap_units*1.8,2)
        base['estimated_residents']=base['estimated_residents_modeled_secondary']
        base['estimated_under5']=under5; base['estimated_under5_signal']=under5; base['estimated_households']=cap_units
        geom=fp['the_geom']
        features_visual.append({'type':'Feature','geometry':geom,'properties':{**base,'visual_layer':'Full 3D Building Massing','visual_color':'neutral_gray'}})
        if not nonres and cap_units>0:
            features_capacity.append({'type':'Feature','geometry':geom,'properties':{**base,'visual_layer':'Residential Capacity / Market Signal Overlay'}})
        zkey=zipc if zipc in TARGET_ZIPS else 'buffer/unknown'
        by_zip[zkey]['visual_3d_buildings']+=1
        if not nonres and cap_units>0: by_zip[zkey]['residential_capacity_buildings']+=1
        elif nonres: by_zip[zkey]['commercial_non_residential_buildings']+=1
        else: by_zip[zkey]['unmatched_unknown_use_buildings']+=1
    # Add PLUTO target lots with no footprint as point-buffer skipped from GeoJSON; count unmatched for coverage documentation.
    for r in pluto_target:
        b=norm_bbl(r.get('bbl'))
        if b not in used_bbl:
            by_zip[str(r.get('zipcode'))]['unmatched_unknown_use_buildings']+=1; unmatched+=1
    visual={'type':'FeatureCollection','name':'buildings_visual_all_v4','features':features_visual}
    capgj={'type':'FeatureCollection','name':'buildings_residential_capacity_v4','features':features_capacity}
    write_json(DATA/'buildings_visual_all.geojson',visual)
    write_json(DATA/'buildings_residential_capacity.geojson',capgj)
    write_json(DATA/'buildings_visual_3d.geojson',visual)
    write_json(DATA/'buildings_enriched.geojson',capgj)
    # CSV capacity extract.
    keys=['bbl','bin','address_or_label','zipcode','residential_use_type','land_use','building_class','residential_units','residential_capacity_units','total_units','residential_floor_area','estimated_household_capacity','under5_capacity_signal','preschool_age_capacity_signal','hgl_building_opportunity_score','capacity_model_confidence','capacity_model_method','non_residential_flag','mixed_use_flag']
    with (PROC/'buildings_residential_capacity_v4.csv').open('w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=keys); w.writeheader()
        for ft in features_visual: w.writerow({k:ft['properties'].get(k) for k in keys})
    # Coverage docs.
    rows=[]
    for z in sorted(TARGET_ZIPS):
        c=by_zip[z]
        total=c['visual_3d_buildings']+c['unmatched_unknown_use_buildings']
        rows.append((z,total,c['visual_3d_buildings'],c['residential_capacity_buildings'],c['commercial_non_residential_buildings'],c['unmatched_unknown_use_buildings']))
    md=['# Building Layer Coverage v4','', 'Sources: NYC Building Footprints (5zhs-2jue) joined to NYC PLUTO/MapPLUTO (64uk-42ks) by BBL where available. Coverage pulled for the six target ZIPs with an approximate 0.5-mile bbox buffer. Confidence is highest where PLUTO UnitsRes and land-use/class are available.', '', '| ZIP | total buildings/lots checked | visual 3D buildings | residential-capacity buildings | commercial / non-residential | unmatched / unknown-use |', '|---|---:|---:|---:|---:|---:|']
    for r in rows: md.append('| {} | {} | {} | {} | {} | {} |'.format(*r))
    md += ['', f'- Full visual 3D building features: {len(features_visual)}', f'- Residential capacity overlay features: {len(features_capacity)}', f'- PLUTO target lots without joined footprint in pulled footprint set: {unmatched}', '- Non-residential buildings remain in the all-building massing layer but have residential capacity, household capacity, and under-5 capacity signal set to 0.', '- All capacity values are public-data modeled signals, not actual residents or children.']
    (DOCS/'building_layer_coverage_v4.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    model=['# Building Capacity Model v4','', 'This model replaces primary building-level “estimated residents” logic with residential capacity signals.', '', 'Rules:', '- If PLUTO UnitsRes is present, residential_capacity_units = UnitsRes.', '- If UnitsRes is missing but residential use is clear, capacity is estimated from ResArea or BldgArea using an average unit-size fallback.', '- If land use / building class indicates non-residential, residential capacity, estimated household capacity, and under-5 capacity signal are 0.', '- estimated_household_capacity equals residential capacity units; it is not observed occupancy.', '- under5_capacity_signal = residential_capacity_units × local aggregate under-5 per household proxy.', '', 'Confidence:', '- High: UnitsRes available and use clear.', '- Medium: residential use clear but units estimated from ResArea/BldgArea.', '- Low: weak inferred residential use.', '- None: non-residential or no residential capacity detected.', '', 'Tooltip caveat: Under-5 capacity signal is modeled from residential unit capacity and aggregate census age patterns. It is not actual children living in this building. 5岁以下儿童潜力信号基于住宅单元承载能力和聚合人口年龄结构建模，不代表该建筑内真实儿童人数。']
    (DOCS/'building_capacity_model_v4.md').write_text('\n'.join(model)+'\n',encoding='utf-8')
    # Duplicate audit.
    props=[ft['properties'] for ft in features_visual]
    audit=['# Repeated Building Value Audit v4','']
    for k in ['residential_units','under5_capacity_signal','hgl_building_opportunity_score']:
        counts=Counter(p.get(k) for p in props)
        top=counts.most_common(10)
        audit.append(f'## Duplicate counts for {k}')
        for v,cnt in top: audit.append(f'- {v}: {cnt}')
        audit.append('')
    nonres_bad=sum(1 for p in props if p.get('non_residential_flag') and (p.get('residential_capacity_units') or p.get('under5_capacity_signal') or p.get('estimated_household_capacity')))
    audit += ['## Findings', f'- Non-residential buildings with non-zero residential capacity fields: {nonres_bad}', '- Repeated zero values are legitimate for non-residential buildings.', '- Repeated one-unit values are expected for one-/two-family or small residential buildings.', '- Scores are derived from building-level UnitsRes/capacity and use classification plus local aggregate income/age proxies; ZIP-level values are no longer directly copied as building residents.', '- Commercial/office/public/institutional/parking/industrial classes are set to zero residential capacity.']
    (DOCS/'repeated_building_value_audit.md').write_text('\n'.join(audit)+'\n',encoding='utf-8')
    status={'pluto_rows_bbox':len(pluto),'pluto_target_rows':len(pluto_target),'footprints_bbox':len(fps),'visual_features':len(features_visual),'capacity_features':len(features_capacity),'unmatched_pluto_target_lots':unmatched,'by_zip':{z:dict(by_zip[z]) for z in sorted(TARGET_ZIPS)}}
    (LOGS/'v4_building_capacity_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))
if __name__=='__main__': main()
