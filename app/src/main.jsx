import { useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Info, Layers3, Route, X } from 'lucide-react'
import { MapView } from './MapView.jsx'
import { TerrainDetails } from './TerrainDetails.jsx'
import { JourneyPlanner } from './JourneyPlanner.jsx'
import { useJourneyPlanner } from './useJourneyPlanner.js'
import { landmarkStop } from './journey-planning.js'
import { loadMapData } from './terrain-data.js'
import './styles.css'

function DataDialog({ dialog, terrain }) {
  const source = terrain?.metadata.source
  return (
    <dialog className="data-dialog" ref={dialog} aria-labelledby="data-title">
      <div className="dialog-heading">
        <h2 id="data-title">地图数据</h2>
        <form method="dialog"><button type="submit" title="关闭" aria-label="关闭"><X size={19} /></button></form>
      </div>
      <dl>
        <div>
          <dt>高程</dt>
          <dd>USGS / NGA GMTED2010 · 30 角秒平均高程 · EGM96 高程基准。{terrain && `沙盘高程网格为 ${terrain.metadata.width} × ${terrain.metadata.height}。`}</dd>
          <dd><a href={source?.url || 'https://www.usgs.gov/coastal-changes-and-impacts/gmted2010'} target="_blank" rel="noreferrer">GMTED2010 官方资料 ↗</a></dd>
        </div>
        <div>
          <dt>地表贴图</dt>
          <dd>底色取自 NASA Blue Marble 2004 年 8 月影像，按 ESA WorldCover 2021 的林地、农田、建成区和水面调整配色。近景山脊和沟谷的明暗取自 GMTED2010 的 7.5 角秒高程。主要河湖、岸线和海深来自 Natural Earth。</dd>
          <dd>© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium.</dd>
          <dd><a href="https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/base-map/" target="_blank" rel="noreferrer">NASA Blue Marble ↗</a>
            <a href="https://doi.org/10.5281/zenodo.7254221" target="_blank" rel="noreferrer">ESA WorldCover ↗</a>
            <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer">WorldCover 许可 ↗</a></dd>
        </div>
        <div>
          <dt>交通路网</dt>
          <dd>全国概览采用 Natural Earth 道路数据。放大后按当前视野从 OpenFreeMap 加载 OpenStreetMap 道路。高德继续提供路线规划。</dd>
          <dd><a href="https://www.naturalearthdata.com/downloads/10m-cultural-vectors/roads/" target="_blank" rel="noreferrer">Natural Earth Roads ↗</a>
            <a href="https://openfreemap.org/" target="_blank" rel="noreferrer">OpenFreeMap ↗</a>
            <a href="https://openmaptiles.org/" target="_blank" rel="noreferrer">© OpenMapTiles ↗</a>
            <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">© OpenStreetMap 贡献者 ↗</a></dd>
        </div>
        <div>
          <dt>海陆与边界</dt>
          <dd>Natural Earth 1:10m 陆地范围 · 阿里云 DataV GeoAtlas 学习交流数据。香港竹篙湾、鼓浪屿、天涯海角和青岛栈桥附近的补充岸线取自 <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">© OpenStreetMap 贡献者</a>。</dd>
          <dd><a href="https://www.naturalearthdata.com/about/terms-of-use/" target="_blank" rel="noreferrer">Natural Earth ↗</a> <a href="https://help.aliyun.com/en/datav/datav-7-0/user-guide/datav-geoatlas-widgets/" target="_blank" rel="noreferrer">DataV GeoAtlas ↗</a></dd>
        </div>
        <div>
          <dt>用途</dt>
          <dd>本地地形原型。沙盘按 25 倍显示地形起伏，海拔读数保留米值。公开展示所需的边界校核和审图待完成。</dd>
        </div>
      </dl>
    </dialog>
  )
}

function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [layers, setLayers] = useState(() => ({
    provinces: true, labels: true, profile: false,
    basemap: new URLSearchParams(location.search).get('basemap') === 'roads' ? 'roads' : 'terrain',
  }))
  const [command, setCommand] = useState(null)
  const [selection, setSelection] = useState(null)
  const [landmarkDetails, setLandmarkDetails] = useState(null)
  const [sampleLongitude, setSampleLongitude] = useState(null)
  const map = useRef(null)
  const dialog = useRef(null)
  const journey = useJourneyPlanner()
  const [flightPreviewRoute, setFlightPreviewRoute] = useState(null)
  const previewFlights = journey.route != null && flightPreviewRoute === journey.route
  useEffect(() => setFlightPreviewRoute(null), [journey.route])
  const plannerPanel = useRef(null)
  const originInput = useRef(null)

  useEffect(() => {
    const request = new AbortController()
    loadMapData(request.signal).then(setData).catch((problem) => {
      if (problem.name !== 'AbortError') setError(`地图数据载入失败。${problem.message}`)
    })
    return () => request.abort()
  }, [])

  function sendCommand(action, payload) {
    setCommand({ action, payload })
  }

  function focusLandform(landform) {
    sendCommand('focus', landform)
    if (matchMedia('(max-width: 820px)').matches) {
      const behavior = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
      map.current.scrollIntoView({ behavior, block: 'start' })
    }
  }

  function toggleProfileLine() {
    setLayers((current) => ({ ...current, profile: !current.profile }))
  }

  function changeLayers(next) {
    if (next.basemap !== layers.basemap) {
      const url = new URL(location.href)
      if (next.basemap === 'roads') url.searchParams.set('basemap', 'roads')
      else url.searchParams.delete('basemap')
      history.replaceState(history.state, '', url)
    }
    setLayers(next)
  }

  function viewPlanner() {
    plannerPanel.current?.scrollIntoView({ block: 'start' })
  }

  function focusPlanner() {
    viewPlanner()
    const focusTarget = journey.previewOnly ? plannerPanel.current : originInput.current
    focusTarget?.focus({ preventScroll: true })
  }

  function showLandmark(landmark) {
    setLandmarkDetails(current => current?.landmark.id === landmark.id ? current : { landmark })
    sendCommand('focus-landmark', landmark)
  }

  function chooseLandmark(landmark) {
    if (!landmarkStop(landmark, journey.draft.mode)) {
      showLandmark(landmark)
      return
    }
    setLandmarkDetails(null)
    const needsOrigin = journey.pickLandmark(landmark)
    if (needsOrigin) sendCommand('focus-landmark', landmark)
    if (matchMedia('(max-width: 820px)').matches) viewPlanner()
    if (needsOrigin) originInput.current?.focus({ preventScroll: true })
  }

  function locateSearchResult(result) {
    const { landmark } = result
    setLandmarkDetails(landmark ? { landmark, fromSearch: true } : null)
    if (landmark) sendCommand('focus-landmark', landmark)
    else sendCommand('focus-place', result)
  }

  return (
    <div className="application">
      <header className="app-header">
        <div className="app-brand">
          <div className="brand-mark"><Layers3 size={21} strokeWidth={1.55} aria-hidden="true" /></div>
          <h1>中国地理沙盘</h1>
        </div>
        <nav className="header-actions" aria-label="沙盘工具">
        <button type="button" className="data-button planner-shortcut" onClick={focusPlanner}>
          <Route size={16} aria-hidden="true" /> {journey.previewOnly ? '路线演示' : '路线规划'}
        </button>
        <button type="button" className="data-button" onClick={() => dialog.current.showModal()}>
          <Info size={16} aria-hidden="true" /> <span>地图数据</span>
        </button>
        </nav>
      </header>
      <main className="workspace">
        <div className="map-column" ref={map}>
          <MapView
            data={data} error={error} layers={layers} onLayers={changeLayers} command={command}
            destinationLandmarkId={journey.draft.end.place?.landmarkId}
            landmarkDetails={landmarkDetails} onDismissLandmark={() => setLandmarkDetails(null)} onSearchPick={locateSearchResult}
            onPlanLandmark={!journey.previewOnly && landmarkDetails && landmarkStop(landmarkDetails.landmark, journey.draft.mode) ? chooseLandmark : null}
            route={journey.route} routeOptions={journey.result.routes} comparison={journey.result.comparison}
            previewFlights={previewFlights}
            optionNumber={journey.result.routes.length > 1 ? journey.result.index + 1 : 0} onLandmark={showLandmark}
            queryMessage={journey.result.status === 'loading' ? (journey.draft.mode === 'transit' ? '正在查询公共交通线路…' : '正在查询驾车线路…') : journey.result.message}
            onCommand={sendCommand} selection={selection} onSelect={setSelection} sampleLongitude={sampleLongitude}
          />
        </div>
        <TerrainDetails
          data={data} showLine={layers.profile} onToggleLine={toggleProfileLine}
          longitude={sampleLongitude} onLongitude={setSampleLongitude}
          onFocus={focusLandform} selection={selection}
        >
          <JourneyPlanner
            planner={journey} startRef={originInput} panelRef={plannerPanel} onLandmark={chooseLandmark}
            previewFlights={previewFlights} onPreviewFlights={enabled => setFlightPreviewRoute(enabled ? journey.route : null)}
            onFit={() => {
              sendCommand('fit-route')
              if (matchMedia('(max-width: 820px)').matches) map.current.scrollIntoView({ block: 'start' })
            }}
            onReset={() => sendCommand('reset')}
          />
        </TerrainDetails>
      </main>
      <DataDialog dialog={dialog} terrain={data?.terrain} />
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
