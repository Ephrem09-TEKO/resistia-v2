import { motion } from 'framer-motion'
import { AlertTriangle, AlertCircle, CheckCircle, Clock } from 'lucide-react'

const LEVELS = {
  ROUGE:  { icon:AlertTriangle, color:'text-danger', bg:'bg-danger/10',  border:'border-danger/30', label:'CRITIQUE' },
  ORANGE: { icon:AlertCircle,   color:'text-amr',    bg:'bg-amr/10',     border:'border-amr/30',    label:'ALERTE'   },
  VERT:   { icon:CheckCircle,   color:'text-bio',    bg:'bg-bio/10',     border:'border-bio/30',    label:'NORMAL'   },
}

export default function AlertCard({ alerts }) {
  return (
    <motion.div
      initial={{ opacity:0, x:20 }}
      animate={{ opacity:1, x:0 }}
      transition={{ delay:0.4 }}
      className="glass p-5 border border-cyan/10 h-full">

      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-white">Alertes AMR actives</h3>
        <span className="text-xs text-blue-200/40 font-mono">
          {new Date().toLocaleDateString('fr-FR')}
        </span>
      </div>

      <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
        {alerts.map((a, i) => {
          const lvl = LEVELS[a.niveau] || LEVELS.VERT
          const Icon = lvl.icon
          return (
            <motion.div key={i}
              initial={{ opacity:0, x:10 }}
              animate={{ opacity:1, x:0 }}
              transition={{ delay: 0.1 * i }}
              className={`flex items-start gap-3 p-3 rounded-xl
                ${lvl.bg} border ${lvl.border}`}>
              <Icon size={16} className={`${lvl.color} mt-0.5 shrink-0`} />
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className={`text-xs font-bold ${lvl.color}`}>
                    {lvl.label}
                  </span>
                  <span className="text-xs text-white font-medium truncate">
                    {a.pathogene}
                  </span>
                </div>
                <p className="text-xs text-blue-200/60 mt-0.5">{a.pays}</p>
                <p className="text-xs text-blue-200/40 mt-0.5">{a.detail}</p>
              </div>
              <div className="flex items-center gap-1 text-blue-200/30
                text-xs shrink-0 ml-auto">
                <Clock size={10} />
                <span>{a.temps}</span>
              </div>
            </motion.div>
          )
        })}
      </div>
    </motion.div>
  )
}