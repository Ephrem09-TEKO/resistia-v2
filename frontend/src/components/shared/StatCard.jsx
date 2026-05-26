import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

function Counter({ target, suffix = '', decimals = 0 }) {
  const [count, setCount] = useState(0)
  useEffect(() => {
    let start = 0
    const step = target / 60
    const timer = setInterval(() => {
      start += step
      if (start >= target) { setCount(target); clearInterval(timer) }
      else setCount(start)
    }, 16)
    return () => clearInterval(timer)
  }, [target])

  const formatted = decimals > 0
    ? count.toFixed(decimals)
    : Math.floor(count).toLocaleString('fr-FR')

  return <span>{formatted}{suffix}</span>
}

export default function StatCard({ icon: Icon, label, value, suffix,
  sub, color = 'cyan', trend, decimals = 0, delay = 0 }) {

  const colors = {
    cyan: {
      text:   'text-cyan',
      bg:     'bg-cyan/10',
      border: 'border-cyan/20',
      glow:   'rgba(0, 212, 255, 0.25)',
      glowSm: 'rgba(0, 212, 255, 0.08)',
    },
    violet: {
      text:   'text-violet',
      bg:     'bg-violet/10',
      border: 'border-violet/20',
      glow:   'rgba(123, 47, 255, 0.25)',
      glowSm: 'rgba(123, 47, 255, 0.08)',
    },
    bio: {
      text:   'text-bio',
      bg:     'bg-bio/10',
      border: 'border-bio/20',
      glow:   'rgba(0, 230, 118, 0.25)',
      glowSm: 'rgba(0, 230, 118, 0.08)',
    },
    amr: {
      text:   'text-amr',
      bg:     'bg-amr/10',
      border: 'border-amr/20',
      glow:   'rgba(255, 107, 53, 0.25)',
      glowSm: 'rgba(255, 107, 53, 0.08)',
    },
    danger: {
      text:   'text-danger',
      bg:     'bg-danger/10',
      border: 'border-danger/20',
      glow:   'rgba(255, 23, 68, 0.25)',
      glowSm: 'rgba(255, 23, 68, 0.08)',
    },
  }

  const c = colors[color]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      whileHover={{
        scale: 1.04,
        boxShadow: `0 0 32px ${c.glow}, 0 0 8px ${c.glow}`,
        borderColor: c.glow,
        backgroundColor: c.glowSm,
        transition: { duration: 0.25, ease: 'easeOut' },
      }}
      style={{
        background: 'rgba(255, 255, 255, 0.03)',
        backdropFilter: 'blur(12px)',
        border: `1px solid ${c.glowSm.replace('0.08', '0.2')}`,
        borderRadius: '16px',
        padding: '20px',
        cursor: 'default',
        transition: 'all 0.25s ease',
      }}>

      {/* Icône + trend */}
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2 rounded-lg ${c.bg}`}>
          <Icon size={18} className={c.text} />
        </div>
        {trend && (
          <span className={`text-xs font-mono px-2 py-0.5 rounded-full
            ${trend > 0
              ? 'bg-danger/10 text-danger border border-danger/20'
              : 'bg-bio/10 text-bio border border-bio/20'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
        )}
      </div>

      {/* Valeur */}
      <p className={`text-2xl font-bold font-mono ${c.text} mb-1`}>
        <Counter target={value} suffix={suffix} decimals={decimals} />
      </p>

      {/* Label */}
      <p className="text-sm font-semibold text-white mb-0.5">{label}</p>

      {/* Sous-label */}
      {sub && (
        <p className="text-xs text-blue-200/40">{sub}</p>
      )}
    </motion.div>
  )
}