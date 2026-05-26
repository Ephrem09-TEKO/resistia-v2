export default function ParticlesBg() {
  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    size:  Math.random() * 3 + 1,
    x:     Math.random() * 100,
    y:     Math.random() * 100,
    delay: Math.random() * 8,
    dur:   Math.random() * 6 + 6,
    color: i % 3 === 0 ? '#00D4FF' : i % 3 === 1 ? '#7B2FFF' : '#00E676',
  }))

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {particles.map(p => (
        <div key={p.id}
          className="absolute rounded-full opacity-20"
          style={{
            width:  p.size,
            height: p.size,
            left:   `${p.x}%`,
            top:    `${p.y}%`,
            background: p.color,
            boxShadow:  `0 0 ${p.size * 3}px ${p.color}`,
            animation:  `float ${p.dur}s ease-in-out ${p.delay}s infinite`,
          }}
        />
      ))}
    </div>
  )
}