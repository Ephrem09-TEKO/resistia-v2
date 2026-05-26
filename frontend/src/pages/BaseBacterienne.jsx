import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, FlaskConical, Dna, Shield, AlertTriangle, ChevronDown } from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis,
         Radar, ResponsiveContainer, Tooltip } from 'recharts'

const BACTERIES = {
  'Escherichia coli': {
    gram:'Gram-négatif', categorie:'GRAM_NEG', who:'HIGH', eskape:false,
    morphologie:'Bacille', aerobiose:'Facultatif',
    genes:['blaTEM','blaCTX-M','blaOXA','qnrA'],
    mecanismes:['Production ESBL','Résistance fluoroquinolones','Pompe à efflux'],
    resistances:{
      'Ampicilline':55,'Ceftriaxone':25,'Imipénem':4,
      'Ciprofloxacine':38,'Gentamicine':28,'TMP-SMX':52,
      'Nitrofurantoïne':8,'Colistine':2,
    },
    description:"E. coli est la bactérie la plus fréquente en pathologie infectieuse humaine. Responsable de 80% des infections urinaires, elle développe des résistances préoccupantes via les ESBL, rendant inefficaces la plupart des céphalosporines.",
  },
  'Klebsiella pneumoniae': {
    gram:'Gram-négatif', categorie:'GRAM_NEG', who:'CRITICAL', eskape:true,
    morphologie:'Bacille', aerobiose:'Facultatif',
    genes:['blaKPC','blaNDM','blaOXA-48','blaCTX-M'],
    mecanismes:['Carbapénémase KPC','Métallo-bêta-lactamase NDM','Production ESBL'],
    resistances:{
      'Ampicilline':95,'Ceftriaxone':38,'Imipénem':18,
      'Ciprofloxacine':42,'Gentamicine':32,'TMP-SMX':58,
      'Tigécycline':6,'Colistine':4,
    },
    description:"K. pneumoniae est classée PRIORITÉ CRITIQUE par l'OMS. Ses carbapénémases (KPC, NDM) la rendent résistante à presque tous les antibiotiques disponibles. Elle est responsable de nombreuses épidémies nosocomiales, particulièrement en réanimation.",
  },
  'Staphylococcus aureus': {
    gram:'Gram-positif', categorie:'GRAM_POS', who:'HIGH', eskape:true,
    morphologie:'Coque en grappe', aerobiose:'Facultatif',
    genes:['mecA','mecC','vanA'],
    mecanismes:['PBP2a — résistance méticilline (SARM)','Glycopeptide resistance (VRSA)'],
    resistances:{
      'Oxacilline':28,'Vancomycine':2,'Linézolide':1,
      'Daptomycine':1,'Clindamycine':30,'TMP-SMX':18,
      'Ciprofloxacine':35,'Érythromycine':38,
    },
    description:"Le SARM (S. aureus Résistant à la Méticilline) est l'un des pathogènes les plus redoutés à l'hôpital. Le gène mecA confère une résistance à tous les antibiotiques bêta-lactamines. La vancomycine reste l'antibiotique de référence mais des souches VRSA émergent.",
  },
  'Pseudomonas aeruginosa': {
    gram:'Gram-négatif', categorie:'GRAM_NEG', who:'CRITICAL', eskape:true,
    morphologie:'Bacille', aerobiose:'Aérobie strict',
    genes:['blaVIM','blaIMP','blaNDM','mexAB-oprM'],
    mecanismes:['Métallo-bêta-lactamase','Surexpression pompe efflux','Perte porine OprD'],
    resistances:{
      'Pip-Tazo':22,'Ceftazidime':25,'Imipénem':28,
      'Méropénem':24,'Ciprofloxacine':30,'Amikacine':12,
      'Colistine':5,'Céfidérocol':4,
    },
    description:"P. aeruginosa est une bactérie opportuniste CRITIQUE, capable de développer simultanément tous les mécanismes de résistance connus. Elle touche particulièrement les patients immunodéprimés et ceux sous ventilation mécanique. Très difficile à traiter.",
  },
  'Candida auris': {
    gram:'Fungi', categorie:'FUNGI', who:'CRITICAL', eskape:false,
    morphologie:'Levure', aerobiose:'Facultatif',
    genes:['ERG11','FKS1','FKS2'],
    mecanismes:['Résistance azolés via ERG11','Résistance échinocandines','Résistance multiple simultanée'],
    resistances:{
      'Fluconazole':90,'Voriconazole':25,'Caspofongine':8,
      'Micafongine':6,'Ampho. B':5,'Anidulafongine':7,
    },
    description:"Candida auris est un champignon émergent découvert en 2009, désormais classé PRIORITÉ CRITIQUE par l'OMS. Résistant naturellement au fluconazole dans 90% des cas, il peut développer des résistances à toutes les classes d'antifongiques. Sa persistance sur les surfaces hospitalières en fait un agent épidémique redoutable.",
  },
}

const WHO_BADGE = {
  CRITICAL: 'badge-critical',
  HIGH:     'badge-high',
  MEDIUM:   'badge-ok',
}

export default function BaseBacterienne() {
  const [search, setSearch]     = useState('')
  const [selected, setSelected] = useState('Escherichia coli')
  const [onglet, setOnglet]     = useState('profil')

  const filtrees = Object.keys(BACTERIES).filter(b =>
    b.toLowerCase().includes(search.toLowerCase())
  )

  const bacterie = BACTERIES[selected]

  const radarData = bacterie
    ? Object.entries(bacterie.resistances).map(([abx, val]) => ({
        abx: abx.length > 12 ? abx.slice(0,12)+'…' : abx,
        valeur: val,
      }))
    : []

  return (
    <div className="space-y-6 pb-10">

      <motion.div initial={{opacity:0,y:-16}} animate={{opacity:1,y:0}}>
        <h2 className="text-2xl font-bold text-white mb-1">Base bactérienne</h2>
        <p className="text-blue-200/50 text-sm">
          Explorer les profils de résistance, gènes et mécanismes de 42 pathogènes.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Liste */}
        <motion.div initial={{opacity:0,x:-20}} animate={{opacity:1,x:0}}
          transition={{delay:0.1}} className="space-y-3">

          <div className="glass p-3 flex items-center gap-2 border border-cyan/10">
            <Search size={14} className="text-blue-200/40" />
            <input value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Rechercher un pathogène…"
              className="bg-transparent text-sm text-white placeholder-blue-200/30
                outline-none flex-1" />
          </div>

          <div className="space-y-1.5 max-h-[520px] overflow-y-auto pr-1">
            {filtrees.map(nom => {
              const b = BACTERIES[nom]
              return (
                <button key={nom} onClick={() => setSelected(nom)}
                  className={`w-full text-left p-3 rounded-xl border transition-all
                    ${selected === nom
                      ? 'bg-cyan/10 border-cyan/30 text-white'
                      : 'bg-white/2 border-white/5 text-blue-200/70 hover:bg-white/5'}`}>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium truncate">{nom}</span>
                    <span className={WHO_BADGE[b.who] +
                      ' px-2 py-0.5 rounded-full text-xs font-semibold shrink-0 ' +
                      (b.who==='CRITICAL'?'bg-danger/20 text-danger border border-danger/30':
                       b.who==='HIGH'?'bg-amr/20 text-amr border border-amr/30':
                       'bg-bio/20 text-bio border border-bio/30')}>
                      {b.who}
                    </span>
                  </div>
                  <p className="text-xs text-blue-200/40 mt-0.5">{b.gram}</p>
                </button>
              )
            })}
          </div>
        </motion.div>

        {/* Détail */}
        <motion.div initial={{opacity:0,x:20}} animate={{opacity:1,x:0}}
          transition={{delay:0.2}} className="lg:col-span-2 space-y-4">

          {bacterie && (
            <>
              {/* En-tête bactérie */}
              <div className="glass border border-cyan/10 p-5">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div>
                    <div className="flex items-center gap-3 mb-2 flex-wrap">
                      <h3 className="text-xl font-bold text-white italic">{selected}</h3>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-bold
                        ${bacterie.who==='CRITICAL'?'bg-danger/20 text-danger border border-danger/30':
                          bacterie.who==='HIGH'?'bg-amr/20 text-amr border border-amr/30':
                          'bg-bio/20 text-bio border border-bio/30'}`}>
                        {bacterie.who}
                      </span>
                      {bacterie.eskape && (
                        <span className="px-2 py-0.5 rounded-full text-xs font-bold
                          bg-violet/20 text-violet border border-violet/30">
                          ESKAPE
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-blue-200/60">{bacterie.description}</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 mt-4">
                  {[
                    { label:'Gram',        val:bacterie.gram },
                    { label:'Morphologie', val:bacterie.morphologie },
                    { label:'Aérobiose',   val:bacterie.aerobiose },
                  ].map(i => (
                    <div key={i.label} className="bg-white/3 rounded-xl p-3 text-center">
                      <p className="text-xs text-blue-200/40 mb-1">{i.label}</p>
                      <p className="text-sm font-semibold text-white">{i.val}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Onglets */}
              <div className="flex gap-2">
                {[
                  { id:'profil', label:'Profil résistance' },
                  { id:'genes',  label:'Gènes & mécanismes' },
                ].map(o => (
                  <button key={o.id} onClick={() => setOnglet(o.id)}
                    className={`px-4 py-2 rounded-xl text-sm font-semibold
                      transition-all border
                      ${onglet===o.id
                        ? 'bg-cyan/10 border-cyan/30 text-cyan'
                        : 'bg-white/3 border-white/8 text-blue-200/50 hover:text-white'}`}>
                    {o.label}
                  </button>
                ))}
              </div>

              <AnimatePresence mode="wait">
                {onglet === 'profil' && (
                  <motion.div key="profil"
                    initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} exit={{opacity:0}}
                    className="glass border border-cyan/10 p-5">
                    <h4 className="font-semibold text-white mb-4">
                      Taux de résistance aux antibiotiques clés
                    </h4>
                    <div style={{ width:'100%', height:260 }}>
                    <RadarChart width={500} height={260} data={radarData}
                        style={{ margin:'0 auto' }}>
                        <PolarGrid stroke="rgba(255,255,255,0.05)" />
                        <PolarAngleAxis dataKey="abx"
                          tick={{ fill:'#94a3b8', fontSize:11 }} />
                        <Radar name="Résistance" dataKey="valeur"
                          stroke="#00D4FF" fill="#00D4FF" fillOpacity={0.2}
                          strokeWidth={2} />
                        <Tooltip
                          contentStyle={{ background:'#0D1528',
                            border:'1px solid rgba(0,212,255,0.2)',
                            borderRadius:'12px', fontSize:'12px' }}
                          formatter={v => [`${v}%`,'Résistance']} />
                      </RadarChart>
                    </div>

                    <div className="space-y-2 mt-4">
                      {Object.entries(bacterie.resistances).map(([abx, val]) => (
                        <div key={abx} className="flex items-center gap-3">
                          <span className="text-sm text-blue-200/70 w-32 truncate">{abx}</span>
                          <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                            <motion.div
                              initial={{width:0}} animate={{width:`${val}%`}}
                              transition={{duration:0.8}}
                              className="h-full rounded-full"
                              style={{
                                background: val>=50?'#FF1744':val>=25?'#FF6B35':'#00E676',
                                boxShadow: `0 0 6px ${val>=50?'#FF174460':val>=25?'#FF6B3560':'#00E67660'}`
                              }} />
                          </div>
                          <span className="text-sm font-mono font-bold w-10 text-right"
                            style={{color:val>=50?'#FF1744':val>=25?'#FF6B35':'#00E676'}}>
                            {val}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}

                {onglet === 'genes' && (
                  <motion.div key="genes"
                    initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} exit={{opacity:0}}
                    className="glass border border-cyan/10 p-5 space-y-4">
                    <div>
                      <h4 className="font-semibold text-white flex items-center gap-2 mb-3">
                        <Dna size={16} className="text-violet" /> Gènes de résistance
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {bacterie.genes.map(g => (
                          <span key={g}
                            className="px-3 py-1.5 rounded-lg bg-violet/10
                              border border-violet/20 text-violet text-xs font-mono
                              font-semibold">
                            {g}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold text-white flex items-center gap-2 mb-3">
                        <Shield size={16} className="text-amr" /> Mécanismes de résistance
                      </h4>
                      <div className="space-y-2">
                        {bacterie.mecanismes.map((m, i) => (
                          <div key={i}
                            className="flex items-start gap-3 p-3 rounded-xl
                              bg-amr/5 border border-amr/10">
                            <AlertTriangle size={14} className="text-amr mt-0.5 shrink-0" />
                            <span className="text-sm text-blue-200/80">{m}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </>
          )}
        </motion.div>
      </div>
    </div>
  )
}