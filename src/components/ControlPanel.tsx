import { LAYER_CONFIG, type AnalysisLayer } from '../config/layerMetricCompatibility';
import { getAvailableMetrics } from '../utils/getAvailableMetrics';
import { getAvailableVisualStyles } from '../utils/getAvailableVisualStyles';

export default function ControlPanel({state,setState,metrics,renderedCount,filteredCount,resetView,resetFilters}:any){
 const layer = state.analysisLayer as AnalysisLayer;
 const availableMetrics = getAvailableMetrics(layer);
 const availableStyles = getAvailableVisualStyles(layer);
 const metricOptions = metrics.filter((m:any)=>availableMetrics.includes(m.key));
 const types=['LinkNYC','Bus shelters','Newsstands','Subway / MTA','Wallscapes','Billboards','Building wraps','Private sign candidates','DOB permitted signs','Candidate walls','Other'];
 const statuses=['Confirmed available','Network bookable','Potentially bookable','Occupied / active advertiser observed','Permitted sign / availability unknown','Candidate to verify','Not recommended'];
 const familyCategories=[['Parks / playgrounds',true],['Libraries',true],['Child activity',true],['Pediatric / health',true],['Family retail / grocery',true],['Museums / culture',true],['Community centers',true],['Transit / corridors',true],['Birthday / camp / event',false]];
 const toggleSet=(key:string,value:string)=>{ const n=new Set(state[key]); n.has(value)?n.delete(value):n.add(value); setState({...state,[key]:n,dataVersion:state.dataVersion+1}); };
 const update=(patch:any)=>setState({...state,...patch,dataVersion:state.dataVersion+1});
 const updateOverlay=(key:string,value:boolean)=>update({overlays:{...state.overlays,[key]:value}});
 return <aside className="panel"><h2>Map Controls</h2>
  <label>Step 1: Analysis Layer<select value={state.analysisLayer} onChange={e=>update({analysisLayer:e.target.value})}>{Object.entries(LAYER_CONFIG).map(([k,v]:any)=><option key={k} value={k}>{v.label}</option>)}</select></label>
  <label>Step 2: Visual Style<select value={state.visualStyle} onChange={e=>update({visualStyle:e.target.value})}>{availableStyles.map(s=><option key={s} value={s}>{s==='3d'?'3D':s==='mixed'?'Mixed':s==='inventory'?'Inventory':s[0].toUpperCase()+s.slice(1)}</option>)}</select></label>
  <label>Step 3: Metric<select value={state.metricKey} onChange={e=>update({metricKey:e.target.value})}>{metricOptions.map((m:any)=><option key={m.key} value={m.key}>{m.label_en}</option>)}</select></label>
  <h3>Step 4: Overlays</h3>
  <div className="checks">
   <label><input type="checkbox" checked={state.overlays.buildings} onChange={e=>updateOverlay('buildings',e.target.checked)}/> Buildings</label>
   <label><input type="checkbox" checked={state.overlays.ooh} onChange={e=>updateOverlay('ooh',e.target.checked)}/> OOH Assets</label>
   <label><input type="checkbox" checked={state.overlays.anchors} onChange={e=>updateOverlay('anchors',e.target.checked)}/> Family-Relevant Public Anchors</label>
   <label><input type="checkbox" checked={state.overlays.schools} onChange={e=>updateOverlay('schools',e.target.checked)}/> Schools / Preschools</label>
   <label><input type="checkbox" checked={state.overlays.parks} onChange={e=>updateOverlay('parks',e.target.checked)}/> Parks / Playgrounds</label>
   <label><input type="checkbox" checked={state.overlays.competitors} onChange={e=>updateOverlay('competitors',e.target.checked)}/> Competitors</label>
   <label><input type="checkbox" checked={state.overlays.zip} onChange={e=>updateOverlay('zip',e.target.checked)}/> ZIP Boundary</label>
   <label><input type="checkbox" checked={state.overlays.hglLocation} onChange={e=>updateOverlay('hglLocation',e.target.checked)}/> HGL Location</label>
  </div>
  {state.overlays.ooh && <details open={state.analysisLayer==='ooh'}><summary>OOH Filters</summary><h3>Types</h3><div className="filterGrid">{types.map(t=><label key={t}><input type="checkbox" checked={state.oohTypeFilters.has(t)} onChange={()=>toggleSet('oohTypeFilters',t)}/>{t}</label>)}</div><h3>Status</h3><div className="filterGrid">{statuses.map(t=><label key={t}><input type="checkbox" checked={state.oohStatusFilters.has(t)} onChange={()=>toggleSet('oohStatusFilters',t)}/>{t}</label>)}</div></details>}
  {state.overlays.anchors && <details open><summary>Family Anchor Filters</summary><div className="filterGrid">{familyCategories.map(([t,hasRecords]:any)=><label key={t} className={!hasRecords?'disabled':''}><input type="checkbox" disabled={!hasRecords} checked={hasRecords && state.familyAnchorCategoryFilters.has(t)} onChange={()=>toggleSet('familyAnchorCategoryFilters',t)}/>{t}{!hasRecords?' — No records loaded':''}</label>)}</div></details>}
  <details className="advanced"><summary>Step 5: Advanced Visual Controls</summary>
    {layer==='building' && <><label>Building Height Scale {state.heightSettings.buildingHeightMultiplier}<input type="range" min="0.15" max="0.75" step="0.05" value={state.heightSettings.buildingHeightMultiplier} onChange={e=>update({heightSettings:{...state.heightSettings,buildingHeightMultiplier:Number(e.target.value)}})}/></label><label>Building Height Cap {state.heightSettings.buildingHeightCapM}m<input type="range" min="30" max="120" step="5" value={state.heightSettings.buildingHeightCapM} onChange={e=>update({heightSettings:{...state.heightSettings,buildingHeightCapM:Number(e.target.value)}})}/></label><label>Data Lift {state.heightSettings.dataLiftMaxM}m<input type="range" min="0" max="10" step="1" value={state.heightSettings.dataLiftMaxM} onChange={e=>update({heightSettings:{...state.heightSettings,dataLiftMaxM:Number(e.target.value)}})}/></label></>}
    {layer==='street' && <label>Street Surface Height {state.heightSettings.streetSurfaceMaxM}m<input type="range" min="2" max="20" step="1" value={state.heightSettings.streetSurfaceMaxM} onChange={e=>update({heightSettings:{...state.heightSettings,streetSurfaceMaxM:Number(e.target.value)}})}/></label>}
    {layer==='blockGroup' && <label>Block Surface Height {state.heightSettings.blockGroupSurfaceMaxM}m<input type="range" min="5" max="40" step="1" value={state.heightSettings.blockGroupSurfaceMaxM} onChange={e=>update({heightSettings:{...state.heightSettings,blockGroupSurfaceMaxM:Number(e.target.value)}})}/></label>}
    {layer==='censusBlock' && <label>Census Block Height {state.heightSettings.censusBlockSurfaceMaxM}m<input type="range" min="3" max="25" step="1" value={state.heightSettings.censusBlockSurfaceMaxM} onChange={e=>update({heightSettings:{...state.heightSettings,censusBlockSurfaceMaxM:Number(e.target.value)}})}/></label>}
    {layer==='zip' && <label>ZIP Overview Height {state.heightSettings.zipOverviewMaxM}m<input type="range" min="5" max="45" step="1" value={state.heightSettings.zipOverviewMaxM} onChange={e=>update({heightSettings:{...state.heightSettings,zipOverviewMaxM:Number(e.target.value)}})}/></label>}
    {layer==='ooh' && <label>Marker size {state.heightSettings.oohMarkerRadiusPx}px<input type="range" min="3" max="10" step="1" value={state.heightSettings.oohMarkerRadiusPx} onChange={e=>update({heightSettings:{...state.heightSettings,oohMarkerRadiusPx:Number(e.target.value)}})}/></label>}
  </details>
  <div className="buttonRow"><button onClick={resetFilters}>Reset Filters</button><button onClick={resetView}>Reset View</button></div>
  <div className="debug">Rendered layers: {renderedCount}<br/>Filtered OOH assets: {filteredCount}<br/>Layer: {state.analysisLayer}; Style: {state.visualStyle}; Metric: {state.metricKey}</div>
 </aside>
}
