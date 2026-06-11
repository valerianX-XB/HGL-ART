import { formatValue } from '../utils/format';
export default function BuildingTooltip({p}:{p:any}){
 const use=p.residential_use_type || p.land_use || 'Building';
 const nonres=!!p.non_residential_flag || Number(p.residential_capacity_units||0)===0;
 if(nonres) return <><b>{p.address_or_label || 'Building'}</b><br/>Building use: {use}<br/>Residential units: 0<br/>Household capacity: 0<br/>Under-5 Capacity Signal: 0<br/>HGL Opportunity Score: 0</>;
 return <><b>{p.address_or_label || 'Building'}</b><br/>Building use: {use}<br/>Residential units: {formatValue(p.residential_units ?? p.units_res)}<br/>Household capacity: {formatValue(p.estimated_household_capacity)}<br/>Under-5 Capacity Signal: {formatValue(p.under5_capacity_signal,'score')}<br/>HGL Opportunity Score: {formatValue(p.hgl_building_opportunity_score,'score')}<br/>Confidence: {p.capacity_model_confidence || p.confidence_level}</>;
}
