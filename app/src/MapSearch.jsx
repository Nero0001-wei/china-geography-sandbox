import { useEffect, useId, useMemo, useRef, useState } from 'react'
import { Landmark, MapPin, Mountain, Search, X } from 'lucide-react'
import { searchMap } from './map-search.js'
import './map-search.css'

const KINDS = {
  landmark: { label: '景点', icon: Landmark },
  city: { label: '城市', icon: MapPin },
  province: { label: '省级地区', icon: MapPin },
  landform: { label: '地貌', icon: Mountain },
}

export function MapSearch({ index, onPick }) {
  const listId = useId()
  const root = useRef(null)
  const input = useRef(null)
  const list = useRef(null)
  const [text, setText] = useState('')
  const [expanded, setExpanded] = useState(false)
  const [composing, setComposing] = useState(false)
  const [active, setActive] = useState(-1)
  const query = text.trim()
  const open = expanded && Boolean(query) && !composing
  const items = useMemo(() => composing || !query ? [] : searchMap(index, query), [index, query, composing])

  function close() {
    setExpanded(false)
    setActive(-1)
  }

  useEffect(() => {
    if (!open) return undefined
    const listbox = list.current
    const stage = listbox.closest('.map-stage')
    function fitResults() {
      const available = stage.getBoundingClientRect().bottom - listbox.getBoundingClientRect().top - 8
      listbox.style.setProperty('--map-search-space', `${Math.max(0, available)}px`)
    }
    const observer = new ResizeObserver(fitResults)
    observer.observe(stage)
    observer.observe(root.current.parentElement)
    fitResults()
    function closeOutside(event) {
      if (!root.current?.contains(event.target)) close()
    }
    document.addEventListener('pointerdown', closeOutside, true)
    return () => {
      observer.disconnect()
      document.removeEventListener('pointerdown', closeOutside, true)
    }
  }, [open])

  useEffect(() => {
    const listbox = list.current
    if (!listbox) return
    if (active < 0) {
      listbox.scrollTop = 0
      return
    }
    const option = listbox.children[active]
    if (!option) return
    const listBounds = listbox.getBoundingClientRect()
    const bounds = option.getBoundingClientRect()
    if (bounds.top < listBounds.top) listbox.scrollTop += bounds.top - listBounds.top
    else if (bounds.bottom > listBounds.bottom) listbox.scrollTop += bounds.bottom - listBounds.bottom
  }, [active, open, query])

  function edit(value) {
    setText(value)
    setExpanded(true)
    setActive(-1)
  }

  function pick(item) {
    setText(item.name)
    close()
    onPick(item)
  }

  function handleKey(event) {
    if (composing || event.nativeEvent.isComposing || event.nativeEvent.keyCode === 229) return
    if (event.key === 'Escape' && open) {
      event.preventDefault()
      event.stopPropagation()
      close()
    } else if (items.length && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      event.preventDefault()
      setExpanded(true)
      const direction = event.key === 'ArrowDown' ? 1 : -1
      setActive(current => {
        if (current < 0 || current >= items.length) return direction > 0 ? 0 : items.length - 1
        return (current + direction + items.length) % items.length
      })
    } else if (event.key === 'Enter' && open && items.length) {
      event.preventDefault()
      pick(items[active] ?? items[0])
    }
  }

  return (
    <div className="map-search" ref={root} onBlur={event => {
      if (!event.currentTarget.contains(event.relatedTarget)) close()
    }}>
      <div className="map-search-entry">
        <Search size={16} strokeWidth={1.8} aria-hidden="true" />
        <input ref={input} role="combobox" aria-label="搜索景点或地点" aria-autocomplete="list"
          aria-expanded={open} aria-controls={open ? listId : undefined}
          aria-activedescendant={open && items[active] ? `${listId}-${active}` : undefined}
          autoComplete="off" maxLength={80} placeholder="搜索景点或地点" value={text}
          onFocus={() => setExpanded(true)} onClick={() => setExpanded(true)} onKeyDown={handleKey}
          onChange={event => edit(event.target.value)} onCompositionStart={() => setComposing(true)}
          onCompositionEnd={event => { setComposing(false); edit(event.currentTarget.value) }} />
        {text && <button type="button" aria-label="清除搜索内容" onClick={() => {
          edit('')
          input.current?.focus({ preventScroll: true })
        }}><X size={16} aria-hidden="true" /></button>}
      </div>
      {open && <div className="map-search-popup">
        <ul id={listId} ref={list} className="map-search-results" role="listbox" aria-label="地图搜索结果">
          {items.map((item, position) => {
            const { label, icon: Icon } = KINDS[item.kind]
            return (
              <li key={item.id} id={`${listId}-${position}`} role="option" aria-selected={position === active}
                onMouseDown={event => event.preventDefault()} onClick={event => {
                  pick(item)
                  if (event.nativeEvent.pointerType === 'touch') input.current?.blur()
                }}>
                <Icon size={15} strokeWidth={1.75} aria-hidden="true" />
                <div className="map-search-result-name">
                  <strong>{item.name}</strong>
                  {item.subtitle && item.subtitle !== label && <small>{item.subtitle}</small>}
                </div>
                <small className="map-search-kind">{label}</small>
              </li>
            )
          })}
        </ul>
        {!items.length && <div className="map-search-empty" role="status">没有找到地点，试试输入部分名称。</div>}
      </div>}
    </div>
  )
}
