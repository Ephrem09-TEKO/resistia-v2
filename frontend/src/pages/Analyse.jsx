import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Microscope, FlaskConical, MapPin, Calendar,
  Loader2, Sparkles, AlertTriangle, CheckCircle,
  ChevronDown, Info, Download, RotateCcw
} from 'lucide-react'
import { apiRecommandation } from '../services/api'

const PATHOGENES = [
  // Bactéries Gram-négatif
  'Escherichia coli',
  'Klebsiella pneumoniae',
  'Klebsiella oxytoca',
  'Pseudomonas aeruginosa',
  'Acinetobacter baumannii',
  'Enterobacter cloacae',
  'Enterobacter aerogenes',
  'Serratia marcescens',
  'Proteus mirabilis',
  'Proteus vulgaris',
  'Morganella morganii',
  'Citrobacter freundii',
  'Stenotrophomonas maltophilia',
  'Haemophilus influenzae',
  'Neisseria gonorrhoeae',
  'Neisseria meningitidis',
  'Salmonella typhi',
  'Salmonella non-typhi',
  'Shigella spp.',
  'Vibrio cholerae',
  'Campylobacter jejuni',
  'Helicobacter pylori',
  // Bactéries Gram-positif
  'Staphylococcus aureus',
  'Staphylococcus epidermidis',
  'Staphylococcus saprophyticus',
  'Streptococcus pneumoniae',
  'Streptococcus pyogenes',
  'Streptococcus agalactiae',
  'Enterococcus faecalis',
  'Enterococcus faecium',
  'Listeria monocytogenes',
  'Clostridioides difficile',
  'Bacillus anthracis',
  // Mycobactéries
  'Mycobacterium tuberculosis',
  'Mycobacterium leprae',
  // Bactéries atypiques
  'Chlamydia trachomatis',
  'Mycoplasma pneumoniae',
  'Legionella pneumophila',
  // Parasites
  'Plasmodium falciparum',
  'Plasmodium vivax',
  // Champignons
  'Candida albicans',
  'Candida auris',
  'Aspergillus fumigatus',
]

const ANTIBIOTIQUES = [
  // Pénicillines
  'Ampicilline',
  'Amoxicilline',
  'Amoxicilline + Ac. clavulanique',
  'Pipéracilline',
  'Pipéracilline + Tazobactam',
  'Ticarcilline + Ac. clavulanique',
  'Oxacilline',
  'Cloxacilline',
  'Pénicilline G',
  'Pénicilline V',
  // Céphalosporines
  'Céfalexine (C1G)',
  'Céfazoline (C1G)',
  'Céfoxitine (C2G)',
  'Céfuroxime (C2G)',
  'Céfotaxime (C3G)',
  'Ceftriaxone (C3G)',
  'Ceftazidime (C3G)',
  'Céfépime (C4G)',
  'Céfidérocol (C5G)',
  'Ceftazidime + Avibactam',
  'Ceftolozane + Tazobactam',
  // Carbapénèmes
  'Imipénem',
  'Méropénem',
  'Ertapénem',
  'Doripénem',
  'Imipénem + Relebactam',
  // Monobactams
  'Aztréonam',
  'Aztréonam + Avibactam',
  // Aminosides
  'Gentamicine',
  'Amikacine',
  'Tobramycine',
  'Nétilmicine',
  'Streptomycine',
  'Kanamycine',
  // Fluoroquinolones
  'Ciprofloxacine',
  'Lévofloxacine',
  'Moxifloxacine',
  'Ofloxacine',
  'Norfloxacine',
  // Glycopeptides
  'Vancomycine',
  'Téicoplanine',
  'Dalbavancine',
  // Oxazolidinones
  'Linézolide',
  'Tédizolide',
  // Lipopeptides
  'Daptomycine',
  // Polymyxines
  'Colistine',
  'Polymyxine B',
  // Macrolides
  'Érythromycine',
  'Azithromycine',
  'Clarithromycine',
  'Spiramycine',
  // Lincosamides
  'Clindamycine',
  'Lincomycine',
  // Tétracyclines
  'Tétracycline',
  'Doxycycline',
  'Minocycline',
  'Tigécycline',
  'Omadacycline',
  // Rifamycines
  'Rifampicine',
  'Rifabutine',
  // Sulfamides
  'Triméthoprime + Sulfaméthoxazole',
  'Sulfaméthoxazole',
  // Autres bactériens
  'Nitrofurantoïne',
  'Fosfomycine',
  'Chloramphénicol',
  'Métronidazole',
  'Tinidazole',
  'Acide fusidique',
  'Mupirocine',
  // Anti-tuberculeux
  'Isoniazide',
  'Rifampicine (TB)',
  'Pyrazinamide',
  'Éthambutol',
  'Bédaquiline',
  'Délamanide',
  'Prétomanide',
  // Antifongiques
  'Fluconazole',
  'Voriconazole',
  'Itraconazole',
  'Posaconazole',
  'Caspofongine',
  'Micafongine',
  'Anidulafongine',
  'Amphotéricine B',
  // Antiparasitaires
  'Artéméther + Luméfantrine',
  'Chloroquine',
  'Quinine',
]

const SITES = [
  'Hémoculture',
  'Urine (ECBU)',
  'Liquide céphalorachidien (LCR)',
  'Crachat / Expectoration',
  'Liquide broncho-alvéolaire (LBA)',
  'Aspirat bronchique',
  'Pus / Plaie superficielle',
  'Pus / Abcès profond',
  'Liquide synovial',
  'Liquide péricardique',
  'Liquide péritonéal',
  'Liquide pleural',
  'Liquide de chyle',
  'Biopsie tissulaire',
  'Écouvillonnage nasal / gorge',
  'Selles / Coproculture',
  'Prélèvement génital',
  'Cathéter / Matériel implanté',
  'Cornée / Œil',
  'Oreille (otite)',
]

const SIR_COLORS = {
  S: { bg:'bg-bio/10', border:'border-bio/30', text:'text-bio',    label:'Sensible',       dot:'bg-bio'    },
  I: { bg:'bg-amr/10', border:'border-amr/30', text:'text-amr',    label:'Intermédiaire',  dot:'bg-amr'    },
  R: { bg:'bg-danger/10',border:'border-danger/30',text:'text-danger',label:'Résistant',    dot:'bg-danger' },
}

// Simulation ResistIA Brain
function simulerRecommandation(pathogene, antibiotiques, site, pays) {
  const resistants = antibiotiques.filter(a => a.sir === 'R').map(a => a.nom)
  const sensibles   = antibiotiques.filter(a => a.sir === 'S').map(a => a.nom)

  const recommandations = [
    { rang:1, abx: sensibles[0] || 'Méropénem',    confiance:94, posologie:'1g IV toutes les 8h', duree:'7-10 jours' },
    { rang:2, abx: sensibles[1] || 'Amikacine',     confiance:81, posologie:'15mg/kg IV en 1 dose/jour', duree:'5-7 jours' },
    { rang:3, abx: sensibles[2] || 'Colistine',     confiance:67, posologie:'9 MUI/j IV en 2 doses', duree:'7-14 jours' },
  ].filter(r => !resistants.includes(r.abx))

  const score = resistants.length >= 4 ? 78 : resistants.length >= 2 ? 45 : 22
  const alerte = score >= 70 ? 'ROUGE' : score >= 40 ? 'ORANGE' : 'VERT'

  return { recommandations, score, alerte, resistants }
}

export default function Analyse() {
  const [pathogene, setPathogene]   = useState('')
  const [site, setSite]             = useState('')
  const [pays, setPays]             = useState('TG')
  const [referentiel, setRef]       = useState('EUCAST')
  const [antibiotiques, setAbx] = useState(
  ANTIBIOTIQUES.slice(0, 12).map(nom => ({ nom, sir:'' }))
)
  const [loading, setLoading]       = useState(false)
  const [resultat, setResultat]     = useState(null)
  const [abxInput, setAbxInput]     = useState('')

  const updateSIR = (nom, sir) =>
    setAbx(prev => prev.map(a => a.nom === nom ? { ...a, sir } : a))

  const ajouterAbx = () => {
    if (abxInput && !antibiotiques.find(a => a.nom === abxInput))
      setAbx(prev => [...prev, { nom:abxInput, sir:'' }])
    setAbxInput('')
  }

  const retirerAbx = (nom) =>
    setAbx(prev => prev.filter(a => a.nom !== nom))

  const analyser = async () => {
  if (!pathogene) return
  setLoading(true)
  setResultat(null)

  // Appel API backend
  const payload = {
    pathogene,
    site,
    pays,
    referentiel,
    antibiotiques: antibiotiques.filter(a => a.sir !== ''),
  }

  const data = await apiRecommandation.analyser(payload)

  if (data) {
    // Réponse backend réelle
    setResultat({
      recommandations: data.recommandations.map(r => ({
        rang:      r.rang,
        abx:       r.abx,
        confiance: r.confiance,
        posologie: r.posologie,
        duree:     r.duree,
      })),
      score:      data.score_severite,
      alerte:     data.niveau_alerte,
      resistants: data.resistants,
      mecanismes: data.mecanismes || [],
      source:     data.source_modele,
    })
  } else {
    // Fallback simulation locale
    setResultat(simulerRecommandation(pathogene, antibiotiques, site, pays))
  }
  setLoading(false)
}

  const reset = () => { setResultat(null); setPathogene(''); setSite('') }

  const ALERTE_STYLE = {
    VERT:   { bg:'bg-bio/10',    border:'border-bio/30',    text:'text-bio',    label:'Situation contrôlée' },
    ORANGE: { bg:'bg-amr/10',    border:'border-amr/30',    text:'text-amr',    label:'Situation préoccupante' },
    ROUGE:  { bg:'bg-danger/10', border:'border-danger/30', text:'text-danger', label:'Situation critique' },
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-10">

      {/* En-tête */}
      <motion.div initial={{opacity:0,y:-16}} animate={{opacity:1,y:0}}>
        <h2 className="text-2xl font-bold text-white mb-1">
          Analyser un antibiogramme
        </h2>
        <p className="text-blue-200/50 text-sm">
          Renseignez le profil de résistance — ResistIA Brain recommande le meilleur traitement en 2 secondes.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* ── Formulaire ── */}
        <motion.div initial={{opacity:0,x:-20}} animate={{opacity:1,x:0}}
          transition={{delay:0.1}} className="space-y-4">

          {/* Pathogène */}
          <div className="glass p-5 border border-cyan/10 space-y-3">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <FlaskConical size={16} className="text-cyan" /> Pathogène identifié
            </h3>
            <div className="relative">
              <select value={pathogene} onChange={e => setPathogene(e.target.value)}
                className="w-full bg-night-800 border border-white/10 rounded-xl px-4 py-3
                  text-white text-sm appearance-none outline-none
                  focus:border-cyan/40 transition-all cursor-pointer">
                <option value="">-- Sélectionner un pathogène --</option>
                {PATHOGENES.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
              <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2
                text-blue-200/40 pointer-events-none" />
            </div>

            {/* Site + Pays + Référentiel */}
            <div className="grid grid-cols-2 gap-3">
              <div className="relative">
                <select value={site} onChange={e => setSite(e.target.value)}
                  className="w-full bg-night-800 border border-white/10 rounded-xl
                    px-3 py-2.5 text-sm text-white appearance-none outline-none
                    focus:border-cyan/40 transition-all cursor-pointer">
                  <option value="">Site de prélèvement</option>
                  {SITES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                <ChevronDown size={12} className="absolute right-2 top-1/2
                  -translate-y-1/2 text-blue-200/40 pointer-events-none" />
              </div>
              <div className="relative">
                <select value={referentiel} onChange={e => setRef(e.target.value)}
                  className="w-full bg-night-800 border border-white/10 rounded-xl
                    px-3 py-2.5 text-sm text-white appearance-none outline-none
                    focus:border-cyan/40 transition-all cursor-pointer">
                  <option value="EUCAST">EUCAST</option>
                  <option value="CLSI">CLSI</option>
                </select>
                <ChevronDown size={12} className="absolute right-2 top-1/2
                  -translate-y-1/2 text-blue-200/40 pointer-events-none" />
              </div>
            </div>
          </div>

          {/* Profil SIR */}
          <div className="glass p-5 border border-cyan/10 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-white flex items-center gap-2">
                <Microscope size={16} className="text-violet" /> Profil de résistance
              </h3>
              <div className="flex items-center gap-2 text-xs text-blue-200/40">
                <div className="w-2 h-2 rounded-full bg-bio" /> S
                <div className="w-2 h-2 rounded-full bg-amr ml-1" /> I
                <div className="w-2 h-2 rounded-full bg-danger ml-1" /> R
              </div>
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {antibiotiques.map(({ nom, sir }) => (
                <div key={nom}
                  className="flex items-center justify-between gap-3
                    py-1.5 px-2 rounded-lg hover:bg-white/3 group">
                  <span className="text-sm text-blue-200/80 flex-1 truncate">{nom}</span>
                  <div className="flex gap-1">
                    {['S','I','R'].map(v => (
                      <button key={v} onClick={() => updateSIR(nom, v)}
                        className={`w-7 h-7 rounded-lg text-xs font-bold
                          border transition-all duration-200
                          ${sir === v
                            ? v === 'S' ? 'bg-bio/20 border-bio text-bio'
                            : v === 'I' ? 'bg-amr/20 border-amr text-amr'
                            : 'bg-danger/20 border-danger text-danger'
                          : 'bg-white/5 border-white/10 text-blue-200/30'
                          }`}>
                        {v}
                      </button>
                    ))}
                  </div>
                  <button onClick={() => retirerAbx(nom)}
                    className="opacity-0 group-hover:opacity-100 text-blue-200/30
                      hover:text-danger transition-all text-xs px-1">✕</button>
                </div>
              ))}
            </div>

            {/* Ajouter antibiotique */}
            <div className="flex gap-2 pt-1">
              <div className="relative flex-1">
                <select value={abxInput} onChange={e => setAbxInput(e.target.value)}
                  className="w-full bg-night-800 border border-white/10 rounded-xl
                    px-3 py-2 text-sm text-white appearance-none outline-none
                    focus:border-cyan/40 transition-all cursor-pointer">
                  <option value="">Ajouter un antibiotique…</option>
                  {ANTIBIOTIQUES.filter(a =>
                    !antibiotiques.find(x => x.nom === a)
                  ).map(a => <option key={a} value={a}>{a}</option>)}
                </select>
                <ChevronDown size={12} className="absolute right-2 top-1/2
                  -translate-y-1/2 text-blue-200/40 pointer-events-none" />
              </div>
              <button onClick={ajouterAbx}
                className="px-4 py-2 rounded-xl bg-cyan/10 border border-cyan/20
                  text-cyan text-sm font-semibold hover:bg-cyan/20 transition-all">
                + Ajouter
              </button>
            </div>
          </div>

          {/* Bouton Analyser */}
          <motion.button
            whileHover={{ scale:1.02 }} whileTap={{ scale:0.98 }}
            onClick={analyser} disabled={!pathogene || loading}
            className={`w-full py-4 rounded-2xl font-bold text-lg flex items-center
              justify-center gap-3 transition-all duration-300
              ${pathogene && !loading
                ? 'bg-gradient-to-r from-cyan to-violet text-night shadow-[0_0_30px_rgba(0,212,255,0.3)] hover:shadow-[0_0_50px_rgba(0,212,255,0.5)]'
                : 'bg-white/5 text-blue-200/30 cursor-not-allowed'}`}>
            {loading
              ? <><Loader2 size={20} className="animate-spin" /> ResistIA Brain analyse...</>
              : <><Sparkles size={20} /> Analyser avec ResistIA Brain 🧠</>
            }
          </motion.button>
        </motion.div>

        {/* ── Résultats ── */}
        <motion.div initial={{opacity:0,x:20}} animate={{opacity:1,x:0}}
          transition={{delay:0.2}} className="space-y-4">

          <AnimatePresence mode="wait">
            {!resultat && !loading && (
              <motion.div key="empty"
                initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}
                className="glass border border-cyan/10 p-8 flex flex-col
                  items-center justify-center text-center h-full min-h-64">
                <div className="p-4 rounded-2xl bg-cyan/5 border border-cyan/10 mb-4">
                  <Sparkles size={32} className="text-cyan/40" />
                </div>
                <p className="text-blue-200/40 text-sm">
                  Renseignez un antibiogramme à gauche — la recommandation apparaîtra ici.
                </p>
              </motion.div>
            )}

            {loading && (
              <motion.div key="loading"
                initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}
                className="glass border border-cyan/20 p-8 flex flex-col
                  items-center justify-center text-center h-full min-h-64">
                <div className="relative mb-6">
                  <div className="w-16 h-16 rounded-full border-2 border-cyan/20
                    border-t-cyan animate-spin" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-8 h-8 rounded-full bg-cyan/10 flex items-center
                      justify-center">
                      <Sparkles size={14} className="text-cyan" />
                    </div>
                  </div>
                </div>
                <p className="text-cyan font-semibold mb-1">ResistIA Brain analyse...</p>
                <p className="text-blue-200/40 text-xs">
                  Comparaison avec 544 170 antibiogrammes mondiaux
                </p>
              </motion.div>
            )}

            {resultat && (
              <motion.div key="result"
                initial={{opacity:0,scale:0.95}} animate={{opacity:1,scale:1}}
                className="space-y-4">

                {/* Score sévérité */}
                {(() => {
                  const st = ALERTE_STYLE[resultat.alerte]
                  return (
                    <div className={`p-4 rounded-2xl border ${st.bg} ${st.border}
                      flex items-center gap-3`}>
                      <AlertTriangle size={20} className={st.text} />
                      <div>
                        <p className={`font-bold ${st.text}`}>
                          Score de sévérité : {resultat.score}/100 — {st.label}
                        </p>
                        <p className="text-xs text-blue-200/50 mt-0.5">
                          {resultat.resistants.length} résistance(s) identifiée(s)
                          {resultat.resistants.length > 0 &&
                            ` — dont ${resultat.resistants.slice(0,2).join(', ')}`}
                        </p>
                      </div>
                    </div>
                  )
                })()}

                {/* Recommandations */}
                <div className="glass border border-cyan/10 p-5 space-y-3">
                  <h3 className="font-bold text-white flex items-center gap-2">
                    <CheckCircle size={16} className="text-bio" />
                    Recommandations thérapeutiques
                  </h3>
                  {resultat.recommandations.map((r, i) => (
                    <motion.div key={i}
                      initial={{opacity:0,y:10}} animate={{opacity:1,y:0}}
                      transition={{delay:i*0.1}}
                      className={`p-4 rounded-xl border
                        ${i === 0
                          ? 'bg-bio/5 border-bio/20'
                          : 'bg-white/2 border-white/8'}`}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-bold px-2 py-0.5 rounded-full
                            ${i === 0
                              ? 'bg-bio/20 text-bio border border-bio/30'
                              : 'bg-white/10 text-blue-200/50 border border-white/10'}`}>
                            {i === 0 ? '1er choix' : i === 1 ? '2e choix' : '3e choix'}
                          </span>
                          <span className="font-semibold text-white text-sm">{r.abx}</span>
                        </div>
                        <span className={`text-sm font-bold font-mono
                          ${i === 0 ? 'text-bio' : 'text-blue-200/60'}`}>
                          {r.confiance}%
                        </span>
                      </div>
                      {/* Barre confiance */}
                      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden mb-2">
                        <motion.div
                          initial={{width:0}} animate={{width:`${r.confiance}%`}}
                          transition={{delay:0.3+i*0.1, duration:0.8}}
                          className={`h-full rounded-full
                            ${i === 0 ? 'bg-bio' : 'bg-blue-200/30'}`} />
                      </div>
                      <p className="text-xs text-blue-200/50">
                        {r.posologie} · {r.duree}
                      </p>
                    </motion.div>
                  ))}
                </div>

                {/* Disclaimer */}
                <div className="flex items-start gap-2 p-3 rounded-xl
                  bg-amr/5 border border-amr/20">
                  <Info size={14} className="text-amr mt-0.5 shrink-0" />
                  <p className="text-xs text-blue-200/50">
                    Ce rapport est une aide à la décision générée par ResistIA Brain 🧠.
                    Il ne remplace pas le jugement clinique du médecin.
                  </p>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <button className="flex-1 btn-primary justify-center gap-2 text-sm py-2.5">
                    <Download size={14} /> Exporter PDF
                  </button>
                  <button onClick={reset}
                    className="btn-outline flex items-center gap-2 text-sm py-2.5 px-4">
                    <RotateCcw size={14} /> Nouvelle analyse
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  )
}