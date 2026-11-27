import { NANJING_HUANGSHAN_ENDPOINTS } from './route-endpoints.js'
import publishedSites from './landmark-catalog.json' with { type: 'json' }

export const LANDMARK_DISPLAY_SIZE = 38 * 2 / 3 // Base CSS pixels on the longest dimension before viewport and zoom adjustments.
const nanjing = { city: '南京市', cityCode: '025', adcode: '320102' }
const tangkou = { city: '黄山市', cityCode: '0559', adcode: '341003' }
const dongcheng = { city: '北京市', cityCode: '010', adcode: '110101' }

function routeEndpoint(place, district) {
  return { ...district, id: place.poiId, name: place.name, address: place.address, location: place.gcj02, sourceUrl: place.sourceUrl }
}

// Model anchors are WGS84. Amap arrival points use GCJ-02 and may be outside the scenic area.
export const LANDMARKS = [
  {
    id: 'zhongshan',
    type: 'museum',
    tier: 'national',
    name: '中山陵',
    province: '江苏省',
    city: nanjing.city,
    description: '钟山南麓的陵寝建筑群。微缩模型保留通往祭堂的台阶中轴、白色石台和蓝色琉璃瓦顶。',
    anchor: [118.848288, 32.064383],
    anchorCrs: 'WGS84',
    anchorSource: 'https://www.openstreetmap.org/way/483693967',
    modelUrl: './models/zhongshan.glb',
    groundSpanMeters: 400, // Approximate extent of the stair axis used for sampling the terrain.
    displaySize: LANDMARK_DISPLAY_SIZE,
    rotationY: 0.139486,
    destination: routeEndpoint(NANJING_HUANGSHAN_ENDPOINTS.start, nanjing),
    transitDestination: {
      ...nanjing,
      id: 'BV11676369',
      name: '中山陵停车场（公交站）',
      address: '江苏省南京市玄武区钟山风景名胜区中山陵停车场旁',
      location: [118.849568, 32.047947],
      sourceUrl: 'https://ditu.amap.com/place/BV11676369',
    },
  },
  {
    id: 'huangshan',
    type: 'nature',
    tier: 'national',
    name: '黄山迎客松',
    province: '安徽省',
    city: tangkou.city,
    description: '迎客松生长在玉屏景区的花岗岩上，长枝从树干一侧伸出。上下山可从汤口换乘。',
    anchor: [118.1703509, 30.1245907],
    anchorCrs: 'WGS84',
    anchorSource: 'https://www.openstreetmap.org/node/793824902',
    modelUrl: './models/huangshan.glb',
    groundSpanMeters: 15,
    displaySize: LANDMARK_DISPLAY_SIZE,
    rotationY: -1.43814, // Local +X (the long branch) faces approximately geographic south.
    destination: routeEndpoint(NANJING_HUANGSHAN_ENDPOINTS.end, tangkou),
    transitDestination: {
      ...tangkou,
      id: 'BV09545560',
      name: '黄山风景区汽车站（公交站）',
      address: '安徽省黄山市黄山区汤口镇',
      location: [118.175299, 30.064965],
      sourceUrl: 'https://ditu.amap.com/place/BV09545560',
    },
  },
  {
    id: 'gugong',
    type: 'heritage',
    tier: 'national',
    name: '故宫太和殿',
    province: '北京市',
    city: dongcheng.city,
    description: '太和殿坐落在故宫中轴线的三层汉白玉台基上，正面朝南。观众由午门进入。',
    anchor: [116.39081395, 39.91589562],
    anchorCrs: 'WGS84',
    anchorSource: 'https://www.openstreetmap.org/way/638449347',
    modelUrl: './models/gugong.glb',
    groundSpanMeters: 90,
    displaySize: LANDMARK_DISPLAY_SIZE,
    rotationY: 0.140415, // South facade, geographic bearing 178.5° in this Albers projection.
    destination: {
      ...dongcheng,
      id: 'B0GKN7A2P0',
      name: '王府中环地下停车场（出入口）',
      address: '北京市东城区王府井大街269号',
      location: [116.409658, 39.913004],
      sourceUrl: 'https://ditu.amap.com/place/B0GKN7A2P0',
    },
    transitDestination: {
      ...dongcheng,
      id: 'BV10006499',
      name: '天安门东（地铁站）',
      address: '北京市东城区东长安街',
      location: [116.401216, 39.907780],
      sourceUrl: 'https://ditu.amap.com/place/BV10006499',
    },
  },
  ...publishedSites.map(site => ({
    ...site,
    anchorCrs: 'WGS84',
    modelUrl: `./models/${site.id}.glb`,
    displaySize: LANDMARK_DISPLAY_SIZE,
  })),
]
