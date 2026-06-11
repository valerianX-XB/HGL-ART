
export const HEIGHT_DEFAULTS = {
  zipOverviewMaxM: 25,
  zipOverviewHardCapM: 45,
  blockGroupSurfaceMaxM: 22,
  censusBlockSurfaceMaxM: 14,
  streetSurfaceMaxM: 12,
  buildingHeightMultiplier: 0.35,
  buildingHeightCapM: 80,
  dataLiftMaxM: 6
};
export function cap(v:number, max:number){ return Math.min(max, Math.max(0, v)); }
