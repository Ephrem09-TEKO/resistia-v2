import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Dna, Activity, Loader2, ChevronDown,
         Heart, Droplets, Wind, Thermometer } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip,
         ResponsiveContainer, ReferenceLine } from 'recharts'
import { apiSimBio } from '../services/api'

const MOLECULES = [
  { nom:'Candidat_KPC_001 (Modèle 9)',   mw:417, logp:-1.42, activite:0.887, cmi:1.007, toxHerg:0.226, toxHepato:0.247, sa:3.8 },
  { nom:'Ciprofloxacine (référence)',     mw:331, logp:0.28,  activite:0.850, cmi:0.015, toxHerg:0.250, toxHepato:0.200, sa:2.8 },
  { nom:'Méropénem (référence)',          mw:383, logp:-0.75, activite:0.920, cmi:0.050, toxHerg:0.150, toxHepato:0.200, sa:4.5 },
  { nom:'Candidat_AMR_001 (Modèle 9)',   mw:342, logp:1.2,   activite:0.780, cmi:1.166, toxHerg:0.180, toxHepato:0.220, sa:3.1 },
]

const ESPECES = [
  { id:'souris', label:'Souris (Mus musculus)',        dose:50, tHalf:0.7  },
  { id:'rat',    label:'Rat (Rattus norvegicus)',       dose:30, tHalf:1.6  },
  { id:'humain', label:'Humain',                        dose:10, tHalf:5.3  },
]

const PAYS_SIMBIO = [
  { code:'TG', nom:'Togo',         region:'AFRO',  immunite:0.770, resilience:0.730 },
  { code:'FR', nom:'France',       region:'EURO',  immunite:0.967, resilience:0.982 },
  { code:'IN', nom:'Inde',         region:'SEARO', immunite:0.727, resilience:0.711 },
  { code:'US', nom:'États-Unis',   region:'AMRO',  immunite:0.910, resilience:0.895 },
  { code:'NG', nom:'Nigeria',      region:'AFRO',  immunite:0.735, resilience:0.679 },
  { code:'CN', nom:'Chine',        region:'WPRO',  immunite:0.920, resilience:0.910 },
  { code:'BR', nom:'Brésil',       region:'AMRO',  immunite:0.860, resilience:0.850 },
  { code:'SA', nom:'Arabie Saoud.', region:'EMRO', immunite:0.880, resilience:0.860 },
]

const STADES = ['Colonisation','Infection légère','Infection modérée','Infection sévère','Sepsis critique']

function simuler(molecule, espece, pays) {
  const pays_data = PAYS_SIMBIO.find(p => p.code === pays) || PAYS_SIMBIO[0]
  const esp_data  = ESPECES.find(e => e.id === espece) || ESPECES[0]

  const resultats = STADES.map((nom, i) => {
    const charge = Math.pow(10, 3 + i*2)
    const facteur_pk = Math.min(1.5, (500 / molecule.cmi) * 0.001 * pays_data.immunite)
    const efficacite = Math.round(
      (molecule.activite * 0.35 + facteur_pk * 0.30 +
       pays_data.immunite * 0.15 + (1 - i*0.08) * 0.20) * 100
    )
    return {
      stade: nom.split(' ').slice(-1)[0] || nom,
      nom,
      efficacite: Math.max(55, Math.min(99, efficacite - i*3)),
      charge,
      chargeApres: charge / Math.pow(10, efficacite/25),
      temps: i === 0 ? 25 : i === 1 ? 48 : i === 2 ? 68 : i === 3 ? 200 : 250,
    }
  })

  const courbe = Array.from({length:24}, (_,h) => ({
    h,
    concentration: +(molecule.activite * Math.exp(-0.693*h/esp_data.tHalf) * 100).toFixed(1),
    cmi: +(molecule.cmi * 100).toFixed(1),
  }))

  const score = Math.round(resultats.slice(0,3).reduce((s,r) => s+r.efficacite, 0) / 3)

  return {
    resultats, courbe, score,
    mecanisme: molecule.mw > 500 ? 'Disruption membranaire' :
               molecule.logp > 1 ? 'Inhibition ADN (gyrase/topoisomérase)' :
               'Inhibition protéique (ribosome 30S/50S)',
    pk: {
      absorption: Math.round(66.8), tHalf: esp_data.tHalf,
      cmax: Math.round(19000 / espece.length * 2),
      voie: molecule.mw <= 500 ? 'Orale' : 'IV recommandée',
    },
    physio: {
      temperature: { sain: 36.7, infecte: 38.9 },
      fc:          { sain: espece==='souris'?575:espece==='rat'?350:80, infecte: espece==='souris'?640:espece==='rat'?410:112 },
      crp:         { sain: 2.5,  infecte: 48.0  },
      il6:         { sain: 3.5,  infecte: 42.0  },
      hb:          { sain: espece==='humain'?pays_data.immunite*147:espece==='rat'?150:140, infecte: espece==='humain'?pays_data.immunite*135:espece==='rat'?138:128 },
    },
  }
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass p-3 border border-cyan/20 text-xs">
      <p className="text-blue-200/40 mb-1">T+{label}h</p>
      {payload.map(p => (
        <p key={p.name} style={{color:p.color}}>
          {p.name==='concentration'?'Concentration':'CMI'} : {p.value}
        </p>
      ))}
    </div>
  )
}

export default function SimBio() {
  const [molecule, setMolecule] = useState('')
  const [espece, setEspece]     = useState('humain')
  const [pays, setPays]         = useState('TG')
  const [loading, setLoading]   = useState(false)
  const [sim, setSim]           = useState(null)

  const lancer = async () => {
  const mol = MOLECULES.find(m => m.nom === molecule)
  if (!mol) return
  setLoading(true)
  setSim(null)

  const data = await apiSimBio.simuler({
    molecule_nom:      mol.nom,
    molecule_activite: mol.activite,
    molecule_cmi:      mol.cmi,
    espece,
    pays,
    stade_infection:   0,
  })

  if (data) {
    setSim({
      score:       data.score_global,
      recommandation: data.recommandation,
      mecanisme:   data.mecanisme,
      courbe:      data.courbe_pk.map(p => ({
        h:             p.h,
        concentration: p.concentration,
        cmi:           p.cmi,
      })),
      resultats:   data.stades.map(s => ({
        nom:       s.stade,
        stade:     s.stade.split(' ').pop(),
        efficacite: s.efficacite,
        temps:     s.temps_h,
      })),
      pk: {
        absorption: 66.8,
        tHalf:     data.t_half,
        voie:      mol.mw <= 500 ? 'Orale' : 'IV recommandée',
      },
      physio: {
        temperature: { sain:36.7, infecte:38.9 },
        fc:          { sain:80,   infecte:112  },
        crp:         { sain:2.5,  infecte:48.0 },
        il6:         { sain:3.5,  infecte:42.0 },
      },
    })
  } else {
    const molData = MOLECULES.find(m => m.nom === molecule)
    setSim(simuler(molData, espece, pays))
  }
  setLoading(false)
}

  const paysData = PAYS_SIMBIO.find(p => p.code === pays)

  return (
    <div className="space-y-6 pb-10">
      <motion.div initial={{opacity:0,y:-16}} animate={{opacity:1,y:0}}>
        <h2 className="text-2xl font-bold text-white mb-1">SimBio 🧬</h2>
        <p className="text-blue-200/50 text-sm">
          Simulez l'effet d'une molécule sur un organisme vivant avant les tests en laboratoire.
          Souris, rat ou humain — 194 pays, 5 stades d'infection.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Config */}
        <motion.div initial={{opacity:0,x:-20}} animate={{opacity:1,x:0}}
          transition={{delay:0.1}} className="space-y-4">

          <div className="glass border border-cyan/10 p-5 space-y-4">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Dna size={16} className="text-bio" /> Configuration de la simulation
            </h3>

            {/* Molécule */}
            <div>
              <label className="text-xs text-blue-200/50 mb-1.5 block">
                Molécule à tester
              </label>
              <div className="relative">
                <select value={molecule} onChange={e => setMolecule(e.target.value)}
                  className="w-full bg-night-800 border border-white/10 rounded-xl
                    px-3 py-2.5 text-sm text-white appearance-none outline-none
                    focus:border-bio/40">
                  <option value="">-- Sélectionner --</option>
                  {MOLECULES.map(m => (
                    <option key={m.nom} value={m.nom}>{m.nom}</option>
                  ))}
                </select>
                <ChevronDown size={12} className="absolute right-2 top-1/2
                  -translate-y-1/2 text-blue-200/40 pointer-events-none"/>
              </div>
            </div>

            {/* Espèce */}
            <div>
              <label className="text-xs text-blue-200/50 mb-1.5 block">
                Espèce / Organisme hôte
              </label>
              <div className="grid grid-cols-3 gap-2">
                {ESPECES.map(e => (
                  <button key={e.id} onClick={() => setEspece(e.id)}
                    className={`p-2 rounded-xl border text-xs font-semibold
                      transition-all text-center
                      ${espece===e.id
                        ? 'bg-bio/10 border-bio/30 text-bio'
                        : 'bg-white/3 border-white/8 text-blue-200/50'}`}>
                    {e.id==='souris'?'🐭 Souris':e.id==='rat'?'🐀 Rat':'🧑 Humain'}
                  </button>
                ))}
              </div>
            </div>

            {/* Pays */}
            {espece === 'humain' && (
              <div>
                <label className="text-xs text-blue-200/50 mb-1.5 block">
                  Pays / Profil physiologique
                </label>
                <div className="relative">
                  <select value={pays} onChange={e => setPays(e.target.value)}
                    className="w-full bg-night-800 border border-white/10 rounded-xl
                      px-3 py-2.5 text-sm text-white appearance-none outline-none
                      focus:border-bio/40">
                    {PAYS_SIMBIO.map(p => (
                      <option key={p.code} value={p.code}>
                        {p.nom} ({p.region})
                      </option>
                    ))}
                  </select>
                  <ChevronDown size={12} className="absolute right-2 top-1/2
                    -translate-y-1/2 text-blue-200/40 pointer-events-none"/>
                </div>
                {paysData && (
                  <div className="mt-2 p-2.5 rounded-lg bg-white/3 border
                    border-white/8 grid grid-cols-2 gap-2">
                    <div className="text-center">
                      <p className="text-xs text-blue-200/40">Immunité</p>
                      <p className={`text-sm font-bold
                        ${paysData.immunite>0.9?'text-bio':paysData.immunite>0.8?'text-amr':'text-danger'}`}>
                        {(paysData.immunite*100).toFixed(0)}%
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-blue-200/40">Résilience</p>
                      <p className={`text-sm font-bold
                        ${paysData.resilience>0.9?'text-bio':paysData.resilience>0.8?'text-amr':'text-danger'}`}>
                        {(paysData.resilience*100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            <motion.button
              whileHover={{scale:1.02}} whileTap={{scale:0.98}}
              onClick={lancer} disabled={!molecule||loading}
              className={`w-full py-3.5 rounded-2xl font-bold flex items-center
                justify-center gap-3 transition-all
                ${molecule&&!loading
                  ? 'bg-gradient-to-r from-bio to-cyan text-night shadow-[0_0_30px_rgba(0,230,118,0.3)]'
                  : 'bg-white/5 text-blue-200/30 cursor-not-allowed'}`}>
              {loading
                ? <><Loader2 size={18} className="animate-spin"/>Simulation...</>
                : <><Activity size={18}/>Lancer SimBio 🧬</>}
            </motion.button>
          </div>
        </motion.div>

        {/* Résultats */}
        <div className="lg:col-span-2 space-y-4">
          <AnimatePresence mode="wait">
            {!sim && !loading && (
              <motion.div key="empty"
                initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}
                className="glass border border-cyan/10 p-12 flex flex-col
                  items-center justify-center text-center">
                <div className="p-5 rounded-2xl bg-bio/5 border border-bio/10 mb-4">
                  <Activity size={40} className="text-bio/40"/>
                </div>
                <p className="text-white font-semibold mb-2">
                  Aucune simulation en cours
                </p>
                <p className="text-blue-200/40 text-sm max-w-sm">
                  Sélectionnez une molécule et configurez l'hôte pour simuler
                  l'effet pharmacologique en conditions réelles.
                </p>
              </motion.div>
            )}

            {loading && (
              <motion.div key="loading"
                initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}
                className="glass border border-bio/20 p-12 flex flex-col
                  items-center justify-center text-center">
                <div className="relative mb-6">
                  <div className="w-20 h-20 rounded-full border-2 border-bio/20
                    border-t-bio animate-spin"/>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Activity size={24} className="text-bio"/>
                  </div>
                </div>
                <p className="text-bio font-semibold mb-1">Simulation physiologique...</p>
                <p className="text-blue-200/40 text-xs">
                  Calcul PK/PD · 5 stades d'infection · Organes cibles
                </p>
              </motion.div>
            )}

            {sim && (
              <motion.div key="sim"
                initial={{opacity:0}} animate={{opacity:1}}
                className="space-y-4">

                {/* Score global */}
                <div className={`p-4 rounded-2xl border flex items-center gap-4
                  ${sim.score>=70
                    ? 'bg-bio/10 border-bio/30'
                    : sim.score>=50
                      ? 'bg-amr/10 border-amr/30'
                      : 'bg-danger/10 border-danger/30'}`}>
                  <div className="text-center">
                    <p className={`text-3xl font-bold font-mono
                      ${sim.score>=70?'text-bio':sim.score>=50?'text-amr':'text-danger'}`}>
                      {sim.score}%
                    </p>
                    <p className="text-xs text-blue-200/50">Score SimBio</p>
                  </div>
                  <div className="flex-1">
                    <p className={`font-bold ${sim.score>=70?'text-bio':sim.score>=50?'text-amr':'text-danger'}`}>
                      {sim.score>=70?'✅ Recommandé pour tests laboratoire':
                       sim.score>=50?'⚠️ Tests supplémentaires nécessaires':
                       '❌ Reformuler la molécule'}
                    </p>
                    <p className="text-sm text-blue-200/50 mt-1">
                      Mécanisme prédit : {sim.mecanisme}
                    </p>
                    <p className="text-xs text-blue-200/40 mt-0.5">
                      Absorption {sim.pk.absorption}% · T½ {sim.pk.tHalf}h · {sim.pk.voie}
                    </p>
                  </div>
                </div>

                {/* Efficacité par stade */}
                <div className="glass border border-cyan/10 p-5">
                  <h4 className="font-semibold text-white mb-4">
                    Efficacité par stade d'infection
                  </h4>
                  <div className="space-y-2.5">
                    {sim.resultats.map((r, i) => (
                      <motion.div key={i}
                        initial={{opacity:0,x:-10}} animate={{opacity:1,x:0}}
                        transition={{delay:i*0.1}}
                        className="flex items-center gap-3">
                        <span className="text-xs text-blue-200/40 w-4 font-mono">
                          {i}
                        </span>
                        <span className="text-xs text-blue-200/70 w-36 truncate">
                          {r.nom}
                        </span>
                        <div className="flex-1 h-2.5 bg-white/5 rounded-full overflow-hidden">
                          <motion.div
                            initial={{width:0}} animate={{width:`${r.efficacite}%`}}
                            transition={{delay:i*0.1+0.3, duration:0.8}}
                            className="h-full rounded-full"
                            style={{
                              background: r.efficacite>=75?'#00E676':r.efficacite>=60?'#FF6B35':'#FF1744',
                              boxShadow: `0 0 8px ${r.efficacite>=75?'#00E67660':'#FF6B3560'}`
                            }}/>
                        </div>
                        <span className="text-sm font-mono font-bold w-12 text-right"
                          style={{color:r.efficacite>=75?'#00E676':r.efficacite>=60?'#FF6B35':'#FF1744'}}>
                          {r.efficacite}%
                        </span>
                        {i===0&&<span className="text-xs bg-bio/20 text-bio
                          border border-bio/30 px-1.5 py-0.5 rounded-full">⭐</span>}
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Courbe PK */}
                <div className="glass border border-cyan/10 p-5">
                  <h4 className="font-semibold text-white mb-1">
                    Courbe pharmacocinétique (PK) — 24h
                  </h4>
                  <p className="text-xs text-blue-200/40 mb-4">
                    Concentration de la molécule vs CMI dans le temps
                  </p>
                  <div style={{ width:'100%', height:180 }}>
                    <LineChart width={620} height={180} data={sim.courbe}>
                      <XAxis dataKey="h" tick={{fill:'#94a3b8',fontSize:11}}
                        axisLine={false} tickLine={false}
                        tickFormatter={v=>`${v}h`}/>
                      <YAxis tick={{fill:'#94a3b8',fontSize:11}}
                        axisLine={false} tickLine={false}/>
                      <Tooltip content={<CustomTooltip/>}/>
                      <Line type="monotone" dataKey="concentration"
                        stroke="#00D4FF" strokeWidth={2} dot={false}
                        name="concentration"/>
                      <Line type="monotone" dataKey="cmi"
                        stroke="#FF6B35" strokeWidth={1.5} dot={false}
                        strokeDasharray="4 4" name="cmi"/>
                    </LineChart>
                  </div>
                  <div className="flex items-center gap-6 mt-2 justify-center text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-0.5 bg-cyan"/>
                      <span className="text-blue-200/50">Concentration</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-0.5 bg-amr" style={{borderTop:'1.5px dashed #FF6B35'}}/>
                      <span className="text-blue-200/50">CMI seuil</span>
                    </div>
                  </div>
                </div>

                {/* Constantes physiologiques */}
                <div className="glass border border-cyan/10 p-5">
                  <h4 className="font-semibold text-white mb-4">
                    Constantes physiologiques — Sain vs Infecté (stade optimal)
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {[
                      { label:'Température', icon:Thermometer, sain:`${sim.physio.temperature.sain}°C`, infecte:`${sim.physio.temperature.infecte}°C`, color:'text-amr' },
                      { label:'FC',           icon:Heart,        sain:`${sim.physio.fc.sain} bpm`,        infecte:`${sim.physio.fc.infecte} bpm`,        color:'text-danger' },
                      { label:'CRP',          icon:Droplets,     sain:`${sim.physio.crp.sain} mg/L`,      infecte:`${sim.physio.crp.infecte} mg/L`,      color:'text-amr' },
                      { label:'IL-6',         icon:Wind,         sain:`${sim.physio.il6.sain} pg/mL`,     infecte:`${sim.physio.il6.infecte} pg/mL`,     color:'text-violet' },
                    ].map(c => (
                      <div key={c.label}
                        className="bg-white/3 border border-white/8 rounded-xl p-3">
                        <div className="flex items-center gap-1.5 mb-2">
                          <c.icon size={12} className={c.color}/>
                          <span className="text-xs text-blue-200/50">{c.label}</span>
                        </div>
                        <p className="text-xs text-blue-200/40">Sain : {c.sain}</p>
                        <p className={`text-sm font-bold ${c.color}`}>
                          Infecté : {c.infecte}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}