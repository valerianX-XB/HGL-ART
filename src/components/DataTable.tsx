import { formatValue } from '../utils/format';
import { useMemo, useState } from 'react';

function cellValue(props:any, key:string){
 const value = props?.[key];
 if (value === null || value === undefined || value === '') return 'N/A';
 if (key === 'street_display_label' || key === 'street_name' || key === 'confidence_level' || key === 'capacity_model_confidence' || key === 'building_use_category' || key === 'residential_use_type' || key === 'address_or_label' || key === 'display_label' || key === 'zipcode') return String(value);
 return formatValue(value, key.includes('income')?'score':key.includes('pct')||key.includes('share')?'percent':key.includes('score')||key.includes('signal')||key.includes('density')?'score':undefined);
}

export default function DataTable({features}: {features:any[]}){
 const sample = features?.[0]?.properties || {};
 const defaultSort = sample.street_segment_id ? 'hgl_street_opportunity_score' : sample.residential_units_raw !== undefined ? 'hgl_family_opportunity_score' : 'hgl_opportunity_score';
 const [sortKey,setSortKey]=useState(defaultSort);
 const rows=useMemo(()=>[...(features||[])].slice(0,250).sort((a,b)=>Number(b.properties?.[sortKey]||0)-Number(a.properties?.[sortKey]||0)),[features,sortKey]);
 if(!rows.length) return null;
 const currentSample = rows[0]?.properties || {};
 const cols = currentSample.street_segment_id ? [
  ['street_display_label','Street / Corridor'],
  ['hgl_street_opportunity_score','HGL Street Opportunity Score'],
  ['street_under5_capacity_signal','Under-5 Capacity Signal'],
  ['income_signal','Income Signal'],
  ['family_anchor_density','Family Anchor Density'],
  ['school_preschool_anchor_density','School / Preschool Density'],
  ['competitor_density','Competitor Density'],
  ['ooh_asset_density','OOH Density'],
  ['confidence_level','Confidence']
 ] : currentSample.residential_units_raw !== undefined ? [
  ['address_or_label','Building'],
  ['building_use_category','Use Category'],
  ['family_residential_capacity_units','Family Capacity Units'],
  ['under5_capacity_signal','Under-5 Capacity Signal'],
  ['preschool_age_capacity_signal','Preschool-Age Signal'],
  ['hgl_family_opportunity_score','HGL Family Opportunity'],
  ['capacity_model_confidence','Confidence']
 ] : currentSample.address_or_label ? [['address_or_label','Building'],['zipcode','ZIP'],['residential_use_type','Use'],['residential_capacity_units','Capacity Units'],['estimated_household_capacity','HH Capacity'],['under5_capacity_signal','Under-5 Capacity Signal'],['hgl_building_opportunity_score','HGL Score'],['capacity_model_confidence','Confidence']] : currentSample.under5_official_bg !== undefined ? [['display_label','Block Group'],['under5_official_bg','Official Under 5 Count'],['official_under5_share','Official Under 5 Share'],['official_population','Official Population'],['official_households','Official Households'],['data_tier','Tier']] : [['zipcode','ZIP'],['under5','Official Under 5'],['median_household_income','Income'],['hgl_opportunity_score','Score']];
 return <div className="tableWrap"><table><thead><tr>{cols.map(([k,l])=><th key={k} onClick={()=>setSortKey(k)}>{l}</th>)}</tr></thead><tbody>{rows.map((f:any,i:number)=><tr key={f.properties?.street_segment_id||f.properties?.bbl||f.properties?.geoid||f.properties?.zipcode||i}>{cols.map(([k])=><td key={k}>{cellValue(f.properties,k)}</td>)}</tr>)}</tbody></table></div>
}
