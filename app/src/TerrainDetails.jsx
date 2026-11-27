import { useId } from 'react'
import { ArrowUpRight, LocateFixed, MapPin, Spline } from 'lucide-react'
import { LANDFORMS } from './terrain-data.js'

function ElevationProfile({ data, showLine, onToggleLine, longitude, onLongitude }) {
  const fillId = useId()
  const step = 0.1
  const minLongitude = data?.samples[0].longitude ?? 79
  const maxLongitude = data?.samples.at(-1).longitude ?? 122
  const index = longitude == null ? null : Math.round((longitude - minLongitude) / step)
  const point = index == null ? null : data?.samples[index]
  const left = 30
  const right = 278
  const top = 13
  const bottom = 123
  const topElevation = 7000
  const chartWidth = right - left
  const x = (longitude) => left + (longitude - minLongitude) / (maxLongitude - minLongitude) * chartWidth
  const y = (altitude) => bottom - Math.min(topElevation, Math.max(0, altitude)) / topElevation * (bottom - top)

  function trace(field) {
    return data.samples.map((entry, i) => `${i === 0 ? 'M' : 'L'}${x(entry.longitude).toFixed(2)},${y(entry[field]).toFixed(2)}`).join(' ')
  }

  function move(event) {
    if (!data) return
    const bounds = event.currentTarget.getBoundingClientRect()
    const px = (event.clientX - bounds.left) / bounds.width * 286
    const fraction = Math.max(0, Math.min(1, (px - left) / chartWidth))
    const index = Math.round(fraction * (data.samples.length - 1))
    onLongitude(data.samples[index].longitude)
  }

  const meshTrace = data ? trace('mesh') : ''
  const number = new Intl.NumberFormat('zh-CN')

  return (
    <section className="sidebar-section profile-section" aria-labelledby="profile-title">
      <div className="section-heading">
        <div>
          <h2 id="profile-title">地形剖面</h2>
          <p>沿北纬 32° 从西向东</p>
        </div>
        <button
          type="button" className="profile-toggle" aria-pressed={showLine} onClick={onToggleLine}
          disabled={!data}
        >
          <Spline size={15} aria-hidden="true" /> <span>{showLine ? '隐藏剖面线' : '显示剖面线'}</span>
        </button>
      </div>
      {data ? (
        <>
          <div className="profile-plot">
            <svg
              viewBox="0 0 286 146" role="img" aria-label="北纬 32 度东西向海拔剖面，从青藏高原降到长江中下游平原"
              onPointerMove={move} onPointerLeave={() => onLongitude(null)} onPointerDown={move}
            >
              <defs>
                <linearGradient id={fillId} x1="0" x2="0" y1="0" y2="1" gradientUnits="objectBoundingBox">
                  <stop offset="0%" stopColor="#83ccb0" stopOpacity=".46" />
                  <stop offset="100%" stopColor="#83ccb0" stopOpacity=".04" />
                </linearGradient>
              </defs>
              {[0, 2000, 4000, 6000].map((altitude) => (
                <g key={altitude}>
                  <text x="0" y={y(altitude) + 3}>{altitude / 1000}{altitude === 6000 ? ' km' : ''}</text>
                  <line x1={left} x2={right} y1={y(altitude)} y2={y(altitude)} className="chart-grid" />
                </g>
              ))}
              {[80, 90, 100, 110, 120].map((lon) => (
                <g key={lon}>
                  <line x1={x(lon)} x2={x(lon)} y1={top} y2={bottom} className="chart-grid chart-grid-light" />
                  <text x={x(lon)} y="141" textAnchor="middle">{lon}°E</text>
                </g>
              ))}
              <path d={`${meshTrace} L${right},${bottom} L${left},${bottom} Z`} fill={`url(#${fillId})`} />
              <path d={trace('source')} className="chart-source" />
              <path d={meshTrace} className="chart-mesh" />
              {point && (
                <g>
                  <line x1={x(point.longitude)} x2={x(point.longitude)} y1={top} y2={bottom} className="chart-cursor" />
                  <circle cx={x(point.longitude)} cy={y(point.mesh)} r="3.1" className="chart-dot" />
                </g>
              )}
            </svg>
            <input
              className="chart-access-input"
              type="range" aria-label="取样经度" aria-valuetext={point ? `东经 ${point.longitude} 度，${point.mesh} 米` : '东经 100 度'}
              min={minLongitude} max={maxLongitude} step={step} value={longitude ?? 100}
              onChange={(event) => onLongitude(Number(event.target.value))}
              onFocus={() => onLongitude(longitude ?? 100)} onBlur={() => onLongitude(null)}
            />
          </div>
          <div className="chart-caption">
            {point ? (
              <span className="chart-readout">{point.longitude.toFixed(1)}°E <b>{number.format(point.mesh)} m</b> <span>源高程 {number.format(point.source)} m</span></span>
            ) : (
              <>
                <span><i className="chart-key chart-key-mesh" /> 沙盘网格</span>
                <span><i className="chart-key chart-key-source" /> 源高程</span>
              </>
            )}
          </div>
        </>
      ) : <div className="chart-loading">载入剖面数据…</div>}
    </section>
  )
}

function SouthChinaSea({ inset }) {
  if (!inset) return null
  const [west, south, east, north] = inset.bounds
  const width = 282
  const height = 202
  const stretch = Math.min((width - 12) / ((east - west) * 0.97), (height - 10) / (north - south))
  const offsetX = (width - (east - west) * stretch * 0.97) / 2
  const offsetY = (height - (north - south) * stretch) / 2
  const x = (lon) => offsetX + (lon - west) * stretch * 0.97
  const y = (lat) => offsetY + (north - lat) * stretch
  const referenceLatitude = (south + north) / 2 * Math.PI / 180
  const scaleWidth = 500 / (111.32 * Math.cos(referenceLatitude)) * stretch * 0.97
  const path = (lines, close = false) => lines.map((line) =>
    line.map(([lon, lat], i) => `${i ? 'L' : 'M'}${x(lon).toFixed(1)} ${y(lat).toFixed(1)}`).join('') +
    (close ? 'Z' : ''),
  ).join('')
  const featureLabels = inset.labels.filter(({ kind }) => kind === 'feature')
  const contextLabels = inset.labels.filter(({ name }) => name === '海南岛' || name === '台湾岛')
  const labelPositions = {
    东沙群岛: [3, -6, 'start'],
    西沙群岛: [-4, -2, 'end'],
    中沙群岛: [-3, 10, 'end'],
    黄岩岛: [4, 8, 'start'],
    南沙群岛: [5, 1, 'start'],
    曾母暗沙: [4, 1, 'start'],
  }

  return (
    <section className="sidebar-section inset-section" aria-labelledby="inset-title">
      <div className="section-heading">
        <div>
          <h2 id="inset-title">南海诸岛</h2>
          <p>独立比例尺附图</p>
        </div>
        <span className="inset-north" aria-label="附图上方为北">N ↑</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="inset-map" role="img" aria-label="南海诸岛附图，含东沙、西沙、中沙、南沙群岛，黄岩岛和曾母暗沙">
        {[105, 110, 115, 120].map((lon) => (
          <line key={lon} x1={x(lon)} x2={x(lon)} y1="0" y2={height} className="inset-grid" />
        ))}
        {[5, 10, 15, 20].map((lat) => (
          <line key={lat} x1="0" x2={width} y1={y(lat)} y2={y(lat)} className="inset-grid" />
        ))}
        <path className="inset-land" fillRule="evenodd" d={path(inset.land.flat(), true)} />
        <path className="inset-maritime" d={path(inset.maritime)} />
        <path className="inset-reefs" d={path(inset.reefs)} />
        {contextLabels.map(({ name, lon, lat }) => (
          <text key={name} x={x(lon)} y={y(lat) - 4} className="inset-context" textAnchor="middle">{name}</text>
        ))}
        {featureLabels.map(({ name, lon, lat }) => {
          const [dx, dy, align] = labelPositions[name] ?? [5, -2, 'start']
          return (
            <g key={name} className="inset-feature">
              <circle cx={x(lon)} cy={y(lat)} r="1.8" />
              <text x={x(lon) + dx} y={y(lat) + dy} textAnchor={align}>{name}</text>
            </g>
          )
        })}
        <g className="inset-scale">
          <text x={width - 9} y={height - 15} textAnchor="end">约 500 km</text>
          <path d={`M${width - 9 - scaleWidth},${height - 11}v4h${scaleWidth}v-4`} />
        </g>
      </svg>
    </section>
  )
}

export function TerrainDetails({ children, data, showLine, onToggleLine, longitude, onLongitude, onFocus, selection }) {
  const active = LANDFORMS.find(({ name }) => name === selection?.name)
  return (
    <aside className="sidebar" aria-label="路线与地形信息">
      {children}
      <ElevationProfile data={data?.profile} showLine={showLine} onToggleLine={onToggleLine} longitude={longitude} onLongitude={onLongitude} />
      <section className="sidebar-section landform-section" aria-labelledby="landform-title">
        <div className="section-heading">
          <div><h2 id="landform-title">三级地势</h2><p>定位代表性地貌</p></div>
          <LocateFixed size={17} aria-hidden="true" className="section-icon" />
        </div>
        <div className="landform-list">
          {LANDFORMS.map((landform) => (
            <button
              type="button" className="landform-button" key={landform.id} aria-pressed={active?.id === landform.id}
              disabled={!data} onClick={() => onFocus(landform)}
            >
              <span className={`landform-symbol landform-${landform.id}`}><MapPin size={15} strokeWidth={1.7} aria-hidden="true" /></span>
              <span className="landform-text"><strong>{landform.name}</strong><small>{landform.description}</small></span>
              <ArrowUpRight size={16} className="landform-arrow" aria-hidden="true" />
            </button>
          ))}
        </div>
      </section>
      <SouthChinaSea inset={data?.inset} />
    </aside>
  )
}
