import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Globe2, FlaskConical, Pill, Brain,
  TrendingUp, Shield, AlertTriangle, Activity,
  Users, Dna, Microscope, Zap
} from 'lucide-react'
import StatCard from '../components/shared/StatCard'
import AlertCard from '../components/shared/AlertCard'
import { apiDashboard } from '../services/api'
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
} from 'recharts'

const TENDANCE_DEFAULT = [
  { annee:'2015', afro:32, searo:30, amro:22, euro:18 },
  { annee:'2016', afro:33, searo:31, amro:23, euro:18 },
  { annee:'2017', afro:34, searo:31, amro:23, euro:19 },
  { annee:'2018', afro:35, searo:32, amro:24, euro:19 },
  { annee:'2019', afro:36, searo:32, amro:25, euro:20 },
  { annee:'2020', afro:36, searo:33, amro:25, euro:20 },
  { annee:'2021', afro:37, searo:33, amro:26, euro:21 },
  { annee:'2022', afro:37, searo:34, amro:27, euro:21 },
  { annee:'2023', afro:38, searo:34, amro:27, euro:22 },
  { annee:'2024', afro:38, searo:34, amro:28, euro:22 },
  { annee:'2025', afro:38, searo:34, amro:29, euro:23 },
]

const LIGNES = [
  { key:'euro',  color:'#7B2FFF', label:'EURO'  },
  { key:'amro',  color:'#FF6B35', label:'AMRO'  },
  { key:'searo', color:'#00E676', label:'SEARO' },
  { key:'afro',  color:'#00D4FF', label:'AFRO'  },
]

const TOP_PATHOGENES = [
  { nom:'Candida auris',       taux:91, color:'#FF1744' },
  { nom:'A. baumannii XDR',    taux:58, color:'#FF1744' },
  { nom:'K. pneumoniae KPC',   taux:42, color:'#FF1744' },
  { nom:'E. coli ESBL',        taux:35, color:'#FF6B35' },
  { nom:'S. aureus SARM',      taux:28, color:'#FF6B35' },
  { nom:'P. aeruginosa MDR',   taux:25, color:'#FF6B35' },
  { nom:'M. tuberculosis MDR', taux:12, color:'#7B2FFF' },
]

const ALERTES_DEFAULT = [
  { niveau:'ROUGE',  pathogene:'K. pneumoniae KPC',   pays:'Grèce — EURO',       detail:'Résistance colistine 95% détectée',    temps:'2h'  },
  { niveau:'ROUGE',  pathogene:'Candida auris MDR',   pays:'Inde — SEARO',       detail:'Émergence souche pan-résistante',       temps:'5h'  },
  { niveau:'ORANGE', pathogene:'E. coli MCR+',        pays:'Nigeria — AFRO',     detail:'Profil MCR+KPC inhabituel signalé',     temps:'8h'  },
  { niveau:'ORANGE', pathogene:'A. baumannii XDR',    pays:'Irak — EMRO',        detail:'Augmentation rapide +18% en 30 jours', temps:'12h' },
  { niveau:'VERT',   pathogene:'S. aureus SARM',      pays:'France — EURO',      detail:'Taux stable dans les normes EARS-Net',  temps:'1j'  },
  { niveau:'ORANGE', pathogene:'M. tuberculosis MDR', pays:'Bangladesh — SEARO', detail:'Cluster familial de 4 cas signalé',     temps:'1j'  },
]

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null
  return (
    <div style={{
      background:'#0D1528', border:'1px solid rgba(0,212,255,0.2)',
      borderRadius:12, padding:'10px 14px', fontSize:12
    }}>
      <p style={{ color:'#00D4FF', fontWeight:'bold', marginBottom:6 }}>{label}</p>
      {[...payload].reverse().map((p, i) => (
        <p key={i} style={{ color:p.color, marginBottom:2 }}>
          {p.name?.toUpperCase()} : {p.value}%
        </p>
      ))}
    </div>
  )
}

export default function Dashboard() {
  const [apiStats, setApiStats]     = useState(null)
  const [alertes, setAlertes]       = useState(ALERTES_DEFAULT)
  const [tendance, setTendance]     = useState(TENDANCE_DEFAULT)

  useEffect(() => {
    apiDashboard.getStats().then(data => {
      if (data) setApiStats(data)
    })
    apiDashboard.getAlertes().then(data => {
      if (data && Array.isArray(data)) setAlertes(data)
    })
    apiDashboard.getTendance().then(data => {
      if (data && Array.isArray(data)) setTendance(data)
    })
  }, [])

  // ── KPIs — définis DANS le composant pour accéder à apiStats ──
  const STATS = [
    { icon:Globe2,       label:'Pays couverts',        value: apiStats?.pays_couverts         || 194,     suffix:'',  color:'cyan',   sub:'6 régions OMS',              trend:null, delay:0    },
    { icon:FlaskConical, label:'Pathogènes suivis',     value: apiStats?.pathogenes_suivis     || 42,      suffix:'',  color:'violet', sub:'dont 8 ESKAPE critiques',     trend:null, delay:0.1  },
    { icon:Pill,         label:'Antibiotiques indexés', value: apiStats?.antibiotiques         || 82,      suffix:'',  color:'bio',    sub:'+ antifongiques/antiparas.',   trend:null, delay:0.2  },
    { icon:Brain,        label:'Modèles IA actifs',     value: apiStats?.modeles_actifs        || 10,      suffix:'',  color:'amr',    sub:'ResistIA Brain 🧠',            trend:null, delay:0.3  },
    { icon:Activity,     label:'Antibiogrammes',        value: apiStats?.antibiogrammes_total  || 1088340, suffix:'',  color:'cyan',   sub:'dans la base mondiale',       trend:3.2,  delay:0.4  },
    { icon:Shield,       label:'Taux résistance moyen', value: apiStats?.taux_resistance_moyen || 32.4,    suffix:'%', color:'amr',    sub:'AFRO 2025 — tendance ↑',      trend:1.8,  delay:0.5, decimals:1 },
    { icon:AlertTriangle,label:'Anomalies détectées',   value: apiStats?.anomalies_detectees   || 32024,   suffix:'',  color:'danger', sub:'sur 544 170 taux analysés',   trend:null, delay:0.6  },
    { icon:Users,        label:'Décès AMR / an',        value: apiStats?.deces_amr_an          || 1270000, suffix:'',  color:'danger', sub:'source OMS 2019 — en hausse', trend:5.1,  delay:0.7  },
  ]

  return (
    <div className="space-y-8 pb-8">

      {/* En-tête */}
      <motion.div initial={{ opacity:0, y:-20 }} animate={{ opacity:1, y:0 }}
        className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">
            Bonjour 👋 — voici ce qui se passe dans le monde aujourd'hui
          </h2>
          <p className="text-blue-200/50 text-sm">
            La résistance aux antibiotiques tue 1 personne toutes les 25 secondes.
            ResistIA surveille, analyse et agit en temps réel.
          </p>
        </div>
        <div className="flex items-center gap-2 glass px-4 py-2 border border-bio/20">
          <Zap size={14} className="text-bio" />
          <span className="text-bio text-sm font-semibold">10 modèles IA actifs</span>
        </div>
      </motion.div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {STATS.map((s, i) => (
          <StatCard key={i} {...s} />
        ))}
      </div>

      {/* Graphique + Alertes */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
          transition={{ delay:0.5 }}
          className="lg:col-span-2 glass p-5 border border-cyan/10">
          <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
            <div>
              <h3 className="font-bold text-white">
                Évolution mondiale de la résistance
              </h3>
              <p className="text-xs text-blue-200/40 mt-0.5">
                Taux moyen par région OMS — 2015 à 2025
              </p>
            </div>
            <div className="flex items-center gap-3 flex-wrap text-xs">
              {[...LIGNES].reverse().map(l => (
                <div key={l.label} className="flex items-center gap-1">
                  <div className="w-3 h-0.5 rounded"
                    style={{ background:l.color }} />
                  <span className="text-blue-200/50">{l.label}</span>
                </div>
              ))}
            </div>
          </div>
          <div style={{ width:'100%', height:220 }}>
            <LineChart
              width={620} height={220} data={tendance}
              margin={{ top:5, right:10, bottom:5, left:0 }}>
              <XAxis dataKey="annee"
                tick={{ fill:'#94a3b8', fontSize:11 }}
                axisLine={false} tickLine={false} />
              <YAxis
                tick={{ fill:'#94a3b8', fontSize:11 }}
                axisLine={false} tickLine={false}
                tickFormatter={v => `${v}%`}
                domain={[15, 45]} />
              <Tooltip content={<CustomTooltip />} />
              {LIGNES.map(l => (
                <Line key={l.key} type="monotone"
                  dataKey={l.key} name={l.label}
                  stroke={l.color} strokeWidth={2}
                  dot={false} strokeLinecap="round" />
              ))}
            </LineChart>
          </div>
        </motion.div>

        <AlertCard alerts={alertes} />
      </div>

      {/* Top pathogènes */}
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
        transition={{ delay:0.6 }}
        className="glass p-5 border border-cyan/10">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-bold text-white">
              Pathogènes les plus résistants en 2025
            </h3>
            <p className="text-xs text-blue-200/40 mt-0.5">
              Classés par taux de résistance mondial décroissant
            </p>
          </div>
          <Microscope size={18} className="text-blue-200/30" />
        </div>
        <div className="space-y-3">
          {TOP_PATHOGENES.map((p, i) => (
            <motion.div key={i}
              initial={{ opacity:0, x:-20 }}
              animate={{ opacity:1, x:0 }}
              transition={{ delay: 0.05*i + 0.6 }}
              className="flex items-center gap-4">
              <span className="text-xs text-blue-200/30 font-mono w-4">{i+1}</span>
              <span className="text-sm text-blue-200/80 w-44 truncate font-medium">
                {p.nom}
              </span>
              <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width:0 }}
                  animate={{ width:`${p.taux}%` }}
                  transition={{ delay: 0.05*i + 0.8, duration:0.8 }}
                  className="h-full rounded-full"
                  style={{
                    background: p.color,
                    boxShadow: `0 0 8px ${p.color}60`
                  }} />
              </div>
              <span className="text-sm font-mono font-bold w-12 text-right"
                style={{ color:p.color }}>
                {p.taux}%
              </span>
              <span className={`text-xs px-2 py-0.5 rounded-full border
                ${p.taux >= 50
                  ? 'bg-danger/10 text-danger border-danger/20'
                  : p.taux >= 25
                    ? 'bg-amr/10 text-amr border-amr/20'
                    : 'bg-violet/10 text-violet border-violet/20'}`}>
                {p.taux >= 50 ? 'CRITIQUE' : p.taux >= 25 ? 'ÉLEVÉ' : 'MODÉRÉ'}
              </span>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* CTA */}
      <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }}
        transition={{ delay:0.9 }}
        className="glass p-6 border border-cyan/20
          bg-gradient-to-r from-cyan/5 to-violet/5">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-cyan/10 border border-cyan/20">
              <Dna size={24} className="text-cyan" />
            </div>
            <div>
              <p className="font-bold text-white">
                Prêt à analyser un antibiogramme ?
              </p>
              <p className="text-sm text-blue-200/50">
                ResistIA Brain identifie le meilleur traitement en 2 secondes —
                pour n'importe quelle bactérie, n'importe où dans le monde.
              </p>
            </div>
          </div>
          <a href="/analyse" className="btn-primary flex items-center gap-2 no-underline">
            <Microscope size={16} />
            Lancer une analyse
          </a>
        </div>
      </motion.div>
    </div>
  )
}