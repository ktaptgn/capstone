export type Vec3 = {
  x: number;
  y: number;
  z: number;
};

export type Vec2 = {
  x: number;
  y: number;
};

export type SceneConfig = {
  unit: string;
  scale: number;
  origin: Vec3;
  bounds: {
    width: number;
    height: number;
  };
  elevationScale?: number;
  baseHeight?: number;
};

export type TerrainHeightRegion = {
  id: string;
  center: {
    x: number;
    z: number;
  };
  radius?: number;
  elevation?: number;
  height?: number;
  terrain_type?: string;
};

export type TerrainConfig = {
  type?: string;
  material?: string;
  baseColor?: string;
  terrain_heightmap?: string;
  terrain_mesh?: string;
  texture?: string;
  size?: {
    width: number;
    depth: number;
  };
  maxHeight?: number;
  height_regions?: TerrainHeightRegion[];
};

export type Facility3D = {
  id: string;
  type: string;
  name: string;
  position2d?: Vec2;
  position: Vec3;
  rotation?: Partial<Vec3>;
  size?: {
    width?: number;
    height?: number;
    depth?: number;
  };
  asset_key?: string;
  queue?: number;
  capacity?: number;
  occupied?: number;
  status?: string;
  riskLevel?: string;
};

export type Route3D = {
  id: string;
  from: string;
  to: string;
  kind: string;
  riskLevel: string;
  width: number;
  speedFactor?: number;
  wearFactor?: number;
  pmFactor?: number;
  activeTruckCount?: number;
  points: Vec3[];
};

export type TruckFrame3D = {
  time: string;
  truck_id: string;
  route_id: string;
  route_progress: number;
  position2d?: Vec2;
  position: Vec3;
  rotation_y: number;
  speed: number;
  truck_state: string;
  truck_hi: number;
  tire_hi: number;
  pm_due_hours: number;
  asset_key?: string;
  target_node?: string;
  work_order_id?: string;
  selected?: boolean;
};

export type QueueArea3D = {
  id: string;
  type: string;
  label: string;
  position2d?: Vec2;
  position: Vec3;
  size: {
    width: number;
    height: number;
    depth: number;
  };
  liveCount: number;
  capacity: number;
  severity: string;
  targetFacility: string;
};

export type Overlay3D = {
  id: string;
  type: string;
  target_id: string;
  label: string;
  visible: boolean;
  screen_anchor: string;
  severity?: string;
};

export type CameraPreset3D = {
  id: string;
  label: string;
  position: Vec3;
  target: Vec3;
  followTruckId?: string;
};

export type CameraConfig3D = {
  default_position: Vec3;
  target: Vec3;
  minZoom: number;
  maxZoom: number;
  presets: CameraPreset3D[];
};

export type C5OperationMap3DData = {
  map_version: string;
  source_basis?: string | Record<string, unknown>;
  scene: SceneConfig;
  terrain: TerrainConfig;
  facilities: Facility3D[];
  routes: Route3D[];
  queueAreas: QueueArea3D[];
  truckFrames: TruckFrame3D[];
  timeRiskProfiles?: unknown[];
  assets?: Record<string, unknown>;
  camera: CameraConfig3D;
  overlays: Overlay3D[];
  statusColorMap: Record<string, string>;
};
