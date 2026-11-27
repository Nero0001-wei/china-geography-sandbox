import { useEffect, useId, useState } from 'react'
import { MapPin, X } from 'lucide-react'

export function PlaceField({ label, value, onEdit, onPick, placeholder, inputRef, kind, marker, instruction, notice }) {
  const id = useId()
  const [expanded, setExpanded] = useState(false)
  const [composing, setComposing] = useState(false)
  const [list, setList] = useState({ status: 'idle', items: [] })
  const [active, setActive] = useState(-1)
  const query = value.text.trim()
  const search = expanded && !value.place && !composing && query.length >= 2

  useEffect(() => {
    setActive(-1)
    setList({ status: 'loading', items: [] })
    if (!search) return
    const controller = new AbortController()
    const timer = setTimeout(async () => {
      try {
        const args = new URLSearchParams({ q: query })
        if (kind) args.set('kind', kind)
        const response = await fetch('./api/places?' + args, { signal: controller.signal })
        const data = await response.json()
        if (controller.signal.aborted) return
        if (!response.ok || data.status !== 'ok') throw new Error(data.message || '地点搜索暂不可用')
        setList({ status: 'ready', query, items: data.places || [] })
      } catch (error) {
        if (!controller.signal.aborted) setList({ status: 'error', query, items: [], message: error.message })
      }
    }, 380)
    return () => { clearTimeout(timer); controller.abort() }
  }, [search, query, kind])

  function pick(item) {
    setExpanded(false)
    setActive(-1)
    onPick(item)
  }

  const items = list.query === query ? list.items : []
  function keyDown(e) {
    if (e.nativeEvent.isComposing || composing) return
    if (e.key === 'Escape') { setExpanded(false); return }
    if (!items.length || !search) return
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault()
      setActive(i => e.key === 'ArrowDown' ? (i + 1) % items.length : (i <= 0 ? items.length - 1 : i - 1))
    } else if (e.key === 'Enter' && active >= 0) {
      e.preventDefault()
      pick(items[active])
    }
  }

  return (
    <div className={'place-field ' + (marker || '')} onBlur={e => {
      if (!e.currentTarget.contains(e.relatedTarget)) setExpanded(false)
    }}>
      <div className="place-label"><label htmlFor={id}>{label}</label>{instruction}</div>
      <div className="place-entry">
        <input id={id} ref={inputRef} role="combobox" autoComplete="off" aria-autocomplete="list"
          aria-expanded={Boolean(search)} aria-controls={search ? id + '-list' : undefined}
          aria-activedescendant={search && active >= 0 ? id + '-' + active : undefined}
          placeholder={placeholder} value={value.text}
          onCompositionStart={() => setComposing(true)} onCompositionEnd={() => setComposing(false)}
          onFocus={() => setExpanded(true)} onKeyDown={keyDown}
          onChange={e => { setExpanded(true); onEdit(e.target.value) }} />
        {value.text && <button type="button" aria-label={'清除' + label} onClick={e => {
          onEdit(''); e.currentTarget.parentElement.querySelector('input').focus()
        }}><X size={13} /></button>}
      </div>
      {value.place && <small className="place-address">{value.place.landmarkName ? value.place.landmarkName + ' · ' : ''}{value.place.address || value.place.city}</small>}
      {Number.isFinite(value.place?.accuracyMeters) && <small className="place-address">设备定位精度约 {Math.max(1, value.place.accuracyMeters).toLocaleString('zh-CN')} 米，可按实际情况修改地址。</small>}
      {notice && <small className="place-address" role="status">{notice}</small>}
      {search && <div className="place-popover">
        <ul id={id + '-list'} role="listbox" aria-label={label + '候选地点'}>
          {items.map((item, index) => <li id={id + '-' + index} key={item.id || index} role="option" aria-selected={index === active}
            onMouseDown={e => e.preventDefault()} onClick={() => pick(item)} onMouseEnter={() => setActive(index)}>
            <MapPin size={14} aria-hidden="true" /><div><strong>{item.name}</strong><small>{[item.city, item.address].filter(Boolean).join(' · ')}</small></div>
          </li>)}
        </ul>
        {!items.length && <div className="place-feedback" role="status">{list.query !== query || list.status === 'loading' ? '正在搜索地点…' :
          (list.message || '没有找到地点，试试加上城市名。')}</div>}
      </div>}
    </div>
  )
}
