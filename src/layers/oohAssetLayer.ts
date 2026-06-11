import { ScatterplotLayer } from '@deck.gl/layers';
function statusColor(status:string){ if(status==='Network bookable') return [20,184,166,185]; if(status==='Confirmed available') return [34,197,94,205]; if(status==='Potentially bookable') return [245,158,11,175]; if(status?.includes('Occupied')) return [239,68,68,150]; if(status?.includes('Permitted')) return [99,102,241,165]; if(status==='Not recommended') return [100,116,139,75]; return [59,130,246,155]; }
export function createOohAssetLayer(data:any, visible:boolean, typeFilters:Set<string>, statusFilters:Set<string>, onHover:any, markerRadiusPx:number){
 if(!visible) return null;
 const rows=(data?.features||[]).filter((f:any)=> typeFilters.has(f.properties.asset_type) && statusFilters.has(f.properties.asset_status) && f.properties.asset_status !== 'Not recommended');
 return new ScatterplotLayer({id:`ooh-assets-v4-${rows.length}-${markerRadiusPx}`, data:rows, pickable:true, radiusUnits:'pixels', radiusMinPixels:2, radiusMaxPixels:9,
  getRadius:(f:any)=>{ const base=Math.max(2,Math.min(7, markerRadiusPx||4)); return Math.min(9, base + (Number(f.properties.hgl_relevance_score||0)>8.5?1:0)); },
  getPosition:(f:any)=>f.geometry.coordinates, getFillColor:(f:any)=>statusColor(f.properties.asset_status), getLineColor:[15,23,42,170], stroked:true, lineWidthMinPixels:0.5, onHover } as any);
}
