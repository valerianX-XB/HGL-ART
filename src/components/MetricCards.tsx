import { formatValue } from '../utils/format';
function maxBy(features:any[], key:string){ return features.reduce((a,b)=>Number(a.properties[key]||0)>Number(b.properties[key]||0)?a:b); }
export default function MetricCards({features, summary}: {features:any[], summary:any}) {
  if (!features.length) return null;
  const topUnder5=maxBy(features,'under5');
  const topScore=maxBy(features,'hgl_opportunity_score');
  return <div className="cards">
    <div><b>Top Family-Eligible Residential Capacity Area</b><span>{summary?.top_family_eligible_residential_capacity_area || `${topUnder5.properties.zipcode}: ${formatValue(topUnder5.properties.under5)}`}</span></div>
    <div><b>Top Under-5 Family Capacity Area</b><span>{summary?.top_under5_family_capacity_area || `${topUnder5.properties.zipcode}: ${formatValue(topUnder5.properties.under5)}`}</span></div>
    <div><b>Highest Family-Eligible Building Opportunity Cluster</b><span>{summary?.top_family_eligible_building_opportunity_cluster || 'Family-eligible residential/mixed-use clusters in 10003, 10011, 10014'}</span></div>
    <div><b>Top Parent/Caregiver Context Corridor</b><span>{summary?.top_parent_caregiver_context_corridor || summary?.top_street_opportunity_corridor || 'Union Square / West Village / Tribeca family-access corridors'}</span></div>
    <div><b>Top OOH-Rich Corridor</b><span>{summary?.top_ooh_corridor || 'Union Square / 14th St / SoHo-Canal corridor'}</span></div>
    <div><b>Highest HGL ZIP Opportunity</b><span>{topScore.properties.zipcode}: {formatValue(topScore.properties.hgl_opportunity_score,'score')}</span></div>
  </div>
}
