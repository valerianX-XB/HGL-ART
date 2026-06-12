import { formatValue, metricExtent } from '../utils/format';
export default function Legend({features, metric, metricConfig, domain}:any){
 const [min,max]=domain || (features?.length?metricExtent(features,metric):[0,1]);
 const label=metricConfig?.label_en || metric;
 const fmt=metricConfig?.format;
 const kind=metric?.includes('score')?'Score':metric?.includes('count')?'Count':metric?.includes('signal')?'Signal':'';
 return <div className="legend"><b>{label}</b>{kind && <div className="tierBadge">{kind}</div>}<div className="bar"></div><span>{formatValue(min,fmt)} → {formatValue(max,fmt)}</span></div>
}
