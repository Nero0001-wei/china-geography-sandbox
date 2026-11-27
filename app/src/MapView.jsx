import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  CircleHelp, Crosshair, Expand, Layers3, Map, Minus, Mountain, Mouse, Move, Navigation2, Pause, Play, Plus, RotateCcw, Route, X,
} from 'lucide-react'
import { createMapScene } from './map-scene.js'
import { getMapLabels, VERTICAL_EXAGGERATION } from './terrain-data.js'
import { hasSegmentTrack, ROUTE_COLORS } from './route-layer.js'
import { segmentNames, transferMarkers } from './journey-planning.js'
import { ROAD_STYLES } from './road-styles.js'
import { ALL_LANDMARKS, matchesLandmark } from '../shared/landmark-filters.js'
import { LandmarkDetails } from './LandmarkDetails.jsx'
import { LandmarkFilters } from './LandmarkFilters.jsx'
import { MapSearch } from './MapSearch.jsx'
import { createMapSearchIndex } from './map-search.js'
import administrativePlaces from '../shared/map-places.json'

function IconButton({ icon: Icon, label, ...props }) {
  return (
    <button type="button" className="icon-button" title={label} aria-label={label} {...props}>
      <Icon size={18} strokeWidth={1.7} aria-hidden="true" />
    </button>
  )
}

function SurfaceLegend() {
  const swatches = [['植被', '#718948'], ['裸地', '#d8b578'], ['冰雪', '#f1eee4'], ['水域', '#9ebfdc']]
  return (
    <div className="map-legend" aria-label="地表设色图例">
      <div className="legend-title">地表设色</div>
      <div className="surface-swatches">
        {swatches.map(([name, color]) => <span key={name}><i style={{ backgroundColor: color }} />{name}</span>)}
      </div>
    </div>
  )
}

function RouteSwatch({ type, children }) {
  return <span><i className="direction-swatch" style={{ backgroundColor: ROUTE_COLORS[type] ?? ROUTE_COLORS.drive }} aria-hidden="true" />{children}</span>
}

function TransitLegend({ segments }) {
  const types = [...new Set(segments.map(segment => segment.type))]
  return <div className="map-legend" aria-label="公共交通线路图例">
    <div className="legend-title">行程线路</div>
    <div className="route-swatches">{types.map(type =>
      <RouteSwatch key={type} type={type}>{segmentNames[type] || '其他'}</RouteSwatch>
    )}</div>
  </div>
}

function RoadLegend({ kinds = [], driving }) {
  const items = kinds.map(key => ROAD_STYLES[key])
  return <div className="map-legend" aria-label="道路图例">
    <div className="legend-title">道路等级</div>
    <div className="route-swatches road-swatches">
      {items.map(({ label, color }) => <span key={label}><i style={{ backgroundColor: color }} />{label}</span>)}
      {driving && <RouteSwatch type="drive">所选驾车路线</RouteSwatch>}
    </div>
  </div>
}

function RoadCredits({ phase, detailUnavailable, rail }) {
  const detailed = phase === 'detail'
  return <div className="road-credits" aria-label="路网数据来源">
    <span role="status">{phase === 'loading' ? '正在载入路网' : phase === 'unavailable' ? '路网暂不可用'
      : detailUnavailable ? '街道数据暂不可用，显示概览' : ''}</span>
    <a href="https://www.naturalearthdata.com/downloads/10m-cultural-vectors/roads/" target="_blank" rel="noreferrer">Natural Earth</a>
    {detailed && <>
      <a href="https://openfreemap.org/" target="_blank" rel="noreferrer">OpenFreeMap</a>
      <a href="https://openmaptiles.org/" target="_blank" rel="noreferrer">© OpenMapTiles</a>
    </>}
    {(detailed || rail) && <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">© OpenStreetMap</a>}
  </div>
}

function BasemapSwitch({ layers, onLayers }) {
  return <div className="basemap-switch" role="radiogroup" aria-label="地图底图">
    {[['terrain', '自然地形', Mountain], ['roads', '交通路网', Route]].map(([value, label, Icon]) =>
      <label key={value}>
        <input type="radio" name="basemap" value={value} checked={layers.basemap === value}
          onChange={() => onLayers({ ...layers, basemap: value })} />
        <span><Icon size={15} strokeWidth={1.7} aria-hidden="true" />{label}</span>
      </label>)}
  </div>
}

function LayersMenu({ layers, onLayers }) {
  const [open, setOpen] = useState(false)
  const menu = useRef(null)
  const button = useRef(null)

  useEffect(() => {
    if (!open) return undefined
    function closeOutside(event) {
      if (!menu.current?.contains(event.target)) setOpen(false)
    }
    function closeOnEscape(event) {
      if (event.key === 'Escape') {
        setOpen(false)
        button.current?.focus()
      }
    }
    document.addEventListener('pointerdown', closeOutside, true)
    document.addEventListener('keydown', closeOnEscape)
    return () => {
      document.removeEventListener('pointerdown', closeOutside, true)
      document.removeEventListener('keydown', closeOnEscape)
    }
  }, [open])

  return (
    <div className="layer-menu" ref={menu}>
      <button
        className="icon-button" type="button" title="地图图层" aria-label="地图图层"
        aria-expanded={open} onClick={() => setOpen(!open)} ref={button}
      >
        <Layers3 size={18} strokeWidth={1.7} aria-hidden="true" />
      </button>
      {open && (
        <div className="layer-popover" role="group" aria-label="可见图层">
          <fieldset><legend>叠加图层</legend>{[
            ['provinces', '省级边界'],
            ['labels', '地貌标注'],
            ['profile', '北纬 32° 剖面线'],
          ].map(([key, label]) => (
            <label key={key}>
              <input type="checkbox" checked={layers[key]} onChange={() => onLayers({ ...layers, [key]: !layers[key] })} />
              {label}
            </label>
          ))}</fieldset>
        </div>
      )}
    </div>
  )
}

export function MapView({ data, layers, onLayers, command, onCommand, route, routeOptions, previewFlights, comparison, optionNumber, queryMessage, onLandmark, destinationLandmarkId, landmarkDetails, onDismissLandmark, onPlanLandmark, onSearchPick, sampleLongitude, selection, onSelect, error }) {
  const viewport = useRef(null)
  const mapLabelGroup = useRef(null)
  const roadLabelGroup = useRef(null)
  const marker = useRef(null)
  const profilePoint = useRef(null)
  const compass = useRef(null)
  const scaleLine = useRef(null)
  const scaleText = useRef(null)
  const controller = useRef(null)
  const refreshOverlays = useCallback(() => controller.current?.refreshOverlays(), [])
  const displayedOptions = useRef(null)
  const landmarkHandler = useRef(onLandmark)
  useEffect(() => { landmarkHandler.current = onLandmark }, [onLandmark])
  const [failure, setFailure] = useState('')
  const [ready, setReady] = useState(false)
  const [showingDifference, setShowingDifference] = useState(false)
  const [roadStatus, setRoadStatus] = useState({ phase: 'loading' })
  const [playback, setPlayback] = useState({ available: false, playing: false })
  const [landmarkFilter, setLandmarkFilter] = useState(ALL_LANDMARKS)
  const localDifference = comparison?.kind === 'local'
  const boundaries = data?.boundaries
  const searchIndex = useMemo(() => boundaries && createMapSearchIndex(boundaries, administrativePlaces), [boundaries])
  const selectedLandmark = landmarkDetails?.landmark
  const searchedLandmarkId = landmarkDetails?.fromSearch ? selectedLandmark.id : null

  useEffect(() => {
    if (!data) return undefined
    let instance
    try {
      instance = createMapScene(viewport.current, {
        labels: Array.from(mapLabelGroup.current.children),
        roadLabels: roadLabelGroup.current,
        marker: marker.current,
        profilePoint: profilePoint.current,
        compass: compass.current,
        scaleLine: scaleLine.current,
        scaleText: scaleText.current,
      }, data, {
        onSelect,
        onLandmark: landmark => landmarkHandler.current?.(landmark),
        onDifferenceView: setShowingDifference,
        onRoadStatus: setRoadStatus,
        onPlayback: setPlayback,
        onContextLost: () => setFailure('三维渲染已暂停，正在等待浏览器恢复。'),
        onContextRestored: () => setFailure(''),
      })
      controller.current = instance
      setReady(true)
    } catch (problem) {
      console.error(problem)
      setFailure(`三维地图初始化失败。${problem.message}`)
    }
    return () => {
      controller.current = null
      displayedOptions.current = null
      instance?.dispose()
    }
  }, [data, onSelect])

  useEffect(() => {
    controller.current?.setLayers(layers)
    controller.current?.markProfile(sampleLongitude)
  }, [data, layers, sampleLongitude])

  useEffect(() => {
    controller.current?.setDestinationLandmark(destinationLandmarkId)
  }, [data, destinationLandmarkId])

  useEffect(() => {
    controller.current?.setLandmarkFilter(landmarkFilter, searchedLandmarkId)
  }, [data, landmarkFilter, searchedLandmarkId])

  useEffect(() => {
    if (!controller.current) return
    controller.current.setRoute(route, {
      fit: displayedOptions.current !== routeOptions,
      focusCoordinates: comparison?.coordinates,
      stationMarkers: localDifference ? transferMarkers(route.segments) : [],
      previewFlights,
    })
    displayedOptions.current = route ? routeOptions : null
  }, [route, routeOptions, previewFlights, comparison, localDifference, data])

  useEffect(() => {
    if (!command || !controller.current) return
    controller.current.command(command.action, command.payload)
  }, [command])

  const mapError = error || failure
  const elevationText = selection?.elevation == null ? '' : `${selection.elevation.toLocaleString('zh-CN')} m`
  const coordinateText = selection
    ? `${selection.lon.toFixed(3)}°E · ${selection.lat.toFixed(3)}°N`
    : '点地形测海拔 · 横拖景点旋转'
  const transit = route?.mode === 'transit'
  const segments = route?.segments ?? []
  const tracks = transit ? segments.filter(hasSegmentTrack) : []
  const networkReference = tracks.some(step => step.geometrySource === 'rail-network')
  const hasRailCredit = networkReference || tracks.some(step => step.geometrySource === 'osm')
  const roadMode = layers.basemap === 'roads'
  let mapCaption = roadMode ? (roadStatus.phase === 'detail' ? '区域道路' : '全国公路概览') : 'Albers 等积圆锥投影'
  if (transit) {
    const missingRail = segments.find(step => step.type === 'rail' && !step.unconfirmed && !hasSegmentTrack(step)
      && step.from?.name && step.to?.name)
    mapCaption = previewFlights ? '虚线为机场间示意航线' : tracks.length === 0 ? '暂无线路轨迹，仅标起终点'
      : missingRail ? `${missingRail.from.name}至${missingRail.to.name}缺少铁路轨迹`
      : tracks.length < segments.length ? '仅显示已有轨迹的路段'
      : networkReference ? '公共交通 · 含铁路网参考走向' : '公共交通 · 分段线路'
  } else if (route) {
    mapCaption = route.source === 'osrm' ? '驾车路线 · 路网参考' : '高德驾车路线'
  }

  return (
    <section className="map-panel" aria-label="中国三维地形">
      <div className={'map-stage' + (roadMode ? ' has-road-map' : '')}>
        <div ref={viewport} className="map-viewport" />
        <div ref={roadLabelGroup} className="road-label-group" aria-hidden="true" />
        <div className="map-label-group" ref={mapLabelGroup} aria-hidden="true">
          {getMapLabels(data?.boundaries).map(({ name, water, secondary, island }) => (
            <span className="map-label-anchor" hidden key={name}>
              {island && <span className="map-island-dot" />}
              <span className={`map-label${water ? ' map-label-water' : ''}${secondary ? ' map-label-secondary' : ''}${island ? ' map-label-island' : ''}`}>{name}</span>
            </span>
          ))}
        </div>
        <div className="marker-anchor" ref={marker} hidden>
          <span className="marker-dot" />
          {selection && (
            <div className="marker-label" aria-hidden="true">
              <span>{selection.name || '地形采样点'}</span>{elevationText && ` ${elevationText}`}
            </div>
          )}
        </div>
        <div className="marker-anchor profile-map-marker" ref={profilePoint} aria-hidden="true" hidden>
          <span className="marker-dot" />
        </div>
        <div className="map-heading">
          <div className="map-title-row">
            <h2>{route?.title || (roadMode ? '交通路网' : '全国地形')}</h2>
            {route && playback.available && !mapError && <button type="button" className="route-playback"
              aria-label={playback.playing ? '暂停路线动画' : '播放路线动画'}
              title={playback.playing ? '暂停路线动画' : '播放路线动画'}
              onClick={() => controller.current?.togglePlayback()}>
              {playback.playing ? <Pause size={13} aria-hidden="true" /> : <Play size={13} aria-hidden="true" />}
              {playback.playing ? '暂停' : '播放'}
            </button>}
          </div>
          <span aria-live="polite">{queryMessage || [
            optionNumber > 0 && '方案 ' + optionNumber,
            showingDifference ? '差异路段' : comparison?.kind === 'same' ? '两种方案的线路走向重合' : mapCaption,
          ].filter(Boolean).join(' · ')}</span>
          {localDifference && <button type="button" className="comparison-view"
            onClick={() => onCommand(showingDifference ? 'fit-route' : 'fit-difference')}>
            <Expand size={13} aria-hidden="true" />{showingDifference ? '查看全程' : '查看差异路段'}
          </button>}
          {ready && !mapError && <MapSearch index={searchIndex} onPick={onSearchPick} />}
        </div>

        {ready && !mapError && <BasemapSwitch layers={layers} onLayers={onLayers} />}
        <div className="map-tools" aria-label="地图视角工具" hidden={!ready || Boolean(mapError)}>
          <button type="button" title="重置为北向斜俯视" aria-label="重置为北向斜俯视" className="compass-button" onClick={() => onCommand('reset')}>
            <span>北</span>
            <Navigation2 ref={compass} size={22} strokeWidth={1.4} fill="currentColor" aria-hidden="true" />
          </button>
          <div className="control-group">
            <IconButton icon={Plus} label="放大" onClick={() => onCommand('zoom-in')} />
            <IconButton icon={Minus} label="缩小" onClick={() => onCommand('zoom-out')} />
          </div>
          <div className="control-group">
            <IconButton icon={Expand} label="正上方俯瞰" onClick={() => onCommand('top')} />
            <IconButton icon={RotateCcw} label="重置视角" onClick={() => onCommand('reset')} />
          </div>
          <LayersMenu layers={layers} onLayers={onLayers} />
          <LandmarkFilters filter={landmarkFilter} onChange={setLandmarkFilter} />
        </div>

        {ready && !mapError && selectedLandmark && (searchedLandmarkId || matchesLandmark(selectedLandmark, landmarkFilter)) &&
          <LandmarkDetails key={selectedLandmark.id} landmark={selectedLandmark} onDismiss={onDismissLandmark}
            onPlan={onPlanLandmark} onLayout={refreshOverlays} />}

        {(!ready || mapError) && (
          <div className="map-status" role={mapError ? 'alert' : 'status'}>
            {mapError ? <CircleHelp size={23} /> : <Map size={23} />}
            <p>{mapError || '正在载入地形与地表贴图…'}</p>
            {mapError && (
              <button type="button" className="text-button" onClick={() => window.location.reload()}>重新加载</button>
            )}
          </div>
        )}

        {tracks.length ? <TransitLegend segments={tracks} /> : roadMode
          ? <RoadLegend kinds={roadStatus.kinds} driving={route?.mode === 'driving'} /> : <SurfaceLegend />}
        <div className="map-scale" style={{ visibility: ready ? 'visible' : 'hidden' }}>
          <div ref={scaleText} />
          <div className="scale-line" ref={scaleLine} />
          {!roadMode && hasRailCredit && <a className="track-credit" href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer" aria-label="铁路线数据版权归 OpenStreetMap 贡献者所有">© OpenStreetMap 贡献者</a>}
        </div>
        {roadMode && <RoadCredits {...roadStatus} rail={hasRailCredit} />}
      </div>
      <footer className="map-footer">
        <div aria-live="polite" className="map-position">
          <Crosshair size={14} aria-hidden="true" />
          <span>{coordinateText}</span>
          {selection && (
            <>
              {elevationText && <strong>{elevationText}</strong>}
              <button type="button" title={selection.name ? '清除定位标记' : '清除采样点'}
                aria-label={selection.name ? '清除定位标记' : '清除采样点'} onClick={() => onCommand('clear')}><X size={13} /></button>
            </>
          )}
        </div>
        <div className="map-instructions">
          <span className="desktop-instructions"><Move size={13} />左键拖动旋转 · 中键拖动平移 <Mouse size={13} />滚轮缩放</span>
          <span className="touch-instructions">单指旋转 · 双指缩放和平移</span>
          <span className="exaggeration">垂直夸张 <b>{VERTICAL_EXAGGERATION}×</b></span>
        </div>
      </footer>
    </section>
  )
}
