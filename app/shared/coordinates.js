const ELLIPSOID_RADIUS = 6378245
const ECCENTRICITY_SQUARED = 0.006693421622965943
const RADIANS_PER_DEGREE = Math.PI / 180

function gcjOffset(lon, lat) {
  const x = lon - 105
  const y = lat - 35
  const sine = Math.sin
  const pi = Math.PI
  const shared = (20 * sine(6 * x * pi) + 20 * sine(2 * x * pi)) * 2 / 3
  const latitudeShift = -100 + 2 * x + 3 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x)) +
    shared + (20 * sine(y * pi) + 40 * sine(y * pi / 3)) * 2 / 3 +
    (160 * sine(y * pi / 12) + 320 * sine(y * pi / 30)) * 2 / 3
  const longitudeShift = 300 + x + 2 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x)) +
    shared + (20 * sine(x * pi) + 40 * sine(x * pi / 3)) * 2 / 3 +
    (150 * sine(x * pi / 12) + 300 * sine(x * pi / 30)) * 2 / 3
  const latitude = lat * RADIANS_PER_DEGREE
  const curvature = 1 - ECCENTRICITY_SQUARED * sine(latitude) ** 2

  return [
    longitudeShift * Math.sqrt(curvature) / (ELLIPSOID_RADIUS * Math.cos(latitude) * RADIANS_PER_DEGREE),
    latitudeShift * curvature ** 1.5 / (ELLIPSOID_RADIUS * (1 - ECCENTRICITY_SQUARED) * RADIANS_PER_DEGREE),
  ]
}

export function wgs84ToGcj02([lon, lat]) {
  const [dLon, dLat] = gcjOffset(lon, lat)
  return [lon + dLon, lat + dLat]
}

export function gcj02ToWgs84([lon, lat]) {
  // Fit the approximate forward offset for mainland China. The route view uses it at national scale.
  let estimate = [lon, lat]
  for (let i = 0; i < 3; i++) {
    const [dLon, dLat] = gcjOffset(...estimate)
    estimate = [lon - dLon, lat - dLat]
  }
  return estimate
}
