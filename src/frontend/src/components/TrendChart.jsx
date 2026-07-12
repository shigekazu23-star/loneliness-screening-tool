// ---- M7 Visualization: score trend chart ----
// Plain SVG line chart, no chart library. Large fonts and high contrast
// per the usability NFR; fixed 3-9 axis so the picture stays comparable
// between visits.

const WIDTH = 640
const HEIGHT = 280
const PAD = 48
const MIN = 3
const MAX = 9

export default function TrendChart({ history }) {
  if (!history || history.length === 0) return null

  const xs = history.map((_, i) =>
    history.length === 1
      ? WIDTH / 2
      : PAD + (i * (WIDTH - 2 * PAD)) / (history.length - 1),
  )
  const ys = history.map(
    (row) => HEIGHT - PAD - ((row.score - MIN) * (HEIGHT - 2 * PAD)) / (MAX - MIN),
  )
  const points = xs.map((x, i) => `${x},${ys[i]}`).join(' ')
  const cutoffY = HEIGHT - PAD - ((6 - MIN) * (HEIGHT - 2 * PAD)) / (MAX - MIN)

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      role="img"
      aria-label="Score trend chart"
      style={{ width: '100%', height: 'auto' }}
    >
      <rect width={WIDTH} height={HEIGHT} fill="#ffffff" />
      {[3, 6, 9].map((v) => {
        const y = HEIGHT - PAD - ((v - MIN) * (HEIGHT - 2 * PAD)) / (MAX - MIN)
        return (
          <g key={v}>
            <line x1={PAD} y1={y} x2={WIDTH - PAD} y2={y} stroke="#cccccc" />
            <text x={8} y={y + 7} fontSize="20" fill="#1a1a1a">
              {v}
            </text>
          </g>
        )
      })}
      <line
        x1={PAD}
        y1={cutoffY}
        x2={WIDTH - PAD}
        y2={cutoffY}
        stroke="#a83200"
        strokeDasharray="8 6"
        strokeWidth="2"
      />
      <polyline
        points={points}
        fill="none"
        stroke="#00509e"
        strokeWidth="4"
        strokeLinejoin="round"
      />
      {xs.map((x, i) => (
        <circle key={i} cx={x} cy={ys[i]} r="8" fill="#00509e" />
      ))}
    </svg>
  )
}
