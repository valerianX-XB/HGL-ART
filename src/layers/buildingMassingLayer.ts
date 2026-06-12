import { GeoJsonLayer } from '@deck.gl/layers';
import { colorFor } from '../utils/format';
import { extent, normalizeForHeight } from '../utils/normalizeMetrics';
import { cap } from '../utils/heightScales';

export function createBuildingMassingLayer(data:any, metricKey:string, visible:boolean, heightMultiplier:number, heightCapM:number, dataLiftMaxM:number, onHover:any) {
  if (!visible) return null;
  const features=data?.features||[];
  const neutral = metricKey === 'neutral';
  const scoreable = features.filter((f:any)=>f.properties?.family_residential_eligible !== false);
  const [min,max]=neutral?[0,1]:extent(scoreable.length ? scoreable : features, metricKey);
  return new GeoJsonLayer({ id:`building-massing-${metricKey}-${features.length}`, data, pickable:true, extruded:true, wireframe:false,
    getElevation:(f:any)=>{
      const p=f.properties||{};
      const excluded = p.family_residential_eligible === false;
      const physical=cap(Number(p.building_height_m||12)*(heightMultiplier||0.35), heightCapM||80);
      const lift=(neutral || excluded) ? 0 : normalizeForHeight(Number(p[metricKey]||0), metricKey, min, max) * Math.min(12, dataLiftMaxM||12);
      return physical + lift;
    },
    getFillColor:(f:any)=> {
      const p=f.properties||{};
      if (neutral || p.family_residential_eligible === false) return [142,148,160,125];
      return colorFor(Number(p[metricKey]||0), min, max);
    },
    getLineColor:[30,41,59,90], lineWidthMinPixels:0.25, onHover } as any);
}
