export const LANDMARK_TYPES = {
  nature: '自然风光',
  heritage: '古迹与历史建筑',
  'town-garden': '古城、街区与园林',
  urban: '城市与工程地标',
  museum: '博物馆与纪念地',
  'theme-park': '主题乐园与动物园',
}

export const LANDMARK_TIERS = { national: '全国代表', regional: '区域代表' }
export const ALL_LANDMARKS = {
  types: Object.keys(LANDMARK_TYPES),
  tiers: Object.keys(LANDMARK_TIERS),
  showNames: true,
}

export function allLandmarksSelected({ types, tiers }) {
  return types.length === ALL_LANDMARKS.types.length && tiers.length === ALL_LANDMARKS.tiers.length
}

export function matchesLandmark(landmark, { types, tiers }) {
  return types.includes(landmark.type) && tiers.includes(landmark.tier)
}
