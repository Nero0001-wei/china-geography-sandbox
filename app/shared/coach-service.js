// A bus serving a coach terminal can mention the terminal in its name or stop list.
const coachService = /(?:长途(?:客运|汽车|客车|巴士|大巴)|(?:省际|跨省|跨市|跨城|城际|市际)(?:客运|班车|大巴|快客|客车|巴士))(?!站|中心|枢纽|[东南西北总]站)/u

export function isCoachService(value) {
  return typeof value === 'string' && coachService.test(value.split(/[（(]/u)[0])
}
