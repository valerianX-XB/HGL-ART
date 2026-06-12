# V5.4.2 Street Metric Contract

Canonical dataset: `public/data/canonical_street_capacity_signal.geojson`.

Required fields are present on every feature. Missing source fields are set to `null`; the UI must not silently substitute ZIP score or block-group count.

| Field | Source rule |
|---|---|
| `street_segment_id` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `street_name` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `from_intersection` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `to_intersection` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `hgl_street_opportunity_score` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `street_under5_capacity_signal` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `street_preschool_age_demand_signal` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `residential_capacity_nearby` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `income_signal` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `family_anchor_density` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `school_preschool_anchor_density` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `competitor_density` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `ooh_asset_density` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `transit_access_signal` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |
| `confidence_level` | Direct canonical field; alias mapped only during V5.4.2 canonicalization where documented. |

Enabled static display metrics: `hgl_street_opportunity_score`, `street_under5_capacity_signal`, `income_signal`, `family_anchor_density`, `ooh_asset_density`, `school_preschool_anchor_density`, `competitor_density`, `transit_access_signal`.
Overlay visibility only changes context layers and never recomputes these fields.