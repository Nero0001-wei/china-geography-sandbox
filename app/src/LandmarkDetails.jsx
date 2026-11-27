import { useEffect, useRef, useState } from 'react'
import { Route, X } from 'lucide-react'
import { LANDMARK_TIERS, LANDMARK_TYPES } from '../shared/landmark-filters.js'

export function LandmarkDetails({ landmark, onDismiss, onPlan, onLayout }) {
  const card = useRef(null)
  const [guides, setGuides] = useState(null)
  const [photoFailed, setPhotoFailed] = useState(false)
  const guide = guides?.[landmark.id]
  const photo = photoFailed ? null : guide?.photo
  const location = landmark.province === landmark.city
    ? landmark.city : landmark.province + ' ' + landmark.city

  useEffect(() => {
    let active = true
    import('./landmark-guides.json').then(({ default: details }) => {
      if (active) setGuides(details)
    }, () => {})
    return () => { active = false }
  }, [])

  useEffect(() => {
    const observer = new ResizeObserver(onLayout)
    observer.observe(card.current)
    return () => { observer.disconnect(); onLayout() }
  }, [onLayout])

  return <aside className="map-landmark-detail" aria-label="景点详情" ref={card}>
    <header className="landmark-detail-heading">
      <div>
        <h3>{landmark.name}</h3>
        <small>{[location, LANDMARK_TYPES[landmark.type], LANDMARK_TIERS[landmark.tier]].join(' · ')}</small>
      </div>
      <button type="button" aria-label="关闭景点详情" onClick={onDismiss}><X size={17} aria-hidden="true" /></button>
    </header>
    <div className="landmark-detail-body" tabIndex={0} aria-label="景点介绍">
      {photo && <figure className="landmark-detail-photo">
        <a href={photo.url} target="_blank" rel="noreferrer">
          <img src={`${import.meta.env.BASE_URL}data/landmark-photos/${photo.file}`} alt={photo.alt}
            decoding="async" onError={() => setPhotoFailed(true)} />
        </a>
        <figcaption>
          <span className="landmark-photo-caption">{photo.alt}</span>
          <a href={photo.url} target="_blank" rel="noreferrer">照片 · {photo.author}</a>
          {photo.licenseUrl
            ? <a href={photo.licenseUrl} target="_blank" rel="noreferrer">{photo.license}</a>
            : <span>{photo.license}</span>}
        </figcaption>
      </figure>}
      <p className="landmark-detail-summary">{guide?.summary ?? landmark.description}</p>
      {guide?.highlights.length > 0 && <section className="landmark-detail-highlights" aria-label="景点看点">
        <h4>看点</h4>
        <ul>{guide.highlights.map(item => <li key={item}>{item}</li>)}</ul>
      </section>}
      {guide?.sources.length > 0 && <div className="landmark-detail-sources">
        <span>资料来源</span>
        {guide.sources.map(source => <a key={source.url} href={source.url} target="_blank" rel="noreferrer">{source.label}</a>)}
      </div>}
    </div>
    {onPlan && <footer className="landmark-detail-actions">
      <button type="button" onClick={() => onPlan(landmark)}><Route size={15} aria-hidden="true" />设为目的地</button>
    </footer>}
  </aside>
}
