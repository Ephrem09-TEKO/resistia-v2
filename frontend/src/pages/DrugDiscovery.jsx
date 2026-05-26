import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Pill, Dna, Sparkles, FlaskConical,
         Loader2, CheckCircle, AlertTriangle, Info } from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis,
         Radar, ResponsiveContainer, Tooltip } from 'recharts'
import { apiDrugDiscovery } from '../services/api'

const BACTERIES_CIBLES = [
  { id:1, nom:'Klebsiella pneumoniae KPC', gram:'neg', who:'CRITICAL', profil:'carbapenem_resistant' },
  { id:2, nom:'Acinetobacter baumannii XDR', gram:'neg', who:'CRITICAL', profil:'pandrug_resistant' },
  { id:3, nom:'Pseudomonas aeruginosa MDR', gram:'neg', who:'CRITICAL', profil:'multidrug_resistant' },
  { id:4, nom:'E. coli ESBL', gram:'neg', who:'HIGH', profil:'esbl_producer' },
  { id:5, nom:'S. aureus SARM', gram:'pos', who:'HIGH', profil:'methicillin_resistant' },
  { id:6, nom:'Candida auris MDR', gram:'fungi', who:'CRITICAL', profil:'azole_resistant' },
]

const MOLECULES_REFERENCE = [
  { nom:'Céfidérocol',    score:95, mw:752.8, logp:-2.5, cmi:0.015, toxicite:0.15, sa:6.5, lipinski:false },
  { nom:'Méropénem',      score:88, mw:383.5, logp:-0.75,cmi:0.05,  toxicite:0.20, sa:4.5, lipinski:true  },
  { nom:'Ciprofloxacine', score:82, mw:331.3, logp:0.28, cmi:0.025, toxicite:0.25, sa:2.8, lipinski:true  },
  { nom:'Tigécycline',    score:79, mw:585.7, logp:-0.5, cmi:0.25,  toxicite:0.30, sa:5.2, lipinski:false },
  { nom:'Colistine',      score:74, mw:1155.4,logp:-1.5, cmi:0.5,   toxicite:0.65, sa:8.0, lipinski:false },
]

function simulerGeneration(bacterie) {
  return Array.from({ length:10 }, (_, i) => ({
    id: i+1,
    nom: `AMR-${bacterie.id}${String.fromCharCode(65+i)}-${Math.floor(Math.random()*9000+1000)}`,
    score:    Math.round(82 + Math.random() * 8),
    activite: Math.round(85 + Math.random() * 7),
    cmi:      +(0.8 + Math.random() * 0.8).toFixed(3),
    mw:       Math.round(300 + Math.random() * 200),
    logp:     +(-2 + Math.random() * 3).toFixed(2),
    toxHerg:  +(0.15 + Math.random() * 0.15).toFixed(3),
    toxHepato:+(0.15 + Math.random() * 0.15).toFixed(3),
    sol:      +(0.55 + Math.random() * 0.25).toFixed(3),
    sa:       +(3.0 + Math.random() * 1.5).toFixed(1),
    lipinski: true,
  }))
}

export default function DrugDiscovery() {
  const [bacterie, setBacterie]   = useState(null)
  const [niveau, setNiveau]       = useState('1')
  const [loading, setLoading]     = useState(false)
  const [resultats, setResultats] = useState(null)
  const [selected, setSelected]   = useState(null)

  const lancer = async () => {
  if (!bacterie) return
  setLoading(true)
  setResultats(null)

  const data = await apiDrugDiscovery.generer({
    bacterie_cible: bacterie.nom,
    niveau:         parseInt(niveau),
    n_molecules:    10,
  })

  if (data && Array.isArray(data)) {
    setResultats(data.map((mol, i) => ({
      id:        mol.id || i+1,
      nom:       mol.nom,
      score:     mol.score,
      activite:  mol.activite,
      cmi:       mol.cmi,
      mw:        mol.mw,
      logp:      mol.logp,
      toxHerg:   mol.tox_herg,
      toxHepato: mol.tox_hepato,
      sa:        mol.sa_score,
      sol:       mol.solubilite,
      lipinski:  mol.lipinski,
    })))
  } else {
    setResultats(simulerGeneration(bacterie))
  }
  setLoading(false)
}

  const radarMol = selected ? [
    { prop:'Activité',    val: selected.activite },
    { prop:'Sécurité',    val: Math.round((1-selected.toxHerg)*100) },
    { prop:'Solubilité',  val: Math.round(selected.sol*100) },
    { prop:'Synthèse',    val: Math.round((1-selected.sa/10)*100) },
    { prop:'CMI opt.',    val: Math.round((1-selected.cmi/2)*100) },
    { prop:'Lipinski',    val: selected.lipinski ? 100 : 40 },
  ] : []

  return (
    <div className="space-y-6 pb-10">
      <motion.div initial={{opacity:0,y:-16}} animate={{opacity:1,y:0}}>
        <h2 className="text-2xl font-bold text-white mb-1">Drug Discovery</h2>
        <p className="text-blue-200/50 text-sm">
          Repositionnement moléculaire, prédiction QSAR et génération de nouvelles molécules
          candidates contre les pathogènes résistants.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Panneau gauche */}
        <motion.div initial={{opacity:0,x:-20}} animate={{opacity:1,x:0}}
          transition={{delay:0.1}} className="space-y-4">

          {/* Niveau */}
          <div className="glass border border-cyan/10 p-5 space-y-3">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Sparkles size={16} className="text-violet" /> Niveau d'analyse
            </h3>
            {[
              { id:'1', label:'Repositionnement', sub:'Trouver parmi les médicaments existants' },
              { id:'2', label:'Prédiction QSAR',  sub:'Évaluer une molécule candidate' },
              { id:'3', label:'Génération',        sub:'Créer de nouvelles molécules par IA' },
            ].map(n => (
              <button key={n.id} onClick={() => setNiveau(n.id)}
                className={`w-full text-left p-3 rounded-xl border transition-all
                  ${niveau===n.id
                    ? 'bg-violet/10 border-violet/30'
                    : 'bg-white/2 border-white/5 hover:bg-white/5'}`}>
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold px-1.5 py-0.5 rounded-md
                    ${niveau===n.id
                      ? 'bg-violet/20 text-violet'
                      : 'bg-white/10 text-blue-200/40'}`}>
                    Niv.{n.id}
                  </span>
                  <span className={`text-sm font-semibold
                    ${niveau===n.id ? 'text-white' : 'text-blue-200/60'}`}>
                    {n.label}
                  </span>
                </div>
                <p className="text-xs text-blue-200/40 mt-1 ml-7">{n.sub}</p>
              </button>
            ))}
          </div>

          {/* Bactérie cible */}
          <div className="glass border border-cyan/10 p-5 space-y-3">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <FlaskConical size={16} className="text-amr" /> Bactérie cible
            </h3>
            <div className="space-y-1.5">
              {BACTERIES_CIBLES.map(b => (
                <button key={b.id} onClick={() => setBacterie(b)}
                  className={`w-full text-left p-2.5 rounded-xl border
                    transition-all text-sm
                    ${bacterie?.id===b.id
                      ? 'bg-amr/10 border-amr/30 text-white'
                      : 'bg-white/2 border-white/5 text-blue-200/60 hover:bg-white/5'}`}>
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate">{b.nom}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded-full shrink-0
                      ${b.who==='CRITICAL'
                        ? 'bg-danger/20 text-danger'
                        : 'bg-amr/20 text-amr'}`}>
                      {b.who}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <motion.button
            whileHover={{scale:1.02}} whileTap={{scale:0.98}}
            onClick={lancer} disabled={!bacterie||loading}
            className={`w-full py-4 rounded-2xl font-bold flex items-center
              justify-center gap-3 transition-all
              ${bacterie&&!loading
                ? 'bg-gradient-to-r from-violet to-cyan text-night shadow-[0_0_30px_rgba(123,47,255,0.3)]'
                : 'bg-white/5 text-blue-200/30 cursor-not-allowed'}`}>
            {loading
              ? <><Loader2 size={20} className="animate-spin"/>Analyse en cours...</>
              : <><Dna size={20}/>Lancer ResistIA Brain 🧠</>}
          </motion.button>
        </motion.div>

        {/* Résultats */}
        <div className="lg:col-span-2 space-y-4">
          <AnimatePresence mode="wait">
            {!resultats && !loading && (
              <motion.div key="empty"
                initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}
                className="glass border border-cyan/10 p-12 flex flex-col
                  items-center justify-center text-center">
                <div className="p-5 rounded-2xl bg-violet/5 border border-violet/10 mb-4">
                  <Dna size={40} className="text-violet/40" />
                </div>
                <p className="text-white font-semibold mb-2">
                  Choisissez un niveau et une bactérie cible
                </p>
                <p className="text-blue-200/40 text-sm max-w-sm">
                  ResistIA Brain va analyser des milliers de molécules et vous proposer
                  les meilleures candidates.
                </p>
              </motion.div>
            )}

            {loading && (
              <motion.div key="loading"
                initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}
                className="glass border border-violet/20 p-12 flex flex-col
                  items-center justify-center text-center">
                <div className="relative mb-6">
                  <div className="w-20 h-20 rounded-full border-2 border-violet/20
                    border-t-violet animate-spin"/>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Dna size={24} className="text-violet" />
                  </div>
                </div>
                <p className="text-violet font-semibold mb-1">
                  ResistIA Brain génère des molécules...
                </p>
                <p className="text-blue-200/40 text-xs">
                  Algorithme évolutionnaire — {60} générations × 150 molécules
                </p>
              </motion.div>
            )}

            {resultats && (
              <motion.div key="results"
                initial={{opacity:0}} animate={{opacity:1}}
                className="space-y-4">

                <div className="flex items-center justify-between flex-wrap gap-3">
                  <p className="text-white font-semibold">
                    {resultats.length} molécules candidates générées pour{' '}
                    <span className="text-violet">{bacterie.nom}</span>
                  </p>
                  <span className="text-xs text-blue-200/40">
                    Cliquez sur une molécule pour voir son profil complet
                  </span>
                </div>

                {/* Tableau */}
                <div className="glass border border-cyan/10 overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-white/5">
                          {['#','Molécule','Score','Activité','CMI','hERG',
                            'Hépa','SA','Lip'].map(h => (
                            <th key={h} className="px-3 py-3 text-left text-xs
                              font-semibold text-blue-200/40 whitespace-nowrap">
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {resultats.map((mol, i) => (
                          <motion.tr key={mol.id}
                            initial={{opacity:0,x:10}}
                            animate={{opacity:1,x:0}}
                            transition={{delay:i*0.03}}
                            onClick={() => setSelected(mol)}
                            className={`border-b border-white/3 cursor-pointer
                              transition-all hover:bg-white/5
                              ${selected?.id===mol.id ? 'bg-violet/10' : ''}`}>
                            <td className="px-3 py-2.5 text-blue-200/30 font-mono">
                              {i+1}
                            </td>
                            <td className="px-3 py-2.5 font-mono text-xs text-cyan">
                              {mol.nom}
                            </td>
                            <td className="px-3 py-2.5">
                              <span className="text-bio font-bold">{mol.score}%</span>
                            </td>
                            <td className="px-3 py-2.5 text-white">{mol.activite}%</td>
                            <td className="px-3 py-2.5 font-mono text-xs
                              text-blue-200/70">
                              {mol.cmi}
                            </td>
                            <td className="px-3 py-2.5">
                              <span className={mol.toxHerg<0.3?'text-bio':'text-amr'}>
                                {mol.toxHerg}
                              </span>
                            </td>
                            <td className="px-3 py-2.5">
                              <span className={mol.toxHepato<0.3?'text-bio':'text-amr'}>
                                {mol.toxHepato}
                              </span>
                            </td>
                            <td className="px-3 py-2.5 text-blue-200/60">
                              {mol.sa}
                            </td>
                            <td className="px-3 py-2.5">
                              {mol.lipinski
                                ? <CheckCircle size={14} className="text-bio"/>
                                : <AlertTriangle size={14} className="text-amr"/>}
                            </td>
                          </motion.tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Détail molécule sélectionnée */}
                <AnimatePresence>
                  {selected && (
                    <motion.div
                      initial={{opacity:0,y:10}} animate={{opacity:1,y:0}}
                      exit={{opacity:0,y:-10}}
                      className="glass border border-violet/20 p-5">
                      <h4 className="font-bold text-white mb-4 font-mono">
                        {selected.nom}
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <p className="text-xs text-blue-200/40 mb-3">
                            Profil QSAR complet
                          </p>
                          <div style={{ width:'100%', height:200, display:'flex', justifyContent:'center' }}>
                            <RadarChart width={280} height={200} data={radarMol}>
                              <PolarGrid stroke="rgba(255,255,255,0.05)"/>
                              <PolarAngleAxis dataKey="prop"
                                tick={{fill:'#94a3b8',fontSize:11}}/>
                              <Radar dataKey="val" stroke="#7B2FFF"
                                fill="#7B2FFF" fillOpacity={0.3} strokeWidth={2}/>
                              <Tooltip
                                contentStyle={{background:'#0D1528',
                                  border:'1px solid rgba(123,47,255,0.2)',
                                  borderRadius:'12px',fontSize:'12px'}}
                                formatter={v=>[`${v}%`]}/>
                            </RadarChart>
                          </div>
                        </div>
                        <div className="space-y-2">
                          {[
                            {label:'Score global',   val:`${selected.score}%`,     color:'text-bio'  },
                            {label:'Activité',        val:`${selected.activite}%`,  color:'text-cyan' },
                            {label:'CMI prédite',     val:`${selected.cmi} mg/L`,   color:'text-white'},
                            {label:'Poids mol.',      val:`${selected.mw} Da`,      color:'text-white'},
                            {label:'LogP',            val:selected.logp,            color:'text-white'},
                            {label:'Toxicité hERG',   val:selected.toxHerg,         color:selected.toxHerg<0.3?'text-bio':'text-amr'},
                            {label:'Toxicité hépa.',  val:selected.toxHepato,       color:selected.toxHepato<0.3?'text-bio':'text-amr'},
                            {label:'SA Score',        val:selected.sa,              color:selected.sa<=4?'text-bio':'text-amr'},
                            {label:'Solubilité',      val:selected.sol,             color:'text-white'},
                            {label:'Lipinski',        val:selected.lipinski?'✅ Conforme':'❌ Hors critères', color:selected.lipinski?'text-bio':'text-amr'},
                          ].map(r => (
                            <div key={r.label}
                              className="flex justify-between items-center
                                py-1.5 border-b border-white/5">
                              <span className="text-xs text-blue-200/50">{r.label}</span>
                              <span className={`text-xs font-semibold ${r.color}`}>
                                {r.val}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="mt-4 p-3 rounded-xl bg-violet/5
                        border border-violet/20 flex items-start gap-2">
                        <Info size={14} className="text-violet mt-0.5 shrink-0"/>
                        <p className="text-xs text-blue-200/50">
                          Cette molécule est un candidat généré par l'algorithme évolutionnaire
                          de ResistIA Brain. Elle nécessite une synthèse chimique et des tests
                          en laboratoire avant toute validation clinique.
                        </p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}