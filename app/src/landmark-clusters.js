// Distances between projected model silhouettes, in CSS pixels.
const MERGE_GAP = 3
export const CLUSTER_RELEASE_GAP = 10

export function screenGap(a, b) {
  return Math.hypot(Math.max(0, a.left - b.right, b.left - a.right),
    Math.max(0, a.top - b.bottom, b.top - a.bottom))
}

export function createLandmarkClusters() {
  let previousLinks = new Set()

  // Call with all on-screen and near-screen candidates, including hidden members of old groups.
  return function update(items) {
    const ordered = [...items].sort((a, b) => a.id.localeCompare(b.id))
    const parent = ordered.map((_, i) => i)
    const links = new Set()

    function root(i) {
      while (i !== parent[i]) i = parent[i]
      return i
    }

    for (let i = 0; i < ordered.length; i++) {
      const a = ordered[i]
      if (!a.city) continue
      for (let j = i + 1; j < ordered.length; j++) {
        const b = ordered[j]
        if (a.city !== b.city) continue
        const key = a.id + '\0' + b.id
        const gap = previousLinks.has(key) ? CLUSTER_RELEASE_GAP : MERGE_GAP
        if (screenGap(a, b) > gap) continue
        links.add(key)
        parent[root(j)] = root(i)
      }
    }
    previousLinks = links

    const groups = new Map()
    ordered.forEach((item, i) => {
      const group = root(i)
      if (!groups.has(group)) groups.set(group, [])
      groups.get(group).push(item.id)
    })
    return [...groups.values()].filter(group => group.length > 1)
  }
}
