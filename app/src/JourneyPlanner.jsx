import { useRef, useState } from 'react'
import { ArrowDownUp, ArrowRight, ArrowUpRight, BusFront, CarFront, ChevronDown, Focus, Footprints, Landmark, LocateFixed, MapPinned, Plane, Route, Ship, TrainFront, TramFront } from 'lucide-react'
import { LANDMARKS } from '../shared/landmarks.js'
import { PlaceField } from './PlaceField.jsx'
import { amapLink, formatTime, landmarkStop, railArrivalSummary, segmentNames } from './journey-planning.js'
import { canPreviewFlight, hasSegmentTrack, ROUTE_COLORS } from './route-layer.js'
import { railVehicleForService } from './vehicle-journey.js'
import './planner.css'

const symbols = { drive: CarFront, taxi: CarFront, walk: Footprints, rail: TrainFront, flight: Plane, metro: TramFront, bus: BusFront, coach: BusFront, ferry: Ship, transfer: Route }
const connections = [['integrated', '综合换乘'], ['rail', '高铁接驳'], ['flight', '飞机接驳']]

function SegmentList({ route, previewFlights, onPreviewFlights }) {
  return <ol className="journey-steps" aria-label="行程分段">
    {route.segments.map((step, i) => {
      const Icon = symbols[step.type] || Route
      const stops = [step.from?.name, step.to?.name].filter(Boolean)
      const vehicle = step.type === 'rail' && !step.unconfirmed ? railVehicleForService(step) : null
      const railLabel = vehicle === 'high-speed-rail' ? '高铁 / 动车' : vehicle === 'intercity-rail' ? '城际列车' : segmentNames[step.type]
      const previewAvailable = canPreviewFlight(step, route)
      return <li key={i} data-kind={step.type}>
        <div className="step-icon" style={{ borderColor: ROUTE_COLORS[step.type] }}><Icon size={15} aria-hidden="true" /></div>
        <div className="step-content">
          <div className="step-heading"><strong>{step.name || railLabel || '行程段'}</strong>
            {Number.isFinite(step.durationSeconds) && step.durationSeconds > 0 && <span>{formatTime(step.durationSeconds)}</span>}</div>
          <small>{[railLabel !== step.name ? railLabel : '', stops.join(' → ')].filter(Boolean).join(' · ')}</small>
          {step.geometrySource === 'osm' && <small>沿 OpenStreetMap 铁路线绘制</small>}
          {step.geometrySource === 'rail-network' && <small>铁路网参考走向 · 按车站和区间里程匹配</small>}
          {step.geometrySource === 'amap-driving' && <small>按上下车点查询的驾车参考路线</small>}
          {previewAvailable ? <>
            <small>{previewFlights ? '虚线连接两端机场，仅作飞行示意。' : '缺少实际飞行轨迹，地图上留空。'}</small>
            <button className="pick-model" type="button" aria-pressed={previewFlights}
              onClick={() => onPreviewFlights(!previewFlights)}><Plane size={13} aria-hidden="true" />
              {previewFlights ? '关闭示意航线' : '预览机场间示意航线'}</button>
          </> : step.unavailable ? <small>该段接驳方案待查询。</small>
            : !hasSegmentTrack(step) && <small>{step.type === 'flight' ? '缺少实际飞行轨迹' : '缺少该段线路轨迹'}，地图上留空。</small>}
        </div>
      </li>
    })}
  </ol>
}

function RouteResult({ planner, onFit, previewFlights, onPreviewFlights }) {
  const { draft, route, result } = planner
  if (result.status === 'loading') return <p className="planner-message" role="status">正在查询出行方案…</p>
  if (result.status === 'error') return <p className="planner-message" role="alert">{result.message}</p>
  if (!route) return null
  const partial = route.source === 'connections'
  const reference = route.source === 'osrm'
  const segments = route.segments || []
  const hasTripDetails = draft.mode === 'transit' && segments.length > 0
  return (
    <section className="journey-result" aria-label="路线结果">
      <div className="result-heading"><h3>{planner.previewOnly ? route.title : (partial ? '分段接驳方案' : draft.mode === 'driving' ? '自驾方案' : '公共交通方案')}</h3>
        <button type="button" onClick={onFit}><Focus size={14} />路线全览</button></div>
      {result.routes.length > 1 && <div className="journey-options" aria-label="备选方案">{result.routes.map((r, i) => {
        const arrival = r.mode === 'transit' && railArrivalSummary(r)
        return <button key={i} type="button" aria-pressed={i === result.index} onClick={() => planner.selectRoute(i)}>
          <span>方案 {i + 1}{Number.isFinite(r.durationSeconds) && ' · ' + formatTime(r.durationSeconds)}</span>
          {arrival && <small>{arrival}</small>}
        </button>
      })}</div>}
      {!partial && <dl className="route-metrics">
        {Number.isFinite(route.durationSeconds) && <div><dt>预计用时</dt><dd>{formatTime(route.durationSeconds)}</dd></div>}
        {Number.isFinite(route.distanceMeters) && <div><dt>全程里程</dt><dd>{(route.distanceMeters / 1000).toLocaleString('zh-CN', { maximumFractionDigits: 1 })} <small>公里</small></dd></div>}
      </dl>}
      {partial && <p className="planner-note">{segments.some(step => step.unconfirmed)
        ? '两端按地面交通规划，中间班次待确认。' : '两端地面接驳和铁路段分别查询，换乘时间请自行预留。'}</p>}
      {hasTripDetails && <SegmentList route={route} previewFlights={previewFlights} onPreviewFlights={onPreviewFlights} />}
      {reference && route.roads && <p className="route-roads">{route.roads.join(' · ')}</p>}
      {reference ? <p className="result-source">{route.note} 本次为路网参考，未计实时路况。<br />
        <a href="https://routing.openstreetmap.de/about.html" target="_blank" rel="noreferrer">OSRM</a> / <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">© OpenStreetMap</a> · <a href="https://www.openstreetmap.org/fixthemap" target="_blank" rel="noreferrer">地图纠错</a></p> :
        <p className="result-source">{partial ? '分段路线查询 · 高德地图' : '本次路线数据 · 高德地图'}
          {segments.some(step => step.geometrySource === 'rail-network') && <> · 铁路网匹配 <a href="https://brouter.de/brouter-web/" target="_blank" rel="noreferrer">BRouter</a></>}</p>}
      {!partial && <a className="route-external" href={amapLink(draft.start.place, draft.end.place, draft.mode)} target="_blank" rel="noreferrer">在高德查看 <ArrowUpRight size={14} /></a>}
      {(segments.some(s => s.type === 'rail') || draft.connection === 'rail' && partial) &&
        <a className="route-external result-link" href="https://www.12306.cn/" target="_blank" rel="noreferrer">到铁路 12306 核对车次 <ArrowUpRight size={14} /></a>}
    </section>
  )
}

export function JourneyPlanner({ planner, onFit, onLandmark, onReset, startRef, panelRef, previewFlights, onPreviewFlights }) {
  const { draft } = planner
  const [picking, setPicking] = useState(false)
  const [landmarkQuery, setLandmarkQuery] = useState('')
  const endRef = useRef(null)

  if (planner.previewOnly) {
    return <section className="sidebar-section planner" ref={panelRef} tabIndex={-1} aria-labelledby="planner-title">
      <div className="planner-heading">
        <div className="planner-title"><MapPinned size={20} strokeWidth={1.6} /><h2 id="planner-title">路线演示</h2></div>
        {planner.route && <button className="planner-reset" type="button" onClick={() => { planner.clear(); onReset() }}>清空路线</button>}
      </div>
      {!planner.route && <button type="button" className="example-route" onClick={planner.example}>
        <Route size={13} />南京至黄山自驾演示<ArrowRight size={12} />
      </button>}
      <RouteResult planner={planner} onFit={onFit} previewFlights={previewFlights} onPreviewFlights={onPreviewFlights} />
    </section>
  }

  const matchingLandmarks = LANDMARKS.filter(item => landmarkStop(item, draft.mode) &&
    [item.name, item.province, item.city, item.description].some(text => text.includes(landmarkQuery.trim())))
  const transit = draft.mode === 'transit'
  const hub = transit && draft.connection !== 'integrated'
  const flight = draft.connection === 'flight'
  const renderField = (key, label, props) => <PlaceField label={label} value={draft[key]}
    onEdit={text => planner.edit(key, text)} onPick={place => planner.pick(key, place)} {...props} />

  return <section className="sidebar-section planner" ref={panelRef} aria-labelledby="planner-title">
    <div className="planner-heading">
      <div className="planner-title"><MapPinned size={20} strokeWidth={1.6} /><h2 id="planner-title">路线规划</h2></div>
      {(draft.start.text || draft.end.text) && <button className="planner-reset" type="button" onClick={() => { setPicking(false); planner.clear(); onReset(); startRef.current?.focus() }}>清空</button>}
    </div>
    <div className="transport-switch" role="group" aria-label="出行方式">
      <button type="button" aria-pressed={!transit} onClick={() => planner.setMode('driving')}><CarFront size={17} />自驾</button>
      <button type="button" aria-pressed={transit} onClick={() => planner.setMode('transit')}><BusFront size={16} />公共交通</button>
    </div>
    <div className="trip-inputs">
      {renderField('start', '起点', {
        marker: 'from', placeholder: '输入出发地点，如南京南站', inputRef: startRef,
        instruction: <button type="button" className="locate-origin" onClick={planner.locating ? planner.cancelLocation : planner.useDeviceLocation}
          title="使用浏览器定位，由高德查询附近地址"><LocateFixed size={14} aria-hidden="true" />{planner.locating ? '取消定位' : '使用我的位置'}</button>,
        notice: planner.locationNotice,
      })}
      <button className="swap-stops" type="button" aria-label="交换起点和目的地" title="交换起点和目的地"
        disabled={!draft.start.text && !draft.end.text} onClick={planner.swap}><ArrowDownUp size={14} /></button>
      {renderField('end', '目的地', { marker: 'to', placeholder: '输入地点，或点选地图上的模型', inputRef: endRef })}
    </div>
    <div className="landmark-picker">
      <button className="pick-model" type="button" aria-expanded={picking} onClick={() => {
        setPicking(!picking)
        setLandmarkQuery('')
      }}><Landmark size={14} />从沙盘景点选择<ChevronDown size={12} /></button>
      {picking && <div className="pick-list">
        <input type="search" className="pick-filter" aria-label="筛选沙盘景点" placeholder="搜索景点、省份或城市"
          value={landmarkQuery} onChange={event => setLandmarkQuery(event.target.value)} />
        {matchingLandmarks.map(item => <button type="button" key={item.id} onClick={() => { setPicking(false); onLandmark(item) }}>
        <span>{item.name}</span><small>{item.city}</small>
      </button>)}
        {!matchingLandmarks.length && <div className="place-feedback" role="status">没有匹配的沙盘景点</div>}
      </div>}
    </div>
    {transit && <div className="connection-type" role="group" aria-label="公共交通方案类型">
      {connections.map(([key, label]) => <button type="button" key={key} aria-pressed={draft.connection === key} onClick={() => planner.setConnection(key)}>{label}</button>)}
    </div>}
    {hub && <div className="hub-fields">
      <p>{flight ? '可自动建议两端机场，也可手动更换。航班请向航空公司核实。' : '留空时按全程方案选择车站，也可指定出发站和到达站。车次以铁路 12306 为准。'}</p>
      {renderField('departure', flight ? '起飞机场' : '出发车站', { kind: draft.connection, placeholder: flight ? '按起点所在城市建议' : '自动选择出发站' })}
      {renderField('arrival', flight ? '到达机场' : '到达车站', { kind: draft.connection, placeholder: flight ? '按终点所在城市建议' : '自动选择到达站' })}
    </div>}
    <button type="button" className="plan-submit" disabled={!planner.canPlan || planner.result.status === 'loading'} onClick={planner.calculate}>
      <span>{planner.result.status === 'loading' ? '正在查询…' : hub ? (flight ? '规划两端接驳' : '规划高铁接驳') : '规划路线'}</span><ArrowRight size={17} />
    </button>
    {!planner.canPlan && (draft.start.text || draft.end.text) && <p className="planner-hint">{!draft.start.place && draft.end.place?.landmarkName
      ? '已选中' + draft.end.place.landmarkName + '，请确认出发地点。' : planner.validation}</p>}
    {!draft.start.text && !draft.end.text && <button type="button" className="example-route" onClick={planner.example}><Route size={13} />体验南京至黄山路线 <ArrowUpRight size={12} /></button>}
    <RouteResult planner={planner} onFit={onFit} previewFlights={previewFlights} onPreviewFlights={onPreviewFlights} />
  </section>
}
