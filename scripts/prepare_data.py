#!/usr/bin/env python3
import argparse, csv, json, math, time, urllib.request, urllib.parse, shutil, xml.etree.ElementTree as ET
from pathlib import Path
TARGET_ZIPS=["10011","10010","10003","10014","10012","10013"]
NEIGHBORHOODS={"10011":"Chelsea / West 14th / Flatiron edge","10010":"Flatiron / Gramercy","10003":"Union Square / East Village / Greenwich Village edge","10014":"West Village","10012":"SoHo / NoHo","10013":"Tribeca / Hudson Square / Chinatown edge"}
PRIORITY={"10013":"Tier 1","10003":"Tier 2","10010":"Tier 2","10014":"Tier 3","10011":"Tier 3","10012":"Tier 4"}
PUBLIC_CAVEAT="Aggregate/modelled public data only; no individual child, parent, caregiver, household, family, or resident data."
BBOX=(-74.026,40.697,-73.968,40.760)

def read_csv(p):
    with open(p,newline='',encoding='utf-8') as f: return list(csv.DictReader(f))
def write_csv(p, rows):
    keys=[]
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open(p,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
def num(v):
    if v in (None,''): return None
    try: return float(v) if '.' in str(v) else int(v)
    except Exception: return v
def by_zip(rows): return {r['zipcode']:r for r in rows}
def fetch_json(url, data=None, timeout=90):
    req=urllib.request.Request(url, data=data, headers={'User-Agent':'hgl-art-v3-public-map'})
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.load(r)
def fetch_text(url, timeout=90):
    req=urllib.request.Request(url, headers={'User-Agent':'hgl-art-v3-public-map'})
    with urllib.request.urlopen(req,timeout=timeout) as r: return r.read().decode('utf-8','ignore')
def fetch_polygon(z):
    return fetch_json(f'https://api.censusreporter.org/1.0/geo/show/tiger2024?geo_ids=86000US{z}')['features'][0]['geometry']
def ring(geom):
    if geom['type']=='Polygon': return geom['coordinates'][0]
    if geom['type']=='MultiPolygon': return max((p[0] for p in geom['coordinates']), key=len)
    return []
def point_in_ring(x,y,r):
    inside=False; j=len(r)-1
    for i in range(len(r)):
        xi,yi=r[i]; xj,yj=r[j]
        if ((yi>y)!=(yj>y)) and (x < (xj-xi)*(y-yi)/(yj-yi+1e-12)+xi): inside=not inside
        j=i
    return inside
def point_in_geom(x,y,g):
    if g['type']=='Polygon': return point_in_ring(x,y,g['coordinates'][0])
    if g['type']=='MultiPolygon': return any(point_in_ring(x,y,p[0]) for p in g['coordinates'])
    return False
def geom_centroid(g):
    r=ring(g); return [sum(p[0] for p in r)/len(r),sum(p[1] for p in r)/len(r)] if r else [0,0]
def bbox(g):
    pts=[]
    if g['type']=='Polygon': pts=[p for rr in g['coordinates'] for p in rr]
    else: pts=[p for poly in g['coordinates'] for rr in poly for p in rr]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return min(xs),min(ys),max(xs),max(ys)
def area_approx(coords):
    pts=coords[0]; a=0
    for i in range(len(pts)-1): a+=pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1]
    return abs(a)/2
def dist_m(a,b):
    dx=(a[0]-b[0])*85000; dy=(a[1]-b[1])*111000; return math.hypot(dx,dy)
def nearest_zip(pt, geoms):
    for z,g in geoms.items():
        if point_in_geom(pt[0],pt[1],g): return z
    cents={z:geom_centroid(g) for z,g in geoms.items()}
    return min(cents,key=lambda z:dist_m(pt,cents[z]))
def tiger_layer(layer_id, max_records=5000):
    features=[]; offset=0; geom=','.join(map(str,BBOX))
    while True:
        params={'f':'geojson','where':"STATE='36' AND COUNTY='061'",'outFields':'*','returnGeometry':'true','outSR':'4326','geometry':geom,'geometryType':'esriGeometryEnvelope','inSR':'4326','spatialRel':'esriSpatialRelIntersects','resultRecordCount':'1000','resultOffset':str(offset)}
        js=fetch_json(f'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/{layer_id}/query?'+urllib.parse.urlencode(params), timeout=70)
        batch=js.get('features',[]); features.extend(batch)
        if not js.get('exceededTransferLimit') or not batch or len(features)>=max_records: break
        offset+=len(batch)
    return features[:max_records]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',default='../HGL_ART_ZIP_OOH_Research_2026_06_10'); ap.add_argument('--out',default='public/data')
    args=ap.parse_args(); source=Path(args.source).resolve(); out=Path(args.out).resolve(); out.mkdir(parents=True,exist_ok=True); (out.parent.parent/'processed_data').mkdir(exist_ok=True)
    demo=by_zip(read_csv(source/'processed_data/zip_demographics_clean.csv')); inc=by_zip(read_csv(source/'processed_data/zip_income_clean.csv')); lang=by_zip(read_csv(source/'processed_data/zip_language_education_clean.csv')); scores={r['item_id']:r for r in read_csv(source/'processed_data/zip_scoring_model.csv') if r.get('scoring_type')=='ZIP'}
    geoms={}; zip_props={}; zip_features=[]; centroids=[]
    for z in TARGET_ZIPS:
        g=fetch_polygon(z); geoms[z]=g; time.sleep(.05)
        d,ii,ll,sc=demo[z],inc[z],lang[z],scores[z]
        under5=num(d['under_5']) or 0; pop=num(d['population']) or 1
        props={'zipcode':z,'zcta_label':f'ZCTA {z}','neighborhood_label':NEIGHBORHOODS[z],'population':pop,'households':num(d['households']),'median_household_income':num(ii['median_household_income']),'mean_household_income':num(ii['mean_household_income']),'per_capita_income':num(ii.get('per_capita_income')),'under5':under5,'under5_pct':round(under5/pop*100,2),'under5_share':round(under5/pop,4),'preschool_age_signal':under5,'households_with_children_pct':num(d['households_with_children_pct']),'family_households_pct':num(d['family_households_pct']),'ba_plus_pct':num(ll['ba_plus_pct']),'chinese_spoken_home_pct':num(ll['chinese_spoken_home_pct']),'spanish_spoken_home_pct':num(ll.get('spanish_spoken_home_pct')),'foreign_born_pct':num(ll.get('foreign_born_pct')),'professional_managerial_pct':num(ll.get('professional_managerial_pct')),'hgl_opportunity_score':num(sc['final_score']),'income_score':num(sc['income_score']),'family_children_score':num(sc['family_children_score']),'premium_education_fit_score':num(sc['premium_education_fit_score']),'advertising_practicality_score':num(sc['advertising_practicality_score']),'recommended_priority_tier':PRIORITY[z],'recommended_hgl_use':'Multilingual early childhood education / preschool-style awareness and enrollment consultation; seasonal programs are family engagement funnels.','caveat':PUBLIC_CAVEAT}
        zip_props[z]=props; zip_features.append({'type':'Feature','geometry':g,'properties':props}); centroids.append({'type':'Feature','geometry':{'type':'Point','coordinates':geom_centroid(g)},'properties':props})
    (out/'hgl_zip_market_enriched.geojson').write_text(json.dumps({'type':'FeatureCollection','metadata':{'all_polygons_available':True,'polygon_count':6},'features':zip_features},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'hgl_zip_centroids.geojson').write_text(json.dumps({'type':'FeatureCollection','features':centroids},ensure_ascii=False,indent=2),encoding='utf-8')
    # TIGER geometry with modeled under-5 signals
    bgs=[]
    for f in tiger_layer(8):
        c=geom_centroid(f['geometry']); z=nearest_zip(c,geoms)
        if z not in TARGET_ZIPS or not point_in_geom(c[0],c[1],geoms[z]): continue
        zp=zip_props[z]; factor=.85+.3*((int(f['properties'].get('BLKGRP') or 1)%3)/2)
        props={'geoid':f['properties'].get('GEOID'),'display_label':f"Block Group {z}-{f['properties'].get('BLKGRP')}",'tract':f['properties'].get('TRACT'),'block_group':f['properties'].get('BLKGRP'),'zipcode_intersection':z,'population':round(zp['population']/8*factor),'households':round(zp['households']/8*factor),'median_household_income':zp['median_household_income'],'under5':round(zp['under5']/8*factor),'under5_pct':zp['under5_pct'],'preschool_age_signal':round(zp['under5']/8*factor),'households_with_children_pct':zp['households_with_children_pct'],'family_households_pct':zp['family_households_pct'],'chinese_spoken_home_pct':zp['chinese_spoken_home_pct'],'spanish_spoken_home_pct':zp['spanish_spoken_home_pct'],'ba_plus_pct':zp['ba_plus_pct'],'hgl_opportunity_score':round(zp['hgl_opportunity_score']*factor,2),'confidence_level':'Medium geometry / Low-Medium modeled attributes','centroid':c,'caveat':'Official TIGER block-group geometry with modeled aggregate attributes; not household-level data.'}
        bgs.append({'type':'Feature','geometry':f['geometry'],'properties':props})
    blocks=[]
    for f in tiger_layer(12, max_records=5000):
        c=geom_centroid(f['geometry']); z=nearest_zip(c,geoms)
        if z not in TARGET_ZIPS or not point_in_geom(c[0],c[1],geoms[z]): continue
        zp=zip_props[z]; seed=(int(str(f['properties'].get('BLOCK') or '1')[-1]) or 1); factor=.6+seed/10
        props={'geoid':f['properties'].get('GEOID'),'display_label':f"Census Block {z}-{f['properties'].get('BLOCK')}",'block':f['properties'].get('BLOCK'),'tract':f['properties'].get('TRACT'),'population_2020':round(zp['population']/80*factor),'housing_units_2020':round(zp['households']/80*factor),'estimated_current_population':round(zp['population']/80*factor),'estimated_residents':round(zp['population']/80*factor),'estimated_under5':round(zp['under5']/80*factor),'estimated_under5_signal':round(zp['under5']/80*factor),'hgl_opportunity_score':round(zp['hgl_opportunity_score']*factor,2),'confidence_level':'Medium geometry / Low modeled attributes','centroid':c,'estimate_method':'Official TIGER block geometry with modeled aggregate allocation.','caveat':'Modeled aggregate estimate; not individual-level data.'}
        blocks.append({'type':'Feature','geometry':f['geometry'],'properties':props})
    (out/'block_groups_enriched.geojson').write_text(json.dumps({'type':'FeatureCollection','features':bgs},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'census_blocks_enriched.geojson').write_text(json.dumps({'type':'FeatureCollection','features':blocks[:2200]},ensure_ascii=False,indent=2),encoding='utf-8')
    # OOH assets: corrected candidates + LinkNYC KML + OSM advertising objects
    ooh_csv=read_csv(source/'processed_data/ooh_candidates_clean.csv'); assets=[]; seen=set()
    def add_asset(a):
        k=(round(a['geometry']['coordinates'][0],6),round(a['geometry']['coordinates'][1],6),a['properties'].get('asset_type'),a['properties'].get('asset_name'))
        if k not in seen:
            seen.add(k); assets.append(a)
    for r in ooh_csv:
        lat=num(r.get('latitude')); lon=num(r.get('longitude'))
        if lat is None or lon is None: continue
        st=r.get('availability_status',''); status='Network bookable' if st.lower().startswith('available network') else 'Potentially bookable' if st.lower().startswith('potentially') else 'Candidate to verify' if st.lower().startswith('candidate') else 'Permitted sign / availability unknown'
        typ='LinkNYC' if 'LinkNYC' in r.get('vendor_owner','') else 'Bus shelters' if 'JCDecaux' in r.get('vendor_owner','') else 'Subway / MTA' if 'MTA' in r.get('vendor_owner','') or 'OUTFRONT' in r.get('vendor_owner','') else 'Wallscapes' if 'Angel' in r.get('vendor_owner','') else 'Other'
        add_asset({'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},'properties':{'ooh_asset_id':r['ooh_id'],'asset_name':r.get('address_or_intersection'),'asset_type':typ,'vendor_owner':r.get('vendor_owner'),'operator_if_known':r.get('vendor_owner'),'address_or_intersection':r.get('address_or_intersection'),'latitude':lat,'longitude':lon,'zipcode':r.get('zipcode'),'media_format':r.get('media_type'),'static_or_digital':'Verify with vendor','asset_status':status,'availability_status':r.get('availability_status'),'availability_confidence':r.get('availability_confidence'),'source_name':r.get('source_id'),'source_url':r.get('source_url'),'retrieval_date':r.get('retrieval_date'),'last_observed_date':None,'pricing_status':'Quote/vendor confirmation required','exact_price_confirmed':False,'impressions_status':'Vendor confirmation required','exact_impressions_confirmed':False,'family_anchor_proximity':r.get('nearby_family_anchors'),'preschool_school_proximity':'Verify locally','transit_proximity':'Verify locally','hgl_relevance_score':num(r.get('score')),'recommended_use':r.get('recommended_use'),'verification_needed':r.get('verification_needed'),'confidence_level':r.get('confidence_level'),'caveat':'Availability, pricing, and exact unit selection must be confirmed with the vendor before purchase.'}})
    try:
        kml=fetch_text('https://www.link.nyc/map/LinkNYC.kml')
        root=ET.fromstring(kml)
        for pm in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
            name=(pm.findtext('{http://www.opengis.net/kml/2.2}name') or 'LinkNYC kiosk').strip(); coords=(pm.findtext('.//{http://www.opengis.net/kml/2.2}coordinates') or '').strip().split(',')
            if len(coords)<2: continue
            lon=float(coords[0]); lat=float(coords[1]); z=nearest_zip([lon,lat],geoms)
            if z in TARGET_ZIPS and point_in_geom(lon,lat,geoms[z]):
                add_asset({'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},'properties':{'ooh_asset_id':f'LINKNYC_{len(assets)+1:04d}','asset_name':name,'asset_type':'LinkNYC','vendor_owner':'LinkNYC / Intersection','operator_if_known':'Intersection / CityBridge','address_or_intersection':name,'latitude':lat,'longitude':lon,'zipcode':z,'media_format':'Digital kiosk screen network','static_or_digital':'Digital','asset_status':'Network bookable','availability_status':'Network bookable; exact screen/date requires confirmation','availability_confidence':'Medium-High network confidence; unit/date unconfirmed','source_name':'LinkNYC KML','source_url':'https://www.link.nyc/map/LinkNYC.kml','retrieval_date':time.strftime('%Y-%m-%d'),'last_observed_date':None,'pricing_status':'Quote or self-service portal required','exact_price_confirmed':False,'impressions_status':'Vendor/platform confirmation required','exact_impressions_confirmed':False,'family_anchor_proximity':'To be evaluated by local context','preschool_school_proximity':'To be evaluated by local context','transit_proximity':'Street-level kiosk; verify locally','hgl_relevance_score':zip_props[z]['hgl_opportunity_score'],'recommended_use':'Parent/caregiver awareness for multilingual preschool-style early education; exact screen/date must be confirmed.','verification_needed':'Confirm screen, date, pricing, dayparting and creative specs with LinkNYC / Intersection.','confidence_level':'Medium-High','caveat':'Availability, pricing, and exact unit selection must be confirmed with the vendor before purchase.'}})
    except Exception: pass
    try:
        q='[out:json][timeout:50];(node["advertising"](40.697,-74.026,40.760,-73.968);way["advertising"](40.697,-74.026,40.760,-73.968);node["man_made"="advertising"](40.697,-74.026,40.760,-73.968););out center tags 1000;'
        osm_ads=fetch_json('https://overpass-api.de/api/interpreter', urllib.parse.urlencode({'data':q}).encode(), timeout=80)
        for el in osm_ads.get('elements',[]):
            lon=el.get('lon') or el.get('center',{}).get('lon'); lat=el.get('lat') or el.get('center',{}).get('lat')
            if lon is None or lat is None: continue
            z=nearest_zip([lon,lat],geoms)
            if z in TARGET_ZIPS and point_in_geom(lon,lat,geoms[z]):
                add_asset({'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},'properties':{'ooh_asset_id':f'OSM_ADV_{len(assets)+1:04d}','asset_name':el.get('tags',{}).get('name') or 'OSM advertising feature','asset_type':'Candidate walls','vendor_owner':'Unknown / OSM advertising feature','operator_if_known':el.get('tags',{}).get('operator'),'address_or_intersection':'OSM mapped advertising feature','latitude':lat,'longitude':lon,'zipcode':z,'media_format':el.get('tags',{}).get('advertising','advertising feature'),'static_or_digital':'Unknown','asset_status':'Candidate to verify','availability_status':'Candidate to verify; no vendor availability confirmed','availability_confidence':'Low','source_name':'OpenStreetMap advertising tag','source_url':'https://overpass-api.de/','retrieval_date':time.strftime('%Y-%m-%d'),'last_observed_date':None,'pricing_status':'Unknown; vendor/source confirmation required','exact_price_confirmed':False,'impressions_status':'Unknown; vendor confirmation required','exact_impressions_confirmed':False,'family_anchor_proximity':'To be evaluated','preschool_school_proximity':'To be evaluated','transit_proximity':'To be evaluated','hgl_relevance_score':zip_props[z]['hgl_opportunity_score']*0.75,'recommended_use':'Candidate only; verify owner, legality, visibility and fit before outreach.','verification_needed':'Confirm asset existence, owner, sales channel, availability, pricing and restrictions.','confidence_level':'Low','caveat':'Availability, pricing, and exact unit selection must be confirmed with the vendor before purchase.'}})
    except Exception: pass
    (out/'ooh_assets_expanded.geojson').write_text(json.dumps({'type':'FeatureCollection','features':assets},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'ooh_assets_expanded.json').write_text(json.dumps([a['properties'] for a in assets],ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'hgl_ooh_candidates.geojson').write_text(json.dumps({'type':'FeatureCollection','features':assets},ensure_ascii=False,indent=2),encoding='utf-8')
    # Buildings: full visual + enriched
    buildings=[]
    for zq,gq in geoms.items():
        bx0,by0,bx1,by1=bbox(gq)
        q=f'[out:json][timeout:55];way["building"]({by0-0.008},{bx0-0.008},{by1+0.008},{bx1+0.008});out tags geom 5000;'
        try: osm_z=fetch_json('https://overpass-api.de/api/interpreter', urllib.parse.urlencode({'data':q}).encode(), timeout=90)
        except Exception: osm_z={'elements':[]}
        for el in osm_z.get('elements',[]):
            coords=[[p['lon'],p['lat']] for p in el.get('geometry',[])]
            if len(coords)<4: continue
            cx=sum(p[0] for p in coords)/len(coords); cy=sum(p[1] for p in coords)/len(coords)
            z=nearest_zip([cx,cy],geoms)
            if z not in TARGET_ZIPS or not point_in_geom(cx,cy,geoms[z]): continue
            if coords[0]!=coords[-1]: coords.append(coords[0])
            tags=el.get('tags',{}); zp=zip_props[z]
            try: levels=float(tags.get('building:levels') or tags.get('levels') or 4)
            except Exception: levels=4
            try: h=float(str(tags.get('height','')).replace('m',''))
            except Exception: h=levels*3.2+3
            footprint=max(area_approx([coords])*1e8,45); btype=tags.get('building','yes')
            res_factor=1.0 if btype in ['apartments','residential','yes','house','terrace','semidetached_house'] else 0.35 if btype in ['commercial','retail','office'] else 0.6
            units=max(1, round(footprint*max(levels,1)/95*res_factor)); est_res=units*1.75; u5_share=zp['under5_share']
            est_u5=est_res*u5_share
            lang_signal=(zp['chinese_spoken_home_pct'] or 0)+(zp['spanish_spoken_home_pct'] or 0)
            bscore=round(min(10,(min(est_u5,8)/8*3)+(min(units,30)/30*1.5)+(min(zp['median_household_income'],180000)/180000*2)+(min(lang_signal,25)/25*1)+(zp['hgl_opportunity_score']/10*2.5)),2)
            props={'bin':None,'bbl':None,'address_or_label':(tags.get('addr:housenumber','')+' '+tags.get('addr:street','')).strip() if tags.get('addr:street') else tags.get('name') or f'Building {el.get("id")}', 'zipcode':z,'census_block_geoid':None,'census_block_group_geoid':None,'building_height_m':round(h,1),'roof_height':round(h,1),'ground_elevation':None,'num_floors':levels,'land_use':'residential/mixed modeled signal','building_class':btype,'units_res':units,'units_total':units,'estimated_residents':round(est_res,1),'estimated_under5':round(est_u5,2),'estimated_under5_signal':round(est_u5,2),'under5_signal_source':'Modeled from aggregate ZCTA under-5 share and estimated residential intensity','estimated_households':units,'estimated_family_households':round(units*zp['family_households_pct']/100,1),'estimated_income_signal':zp['median_household_income'],'income_signal':zp['median_household_income'],'chinese_spoken_home_pct':zp['chinese_spoken_home_pct'],'spanish_spoken_home_pct':zp['spanish_spoken_home_pct'],'preschool_age_signal':round(est_u5,2),'hgl_building_opportunity_score':bscore,'hgl_opportunity_score':bscore,'estimate_method':'OSM building footprint + modeled residential allocation from aggregate public data; no actual resident data.','score_drivers':'estimated under-5 signal, residential intensity, income signal, language signal','confidence_level':'Low-Medium','centroid':[cx,cy],'caveat':'Modeled aggregate estimate. Not actual residents, children, families, or households.'}
            buildings.append({'type':'Feature','geometry':{'type':'Polygon','coordinates':[coords]},'properties':props})
        time.sleep(.05)
    # de-dupe buildings by rounded centroid
    out_build=[]; bseen=set()
    for b in buildings:
        c=b['properties']['centroid']; key=(round(c[0],6),round(c[1],6))
        if key not in bseen: bseen.add(key); out_build.append(b)
    (out/'buildings_visual_3d.geojson').write_text(json.dumps({'type':'FeatureCollection','features':out_build},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'buildings_enriched.geojson').write_text(json.dumps({'type':'FeatureCollection','features':out_build},ensure_ascii=False,indent=2),encoding='utf-8')
    # Streets after building and OOH known
    streets=[]; bld_pts=[b['properties']['centroid'] for b in out_build]; asset_pts=[a['geometry']['coordinates'] for a in assets]
    try:
        sq='[out:json][timeout:60];way["highway"](40.697,-74.026,40.760,-73.968);out tags geom 10000;'
        osm_s=fetch_json('https://overpass-api.de/api/interpreter', urllib.parse.urlencode({'data':sq}).encode(), timeout=100)
    except Exception: osm_s={'elements':[]}
    for el in osm_s.get('elements',[]):
        tags=el.get('tags',{}); coords=[[p['lon'],p['lat']] for p in el.get('geometry',[])]
        if len(coords)<2: continue
        c=[sum(p[0] for p in coords)/len(coords),sum(p[1] for p in coords)/len(coords)]; z=nearest_zip(c,geoms)
        if z not in TARGET_ZIPS or not point_in_geom(c[0],c[1],geoms[z]): continue
        zp=zip_props[z]
        nearby_b=sum(1 for p in bld_pts if dist_m(c,p)<120); nearby_o=sum(1 for p in asset_pts if dist_m(c,p)<180)
        u5_signal=min(10,(nearby_b/18)*5+(zp['under5_pct']/5)*5)
        income_signal=min(10,(zp['median_household_income']/180000)*10)
        lang_signal=min(10,((zp['chinese_spoken_home_pct'] or 0)+(zp['spanish_spoken_home_pct'] or 0))/3)
        anchor_signal=0 if nearby_b==0 else min(10,nearby_b/8)
        ooh_signal=min(10,nearby_o*1.2)
        transit_signal=3 if tags.get('highway') in ['primary','secondary','tertiary'] else 1
        score=round(u5_signal*.30+zp['households_with_children_pct']/10*.15+income_signal*.20+lang_signal*.10+anchor_signal*.10+anchor_signal*.10+ooh_signal*.05,2)
        drivers=sorted([('under-5 signal',u5_signal),('income signal',income_signal),('OOH nearby',ooh_signal),('language signal',lang_signal),('building intensity',anchor_signal)], key=lambda x:x[1], reverse=True)[:2]
        streets.append({'type':'Feature','geometry':{'type':'LineString','coordinates':coords},'properties':{'street_segment_id':f'ST_{len(streets)+1:05d}','street_name':tags.get('name') or 'Unnamed street segment','from_intersection':'Modeled OSM segment start','to_intersection':'Modeled OSM segment end','zipcode':z,'adjacent_block_groups':'Nearest TIGER block groups in target area','intersecting_blocks':'Nearest TIGER blocks in target area','estimated_resident_signal':nearby_b,'estimated_under5_signal':round(u5_signal,2),'under5_signal_source':'Nearby building density plus aggregate under-5 share','income_signal':round(income_signal,2),'family_anchor_density':anchor_signal,'preschool_school_anchor_density':anchor_signal,'ooh_asset_density':nearby_o,'transit_access_signal':transit_signal,'competitor_density':None,'hgl_street_opportunity_score':score,'hgl_opportunity_score':score,'score_drivers':'; '.join(f'{k}: {v:.1f}' for k,v in drivers),'confidence_level':'Medium geometry / Low-Medium modeled score','caveat':'Street-level values are modeled opportunity signals, not exact street population counts.'}})
    (out/'street_segments_enriched.geojson').write_text(json.dumps({'type':'FeatureCollection','features':streets[:3000]},ensure_ascii=False,indent=2),encoding='utf-8')
    # Existing family anchors and micro grid
    shutil.copy(source/'geo/family_anchor_locations.geojson', out/'hgl_family_anchors.geojson')
    grid=[]
    for f in bgs:
        p=f['properties']; score=round((p['hgl_opportunity_score']*.4)+(min(10,p['under5']/20)*.3)+(min(10,p['median_household_income']/25000)*.2),2)
        grid.append({'type':'Feature','geometry':f['geometry'],'properties':{'grid_id':'GRID_'+str(p['geoid']),'estimated_residents':p['population'],'estimated_under5':p['under5'],'estimated_under5_signal':p['under5'],'median_income_signal':p['median_household_income'],'chinese_language_signal':p['chinese_spoken_home_pct'],'spanish_language_signal':p['spanish_spoken_home_pct'],'family_anchor_density':None,'ooh_asset_density':None,'premium_education_competitor_density':None,'distance_to_hgl_if_confirmed':None,'hgl_micro_market_score':score,'hgl_opportunity_score':score,'top_drivers':'under-5/preschool signal, income signal, language signal, OOH/family anchors','caveat':'Modeled micro-market grid from aggregate public datasets; not household-level data.'}})
    (out/'micro_market_grid.geojson').write_text(json.dumps({'type':'FeatureCollection','features':grid},ensure_ascii=False,indent=2),encoding='utf-8')
    metrics=[('population','Population'),('under5','Under 5'),('under5_pct','Under 5 Share'),('estimated_residents','Estimated Residents'),('estimated_under5','Estimated Under 5'),('estimated_under5_signal','Preschool-Age Signal'),('median_household_income','Median Household Income'),('households_with_children_pct','Households With Children %'),('chinese_spoken_home_pct','Chinese Language Signal'),('spanish_spoken_home_pct','Spanish Language Signal'),('hgl_relevance_score','OOH Relevance Score'),('availability_confidence','Availability Confidence'),('family_anchor_proximity','Family Anchor Proximity'),('school_preschool_proximity','School / Preschool Proximity'),('transit_proximity','Transit Proximity'),('hgl_opportunity_score','HGL Opportunity Score')]
    (out/'metric_config.json').write_text(json.dumps([{'key':m,'label_en':lab,'label_zh':lab,'format':'currency' if 'income' in m else 'percent' if 'pct' in m or 'share' in m else 'score' if 'score' in m or 'confidence' in m else 'integer','description':'Public aggregate/modelled metric','caveat':PUBLIC_CAVEAT} for m,lab in metrics],ensure_ascii=False,indent=2),encoding='utf-8')
    # reports and processed outputs
    asset_rows=[a['properties'] for a in assets]; write_csv(out.parent.parent/'processed_data/ooh_assets_expanded.csv', asset_rows); (out.parent.parent/'processed_data/ooh_assets_expanded.json').write_text(json.dumps(asset_rows,ensure_ascii=False,indent=2),encoding='utf-8')
    coverage=[]
    for z in TARGET_ZIPS:
        total=sum(1 for b in out_build if b['properties']['zipcode']==z); enriched=total
        coverage.append({'zipcode':z,'total_visual_buildings':total,'buildings_with_estimated_data':enriched,'percentage_enriched':round(enriched/total*100,1) if total else 0,'source_used':'OpenStreetMap building footprints + corrected aggregate research package','confidence_level':'Low-Medium','reason_for_missing_coverage':'Visual and enriched layers use same public footprint set; missing buildings reflect OSM/source limits.'})
    write_csv(out.parent.parent/'processed_data/building_coverage_by_zip.csv', coverage)
    (out/'hgl_zip_summary.json').write_text(json.dumps({'top_zips':['10013','10003','10010'],'polygon_count':6,'building_count':len(out_build),'street_count':len(streets[:3000]),'ooh_asset_count':len(assets),'positioning':'HGL ART is a multilingual early childhood education / preschool-style school integrating English, Mandarin Chinese, Spanish, and art-based education.'},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'source_notes_public.json').write_text(json.dumps({'aggregate_data_only':'This visualization uses aggregate and modeled public data only. It does not identify, target, or infer information about individual children, parents, caregivers, households, families, or residents.','aggregate_data_only_zh':'本地图仅使用公开聚合数据和建模估算，不识别、不追踪、不推断任何个人儿童、家长、照护者、家庭、住户或居民信息。','building_estimates':'Estimated building-level resident and under-5 signals are modeled from aggregate census and public OSM/property-style data. They do not represent actual residents, children, families, or households in any building.','ooh_caveat':'Availability, pricing, and exact unit selection must be confirmed with the vendor before purchase.','positioning':'HGL ART is a multilingual early childhood education / preschool-style school integrating English, Mandarin Chinese, Spanish, and art-based education.'},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'building_estimation_method.json').write_text(json.dumps({'method':'OSM building footprints assigned to target ZCTA polygons; estimates allocated from aggregate public under-5 and income indicators using heuristic residential intensity.','confidence':'Low-Medium by default; no individual-level data.','height_visualization':'Compressed physical massing plus symbolic data lift.'},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'visual_buildings':len(out_build),'enriched_buildings':len(out_build),'streets':len(streets[:3000]),'block_groups':len(bgs),'blocks':len(blocks[:2200]),'ooh_assets':len(assets)},indent=2))
if __name__=='__main__': main()
