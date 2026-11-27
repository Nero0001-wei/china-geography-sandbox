let nextTooltipId = 0

export function createLandmarkTooltip(host, canvas, getCluster, pickModel, setHighlight) {
  const tip = document.createElement('div')
  tip.className = 'landmark-tooltip'
  tip.id = 'landmark-tooltip-' + ++nextTooltipId
  tip.setAttribute('role', 'tooltip')
  tip.hidden = true
  const list = document.createElement('ul')
  tip.append(list)
  host.append(tip)

  let pointer = null
  let activeButton = null
  let fromModel = false
  let namesKey = ''
  let dismissedId = null
  let frame = 0

  function close() {
    activeButton?.removeAttribute('aria-describedby')
    activeButton = null
    tip.hidden = true
  }

  function refresh() {
    const focus = host.contains(document.activeElement) && document.activeElement.matches('.map-landmark-label:focus-visible')
      ? document.activeElement : null
    const hit = pointer && document.elementFromPoint(pointer.clientX, pointer.clientY)
    const onTooltip = tip.contains(hit) && activeButton
    const hoveredLabel = onTooltip ? activeButton : hit?.closest('.map-landmark-label')
    const modelId = hit === canvas ? pickModel(pointer) : null
    setHighlight(hoveredLabel?.dataset.landmarkId ?? modelId ?? focus?.dataset.landmarkId)

    let button = hoveredLabel?.classList.contains('is-cluster') ? hoveredLabel : null
    let cluster
    let model = false
    if (onTooltip) {
      model = fromModel
    } else if (modelId) {
      cluster = getCluster(modelId)
      model = Boolean(cluster)
    }
    button ??= cluster?.button ?? (focus?.classList.contains('is-cluster') ? focus : null)
    cluster ??= getCluster(button?.dataset.landmarkId)
    if (!cluster || (!model && button.hidden && !button.classList.contains('has-hover-placement'))) {
      dismissedId = null
      close()
      return
    }
    const id = button.dataset.landmarkId
    if (dismissedId === id) return
    dismissedId = null
    if (activeButton !== button) {
      activeButton?.removeAttribute('aria-describedby')
      button.setAttribute('aria-describedby', tip.id)
      activeButton = button
    }
    fromModel = model
    const key = cluster.names.join('\n')
    if (key !== namesKey) {
      list.replaceChildren(...cluster.names.map(name => {
        const item = document.createElement('li')
        item.textContent = name
        return item
      }))
      namesKey = key
    }
    tip.hidden = false
    const area = host.getBoundingClientRect()
    const label = button.getBoundingClientRect()
    const labelBox = { left: label.left - area.left, right: label.right - area.left,
      top: label.top - area.top, bottom: label.bottom - area.top }
    const anchor = model ? cluster.bounds : labelBox
    const other = model ? labelBox : cluster.bounds
    const w = tip.offsetWidth, h = tip.offsetHeight
    const x = (anchor.left + anchor.right - w) / 2, y = (anchor.top + anchor.bottom - h) / 2
    const spots = [[x, anchor.bottom], [x, anchor.top - h], [anchor.right, y], [anchor.left - w, y]]
      .map(([left, top]) => [Math.max(0, Math.min(left, area.width - w)), Math.max(0, Math.min(top, area.height - h))])
    const overlaps = (left, top, box) => left < box.right && left + w > box.left && top < box.bottom && top + h > box.top
    const clear = spots.filter(([left, top]) => !overlaps(left, top, anchor))
    const [left, top] = clear.find(([left, top]) => !overlaps(left, top, other)) ?? clear[0] ?? spots[0]
    tip.style.left = Math.round(left) + 'px'
    tip.style.top = Math.round(top) + 'px'
  }

  // The map also calls refresh after it moves or regroups.
  function schedule() {
    if (!frame) frame = requestAnimationFrame(() => { frame = 0; refresh() })
  }
  function move(event) {
    pointer = event.pointerType !== 'touch' && !event.buttons ? event : null
    schedule()
  }
  function leave() {
    pointer = null
    schedule()
  }
  function dismiss() {
    dismissedId = activeButton?.dataset.landmarkId ?? null
    pointer = null
    setHighlight(null)
    close()
  }
  function onKey(event) {
    if (event.key === 'Escape' && activeButton) {
      dismissedId = activeButton.dataset.landmarkId
      close()
    } else if (event.key === 'Tab') {
      pointer = null
      dismissedId = null
    }
  }

  host.addEventListener('pointerover', move)
  host.addEventListener('pointermove', move)
  host.addEventListener('pointerleave', leave)
  host.addEventListener('pointercancel', leave)
  host.addEventListener('pointerup', move)
  host.addEventListener('pointerdown', dismiss, true)
  host.addEventListener('focusin', schedule)
  host.addEventListener('focusout', schedule)
  document.addEventListener('keydown', onKey)
  return {
    refresh,
    dispose() {
      cancelAnimationFrame(frame)
      host.removeEventListener('pointerover', move)
      host.removeEventListener('pointermove', move)
      host.removeEventListener('pointerleave', leave)
      host.removeEventListener('pointercancel', leave)
      host.removeEventListener('pointerup', move)
      host.removeEventListener('pointerdown', dismiss, true)
      host.removeEventListener('focusin', schedule)
      host.removeEventListener('focusout', schedule)
      document.removeEventListener('keydown', onKey)
      close()
      tip.remove()
    },
  }
}
