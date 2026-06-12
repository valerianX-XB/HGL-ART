import { useEffect, useMemo, useState, useCallback } from 'react';
import DeckGL from '@deck.gl/react';
import Map from 'react-map-gl/maplibre';
import type { MapState, MetricConfig } from './types/data';
import { INITIAL_VIEW_STATE, MAP_STYLE } from './utils/mapConstants';
import { HEIGHT_DEFAULTS } from './utils/heightScales';
import { createZipExtrusionLayer } from './layers/zipExtrusionLayer';
import { createBlockGroupSurfaceLayer } from './layers/blockGroupSurfaceLayer';
import { createCensusBlockSurfaceLayer } from './layers/censusBlockSurfaceLayer';
import { createStreetOpportunityRibbonLayer } from './layers/streetOpportunityRibbonLayer';
import { createBuildingMassingLayer } from './layers/buildingMassingLayer';
import { createOohAssetLayer } from './layers/oohAssetLayer';
import { createBuildingHeatmapLayer } from './layers/buildingHeatmapLayer';
import { createBlockGroupHeatmapLayer } from './layers/blockGroupHeatmapLayer';
import { createCensusBlockHeatmapLayer } from './layers/censusBlockHeatmapLayer';
import { createZipChoroplethLayer } from './layers/zipChoroplethLayer';
import { CANONICAL_STREET_DATASET_PATH, CANONICAL_STREET_DATASET_VERSION, getStreetDomain } from './config/streetMetricContract';
import { createFamilyAnchorLayer } from './layers/familyAnchorLayer';
import { createSchoolPreschoolLayer } from './layers/schoolPreschoolLayer';
import { createCompetitorLayer } from './layers/competitorLayer';
import ControlPanel from './components/ControlPanel';
import Legend from './components/Legend';
import ZipTooltip from './components/ZipTooltip';
import DataTable from './components/DataTable';
import MetricCards from './components/MetricCards';
import OohAssetTable from './components/OohAssetTable';
import { getMetric } from './utils/format';
import { validateMapState } from './utils/validateMapState';

async function loadJson(path:string){ const r=await fetch(path); if(!r.ok) throw new Error(path); return r.json(); }
const typeList=['LinkNYC','Bus shelters','Newsstands','Subway / MTA','Wallscapes','Billboards','Building wraps','Private sign candidates','DOB permitted signs','Candidate walls','Other'];
const defaultStatuses=['Confirmed available','Network bookable','Potentially bookable','Permitted sign / availability unknown','Candidate to verify'];
const familyAnchorCategories=['Parks / playgrounds','Libraries','Child activity','Pediatric / health','Family retail / grocery','Museums / culture','Community centers','Transit / corridors'];

const initialState: MapState = validateMapState({
  analysisLayer: 'building',
  visualStyle: '3d',
  metricKey: 'hgl_family_opportunity_score',
  overlays: { buildings:true, ooh:true, anchors:true, schools:true, parks:true, competitors:true, zip:false, hglLocation:false },
  oohTypeFilters: new Set(typeList),
  oohStatusFilters: new Set(defaultStatuses),
  familyAnchorCategoryFilters: new Set(familyAnchorCategories),
  heightSettings: {...HEIGHT_DEFAULTS, oohMarkerRadiusPx: 4},
  selectedFeatureId: null,
  hoveredFeatureId: null,
  dataVersion: 1
});
const desktopOpen = () => typeof window === 'undefined' ? true : window.innerWidth >= 1024;

type PanelState = { infoOpen:boolean; controlsOpen:boolean; layersOpen:boolean; summaryOpen:boolean };

export default function App(){
 const [zip,setZip]=useState<any>(),[centroids,setCentroids]=useState<any>(),[bg,setBg]=useState<any>(),[blocks,setBlocks]=useState<any>(),[buildings,setBuildings]=useState<any>(),[visualBuildings,setVisualBuildings]=useState<any>(),[streets,setStreets]=useState<any>(),[streetDomains,setStreetDomains]=useState<any>(),[ooh,setOoh]=useState<any>(),[anchors,setAnchors]=useState<any>(),[schools,setSchools]=useState<any>(),[competitors,setCompetitors]=useState<any>(),[grid,setGrid]=useState<any>(),[metrics,setMetrics]=useState<MetricConfig[]>([]),[notes,setNotes]=useState<any>(),[summary,setSummary]=useState<any>();
 const [state,setStateRaw]=useState<MapState>(()=>initialState);
 const [hover,setHover]=useState<any>(null);
 const [panelState,setPanelState]=useState<PanelState>(()=>({infoOpen:desktopOpen(), controlsOpen:desktopOpen(), layersOpen:false, summaryOpen:false}));
 const setState = useCallback((next:any)=>setStateRaw(prev=>validateMapState(typeof next==='function'?next(prev):next)),[]);
 const handleHover = useCallback((info:any)=>{ setHover(info?.object ? info : null); },[]);
 const patchPanels = useCallback((patch:Partial<PanelState>)=>setPanelState(prev=>({...prev,...patch})),[]);
 useEffect(()=>{Promise.all([
  loadJson('./data/hgl_zip_market_enriched.geojson'),loadJson('./data/hgl_zip_centroids.geojson'),loadJson('./data/block_groups_official_under5.geojson'),loadJson('./data/census_blocks_enriched.geojson'),loadJson('./data/buildings_residential_capacity_v5.geojson'),loadJson('./data/buildings_visual_all.geojson'),loadJson(CANONICAL_STREET_DATASET_PATH),loadJson('./data/street_metric_domains.json'),loadJson('./data/ooh_assets_expanded_v4.geojson'),loadJson('./data/hgl_family_anchors.geojson'),loadJson('./data/schools_preschools.geojson'),loadJson('./data/competitors.geojson'),loadJson('./data/micro_market_grid.geojson'),loadJson('./data/metric_config.json'),loadJson('./data/source_notes_public.json'),loadJson('./data/hgl_zip_summary.json')]).then(([z,c,bg,bl,bu,vb,st,sd,o,a,sc,co,g,m,n,s])=>{setZip(z);setCentroids(c);setBg(bg);setBlocks(bl);setBuildings(bu);setVisualBuildings(vb);setStreets(st);setStreetDomains(sd);setOoh(o);setAnchors(a);setSchools(sc);setCompetitors(co);setGrid(g);setMetrics(m);setNotes(n);setSummary(s);});},[]);
 useEffect(()=>{const onKey=(e:KeyboardEvent)=>{if(e.key==='Escape')setPanelState(prev=> prev.summaryOpen?{...prev,summaryOpen:false}:prev.layersOpen?{...prev,layersOpen:false,controlsOpen:false}:prev.controlsOpen?{...prev,controlsOpen:false}:prev.infoOpen?{...prev,infoOpen:false}:prev);}; window.addEventListener('keydown',onKey); return()=>window.removeEventListener('keydown',onKey);},[]);
 const metric=state.metricKey, layer=state.analysisLayer, style=state.visualStyle, height=state.heightSettings;
 const selected=getMetric(metrics as any, metric);
 const activeStreetDomain = layer==='street' ? getStreetDomain(streetDomains, metric) : undefined;
 const activeFeatures = layer==='building'? buildings?.features||[] : layer==='blockGroup'? bg?.features||[] : layer==='censusBlock'? blocks?.features||[] : layer==='street'? streets?.features||[] : layer==='combined'? grid?.features||[] : layer==='ooh'? ooh?.features||[] : centroids?.features||[];
 const filteredOohCount = (ooh?.features||[]).filter((f:any)=>state.oohTypeFilters.has(f.properties.asset_type) && state.oohStatusFilters.has(f.properties.asset_status)).length;
 const layers=useMemo(()=>{
  const arr:any[]=[]; if(!zip) return arr;
  const showZip = state.overlays.zip || layer==='zip';
  if(showZip) arr.push(createZipExtrusionLayer(zip, layer==='zip'?metric:'hgl_opportunity_score', height.zipOverviewMaxM, handleHover));
  if(state.overlays.buildings && visualBuildings && layer!=='building') arr.push(createBuildingMassingLayer(visualBuildings,'neutral',true,0.18,45,0,handleHover));
  if(layer==='building' && visualBuildings) arr.push(createBuildingMassingLayer(visualBuildings,'neutral',true,height.buildingHeightMultiplier,height.buildingHeightCapM,0,handleHover));
  if(layer==='building' && buildings) style==='heatmap'?arr.push(createBuildingHeatmapLayer(buildings,metric,true)):arr.push(createBuildingMassingLayer(buildings,metric,true,height.buildingHeightMultiplier,height.buildingHeightCapM,height.dataLiftMaxM,handleHover));
  if(layer==='blockGroup' && bg) style==='heatmap'?arr.push(createBlockGroupHeatmapLayer(bg,metric,true)):arr.push(createBlockGroupSurfaceLayer(bg,metric,height.blockGroupSurfaceMaxM,true,handleHover));
  if(layer==='censusBlock' && blocks) style==='heatmap'?arr.push(createCensusBlockHeatmapLayer(blocks,metric,true)):arr.push(createCensusBlockSurfaceLayer(blocks,metric,height.censusBlockSurfaceMaxM,true,handleHover));
  if(layer==='street' && streets) arr.push(createStreetOpportunityRibbonLayer(streets,metric,height.streetSurfaceMaxM,true,handleHover,style,activeStreetDomain,CANONICAL_STREET_DATASET_VERSION));
  if(layer==='combined' && grid) style==='heatmap'?arr.push(createBlockGroupHeatmapLayer(grid,metric,true)):arr.push(createBlockGroupSurfaceLayer(grid,metric,35,true,handleHover));
  if(style==='flat' && layer==='zip') arr.push(createZipChoroplethLayer(zip,centroids,metric,handleHover));
  if((state.overlays.ooh || layer==='ooh') && ooh) arr.push(createOohAssetLayer(ooh,true,state.oohTypeFilters,state.oohStatusFilters,handleHover,height.oohMarkerRadiusPx));
  if(state.overlays.anchors && anchors) arr.push(createFamilyAnchorLayer(anchors,true,handleHover,state.familyAnchorCategoryFilters));
  if(state.overlays.schools && schools) arr.push(createSchoolPreschoolLayer(schools,true,handleHover));
  if(state.overlays.competitors && competitors) arr.push(createCompetitorLayer(competitors,true,handleHover));
  return arr.filter(Boolean);
 },[zip,centroids,bg,blocks,buildings,visualBuildings,streets,ooh,anchors,schools,competitors,grid,metric,layer,style,height,state.overlays,state.oohTypeFilters,state.oohStatusFilters,state.familyAnchorCategoryFilters,state.dataVersion,activeStreetDomain,handleHover]);
 function resetFilters(){setState({...state,oohTypeFilters:new Set(typeList),oohStatusFilters:new Set(defaultStatuses),familyAnchorCategoryFilters:new Set(familyAnchorCategories),overlays:{...state.overlays,buildings:true,ooh:true,anchors:true,schools:true,competitors:true,zip:false},dataVersion:state.dataVersion+1})}
 function resetView(){setState(initialState);}
 const closeMobilePanels=()=>patchPanels({infoOpen:false,controlsOpen:false,layersOpen:false,summaryOpen:false});
 const anyDrawerOpen=panelState.infoOpen||panelState.controlsOpen||panelState.summaryOpen;
 return <div className="app"><div className="mapShell"><DeckGL initialViewState={INITIAL_VIEW_STATE as any} controller layers={layers} getTooltip={null as any}><Map mapStyle={MAP_STYLE}/></DeckGL></div>
 <header><h1>HGL ART Street-Level Market & OOH Intelligence Map</h1><p>Market opportunity visualization for multilingual early childhood education, residential capacity, family-relevant anchors, and outdoor media planning.</p></header>
 <div className="floatingToggles" aria-label="Map panel shortcuts"><button onClick={()=>patchPanels({infoOpen:!panelState.infoOpen})}>Info</button><button onClick={()=>patchPanels({controlsOpen:!panelState.controlsOpen,layersOpen:false})}>Controls</button><button onClick={()=>patchPanels({controlsOpen:true,layersOpen:true})}>Layers</button><button onClick={()=>patchPanels({summaryOpen:!panelState.summaryOpen})}>Summary</button></div>
 {anyDrawerOpen && <button className="panelBackdrop" aria-label="Close panels" onClick={closeMobilePanels}></button>}
 <ControlPanel state={state} setState={setState} metrics={metrics} renderedCount={layers.length} filteredCount={filteredOohCount} resetView={resetView} resetFilters={resetFilters} open={panelState.controlsOpen} layersFocus={panelState.layersOpen} onClose={()=>patchPanels({controlsOpen:false,layersOpen:false})}/>
 <section className={`sideInfo ${panelState.infoOpen?'open':'collapsed'}`} aria-label="Market Summary"><button className="panelClose" aria-label="Close info panel" title="Close info panel" onClick={()=>patchPanels({infoOpen:false})}>×</button><h2>Market Summary</h2><Legend features={activeFeatures} metric={metric} metricConfig={selected} domain={activeStreetDomain}/><MetricCards features={centroids?.features||[]} summary={summary}/></section>
 <section className={panelState.summaryOpen ? 'bottom open' : 'bottom collapsed'} aria-label="Summary Table"><button className="panelClose summaryClose" aria-label="Close summary table" title="Close summary table" onClick={()=>patchPanels({summaryOpen:false})}>×</button><button onClick={()=>patchPanels({summaryOpen:!panelState.summaryOpen})}>{panelState.summaryOpen ? 'Hide summary table' : 'Summary Table'}</button>{panelState.summaryOpen && <><DataTable features={activeFeatures}/>{(state.overlays.ooh||layer==='ooh') && <OohAssetTable features={ooh?.features||[]}/>}</>}</section><ZipTooltip info={hover}/></div>
}
