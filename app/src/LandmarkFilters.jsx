import { useEffect, useId, useRef, useState } from 'react'
import { MapPin } from 'lucide-react'
import { LANDMARKS } from '../shared/landmarks.js'
import { ALL_LANDMARKS, LANDMARK_TIERS, LANDMARK_TYPES, allLandmarksSelected, matchesLandmark } from '../shared/landmark-filters.js'

function FilterGroup({ name, options, selected, onChange }) {
  const entries = Object.entries(options)
  const all = selected.length === entries.length
  return <fieldset aria-label={name}>
    <legend><span className="landmark-filter-group-title">
      <span>{name}</span>
      <button type="button" className="text-button" aria-label={all ? `清空${name}` : `全选${name}`}
        onClick={() => onChange(all ? [] : Object.keys(options))}>{all ? '清空' : '全选'}</button>
    </span></legend>
    <div className="landmark-filter-options">
      {entries.map(([value, label]) => <label key={value}>
        <input type="checkbox" checked={selected.includes(value)} onChange={event =>
          onChange(event.target.checked ? [...selected, value] : selected.filter(item => item !== value))}
        />
        <span>{label}</span>
      </label>)}
    </div>
  </fieldset>
}

export function LandmarkFilters({ filter, onChange }) {
  const [open, setOpen] = useState(false)
  const wrapper = useRef(null)
  const trigger = useRef(null)
  const panel = useRef(null)
  const panelId = useId()
  const filtered = !allLandmarksSelected(filter)
  const count = LANDMARKS.filter(landmark => matchesLandmark(landmark, filter)).length

  useEffect(() => {
    if (!open) return undefined
    const stage = wrapper.current.closest('.map-stage')
    const triggerElement = trigger.current
    const popover = panel.current
    function fitPanel() {
      const map = stage.getBoundingClientRect()
      const button = triggerElement.getBoundingClientRect()
      const below = matchMedia('(max-width: 560px)').matches
      const height = below ? map.bottom - button.bottom - 7 : button.bottom - map.top
      popover.style.setProperty('--landmark-filter-height', `${Math.max(0, height - 8)}px`)
    }
    const observer = new ResizeObserver(fitPanel)
    observer.observe(stage)
    observer.observe(stage.querySelector('.map-heading'))
    fitPanel()
    function closeOutside(event) {
      if (!wrapper.current?.contains(event.target)) setOpen(false)
    }
    function closeOnEscape(event) {
      if (event.key === 'Escape') {
        setOpen(false)
        trigger.current?.focus()
      }
    }
    document.addEventListener('pointerdown', closeOutside, true)
    document.addEventListener('keydown', closeOnEscape)
    return () => {
      observer.disconnect()
      document.removeEventListener('pointerdown', closeOutside, true)
      document.removeEventListener('keydown', closeOnEscape)
    }
  }, [open])

  return <div className="layer-menu" ref={wrapper}>
    <button type="button" className="icon-button landmark-filter-button" title="景点筛选"
      aria-label="景点筛选" aria-expanded={open} aria-controls={open ? panelId : undefined}
      data-filtered={filtered || !filter.showNames} onClick={() => setOpen(!open)} ref={trigger}>
      <MapPin size={16} strokeWidth={1.8} aria-hidden="true" /><span>景点</span>
    </button>
    {open && <div ref={panel} id={panelId} className="layer-popover landmark-filter-popover" role="group" aria-label="景点筛选">
      <FilterGroup name="类型" options={LANDMARK_TYPES} selected={filter.types}
        onChange={types => onChange({ ...filter, types })} />
      <FilterGroup name="级别" options={LANDMARK_TIERS} selected={filter.tiers}
        onChange={tiers => onChange({ ...filter, tiers })} />
      <label className="landmark-name-toggle">
        <input type="checkbox" checked={filter.showNames}
          onChange={event => onChange({ ...filter, showNames: event.target.checked })} />
        显示景点名称
      </label>
      <div className="landmark-filter-summary">
        <output aria-live="polite">{filtered ? '符合条件' : '全部景点'} {count} 处</output>
        {filtered && <button type="button" className="text-button" onClick={() =>
          onChange({ ...ALL_LANDMARKS, showNames: filter.showNames })}>显示全部</button>}
      </div>
    </div>}
  </div>
}
