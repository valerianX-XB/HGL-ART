import { formatValue } from '../utils/format';
export default function OohAssetTooltip({p}:any){return <><b>{p.asset_name}</b><br/>Type: {p.asset_type}<br/>Vendor / owner: {p.vendor_owner}<br/>Status: {p.asset_status}<br/>Location: {p.address_or_intersection}<br/>Relevance score: {formatValue(p.hgl_relevance_score,'score')}</>}
