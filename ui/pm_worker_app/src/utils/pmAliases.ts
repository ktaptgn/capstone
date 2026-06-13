/** PM type → Korean alias map */
export const PM_TYPE_ALIASES: Record<string, string> = {
  'Tire PM': '타이어 정비',
  'Tire Inspection': '타이어 점검',
  'Tire Check': '타이어 체크',
  'Tire Rotation': '타이어 교체/로테이션',
  'Tire Pressure Check': '타이어 공기압 점검',
  'Emergency Tire Replace': '긴급 타이어 교체',
  'Brake Check': '브레이크 점검',
  'Brake Inspection': '브레이크 점검',
  'Suspension Check': '서스펜션 점검',
  'Full PM Service': '종합 정비',
  'Drive Unit PM': '구동부 정비',
  'Preventive PM': '예방 정비',
  'Inspection': '정기 점검',
  'PM_TIRE': '타이어 점검',
  'PM_BRAKE': '브레이크 점검',
  'PM_ENGINE': '엔진 점검',
  'PM_SUSPENSION': '서스펜션 점검',
  'PM_FULL': '종합 정비',
  'PM_DRIVE': '구동부 정비',
  'PM_HYDRAULIC': '유압 점검',
};

/**
 * Returns the Korean alias for a PM type string.
 * Falls back to the original string if no alias is found.
 */
export function getPMAlias(pmType: string): string {
  if (!pmType) return pmType;

  // Direct match
  if (PM_TYPE_ALIASES[pmType]) return PM_TYPE_ALIASES[pmType];

  // Case-insensitive match
  const lower = pmType.toLowerCase();
  for (const [key, alias] of Object.entries(PM_TYPE_ALIASES)) {
    if (key.toLowerCase() === lower) return alias;
  }

  return pmType;
}

/**
 * Extracts a short PM keyword from a longer description string.
 * e.g. "Tire PM - Front Left Replacement" → "Tire PM"
 */
export function extractPMKeyword(description: string): string {
  if (!description) return description;

  // Try to match known PM type keys anywhere in the string
  for (const key of Object.keys(PM_TYPE_ALIASES)) {
    if (description.includes(key)) return key;
  }

  // Fallback: return the part before " - " or the full string
  const dashIdx = description.indexOf(' - ');
  return dashIdx > 0 ? description.slice(0, dashIdx).trim() : description;
}
