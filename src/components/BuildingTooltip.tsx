import { formatValue } from '../utils/format';
export default function BuildingTooltip({p}:{p:any}){
 const use=p.building_use_category || p.residential_use_type || p.land_use || 'Building';
 const confidence=p.classification_confidence || p.capacity_model_confidence || p.confidence_level;
 const conflict=p.conflict_flag ? <><br/>Classification note: category based on strongest residential evidence.</> : null;
 const excluded=p.family_residential_eligible === false || p.under5_capacity_eligible === false;
 if(excluded) return <><b>{p.address_or_label || 'Building'}</b><br/>Building use category: {use}<br/>Family capacity: 0<br/>Under-5 capacity signal: 0<br/>Exclusion reason: {p.family_capacity_exclusion_reason || 'Excluded from ordinary family residential capacity.'}<br/>Confidence: {confidence}</>;
 return <><b>{p.address_or_label || 'Building'}</b><br/>Building use category: {use}<br/>Family residential capacity units: {formatValue(p.family_residential_capacity_units ?? p.residential_capacity_units)}<br/>Under-5 Capacity Signal: {formatValue(p.under5_capacity_signal,'score')}<br/>HGL family opportunity score: {formatValue(p.hgl_family_opportunity_score ?? p.hgl_building_opportunity_score,'score')}<br/>Confidence: {confidence}{conflict}</>;
}
