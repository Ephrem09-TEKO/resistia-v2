import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Globe2, TrendingUp, AlertTriangle, MapPin, Activity } from 'lucide-react'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'

const REGIONS = [
  { region:'AFRO',  taux:38, pays:47,  couleur:'#FF1744', label:'Afrique'               },
  { region:'EMRO',  taux:35, pays:21,  couleur:'#FF6B35', label:'Méditerranée orientale' },
  { region:'SEARO', taux:34, pays:11,  couleur:'#FF6B35', label:'Asie du Sud-Est'        },
  { region:'AMRO',  taux:28, pays:35,  couleur:'#FFB300', label:'Amériques'              },
  { region:'WPRO',  taux:26, pays:27,  couleur:'#7B2FFF', label:'Pacifique occidental'   },
  { region:'EURO',  taux:23, pays:53,  couleur:'#00E676', label:'Europe'                 },
]

const COUNTRY_TO_REGION = {
  // ── AFRO (47 pays) ──────────────────────────────────
  12:'AFRO',   // Algérie
  24:'AFRO',   // Angola
  204:'AFRO',  // Bénin
  72:'AFRO',   // Botswana
  854:'AFRO',  // Burkina Faso
  108:'AFRO',  // Burundi
  132:'AFRO',  // Cap-Vert
  120:'AFRO',  // Cameroun
  140:'AFRO',  // Centrafrique
  148:'AFRO',  // Tchad
  174:'AFRO',  // Comores
  178:'AFRO',  // Congo
  180:'AFRO',  // RD Congo
  384:'AFRO',  // Côte d'Ivoire
  226:'AFRO',  // Guinée équatoriale
  232:'AFRO',  // Érythrée
  748:'AFRO',  // Eswatini
  231:'AFRO',  // Éthiopie
  266:'AFRO',  // Gabon
  270:'AFRO',  // Gambie
  288:'AFRO',  // Ghana
  324:'AFRO',  // Guinée
  624:'AFRO',  // Guinée-Bissau
  404:'AFRO',  // Kenya
  426:'AFRO',  // Lesotho
  430:'AFRO',  // Liberia
  450:'AFRO',  // Madagascar
  454:'AFRO',  // Malawi
  466:'AFRO',  // Mali
  478:'AFRO',  // Mauritanie
  480:'AFRO',  // Maurice
  508:'AFRO',  // Mozambique
  516:'AFRO',  // Namibie
  562:'AFRO',  // Niger
  566:'AFRO',  // Nigeria
  646:'AFRO',  // Rwanda
  678:'AFRO',  // Sao Tomé-et-Príncipe
  686:'AFRO',  // Sénégal
  690:'AFRO',  // Seychelles
  694:'AFRO',  // Sierra Leone
  710:'AFRO',  // Afrique du Sud
  728:'AFRO',  // Soudan du Sud
  834:'AFRO',  // Tanzanie
  768:'AFRO',  // Togo
  800:'AFRO',  // Ouganda
  894:'AFRO',  // Zambie
  716:'AFRO',  // Zimbabwe
  // ── EMRO (21 pays) ──────────────────────────────────
  4:'EMRO',    // Afghanistan
  48:'EMRO',   // Bahreïn
  262:'EMRO',  // Djibouti
  818:'EMRO',  // Égypte
  364:'EMRO',  // Iran
  368:'EMRO',  // Irak
  400:'EMRO',  // Jordanie
  414:'EMRO',  // Koweït
  422:'EMRO',  // Liban
  434:'EMRO',  // Libye
  504:'EMRO',  // Maroc
  512:'EMRO',  // Oman
  586:'EMRO',  // Pakistan
  275:'EMRO',  // Palestine
  634:'EMRO',  // Qatar
  682:'EMRO',  // Arabie saoudite
  706:'EMRO',  // Somalie
  729:'EMRO',  // Soudan
  760:'EMRO',  // Syrie
  788:'EMRO',  // Tunisie
  784:'EMRO',  // Émirats arabes unis
  887:'EMRO',  // Yémen
  // ── EURO (53 pays) ──────────────────────────────────
  8:'EURO',    // Albanie
  20:'EURO',   // Andorre
  51:'EURO',   // Arménie
  40:'EURO',   // Autriche
  31:'EURO',   // Azerbaïdjan
  112:'EURO',  // Biélorussie
  56:'EURO',   // Belgique
  70:'EURO',   // Bosnie-Herzégovine
  100:'EURO',  // Bulgarie
  191:'EURO',  // Croatie
  196:'EURO',  // Chypre
  203:'EURO',  // Tchéquie
  208:'EURO',  // Danemark
  233:'EURO',  // Estonie
  246:'EURO',  // Finlande
  250:'EURO',  // France
  268:'EURO',  // Géorgie
  276:'EURO',  // Allemagne
  300:'EURO',  // Grèce
  304:'EURO',  // Groenland (territoire du Danemark)
  348:'EURO',  // Hongrie
  352:'EURO',  // Islande
  372:'EURO',  // Irlande
  376:'EURO',  // Israël
  380:'EURO',  // Italie
  398:'EURO',  // Kazakhstan
  417:'EURO',  // Kirghizistan
  428:'EURO',  // Lettonie
  440:'EURO',  // Lituanie
  442:'EURO',  // Luxembourg
  470:'EURO',  // Malte
  498:'EURO',  // Moldavie
  492:'EURO',  // Monaco
  499:'EURO',  // Monténégro
  528:'EURO',  // Pays-Bas
  807:'EURO',  // Macédoine du Nord
  578:'EURO',  // Norvège
  616:'EURO',  // Pologne
  620:'EURO',  // Portugal
  642:'EURO',  // Roumanie
  643:'EURO',  // Russie
  674:'EURO',  // Saint-Marin
  688:'EURO',  // Serbie
  703:'EURO',  // Slovaquie
  705:'EURO',  // Slovénie
  724:'EURO',  // Espagne
  752:'EURO',  // Suède
  756:'EURO',  // Suisse
  762:'EURO',  // Tadjikistan
  795:'EURO',  // Turkménistan
  792:'EURO',  // Turquie
  804:'EURO',  // Ukraine
  826:'EURO',  // Royaume-Uni
  860:'EURO',  // Ouzbékistan
  // ── SEARO (11 pays) ─────────────────────────────────
  50:'SEARO',  // Bangladesh
  64:'SEARO',  // Bhoutan
  408:'SEARO', // Corée du Nord
  356:'SEARO', // Inde
  360:'SEARO', // Indonésie
  462:'SEARO', // Maldives
  104:'SEARO', // Myanmar
  524:'SEARO', // Népal
  144:'SEARO', // Sri Lanka
  764:'SEARO', // Thaïlande
  626:'SEARO', // Timor oriental
  // ── AMRO (35 pays) ──────────────────────────────────
  28:'AMRO',   // Antigua-et-Barbuda
  32:'AMRO',   // Argentine
  44:'AMRO',   // Bahamas
  52:'AMRO',   // Barbade
  84:'AMRO',   // Belize
  68:'AMRO',   // Bolivie
  76:'AMRO',   // Brésil
  124:'AMRO',  // Canada
  152:'AMRO',  // Chili
  170:'AMRO',  // Colombie
  188:'AMRO',  // Costa Rica
  192:'AMRO',  // Cuba
  212:'AMRO',  // Dominique
  214:'AMRO',  // Rép. Dominicaine
  218:'AMRO',  // Équateur
  222:'AMRO',  // Salvador
  308:'AMRO',  // Grenade
  320:'AMRO',  // Guatemala
  328:'AMRO',  // Guyana
  254:'AMRO',  // Guyane française (territoire de France)
  332:'AMRO',  // Haïti
  340:'AMRO',  // Honduras
  388:'AMRO',  // Jamaïque
  484:'AMRO',  // Mexique
  558:'AMRO',  // Nicaragua
  591:'AMRO',  // Panama
  600:'AMRO',  // Paraguay
  604:'AMRO',  // Pérou
  659:'AMRO',  // Saint-Kitts-et-Nevis
  662:'AMRO',  // Sainte-Lucie
  670:'AMRO',  // Saint-Vincent
  740:'AMRO',  // Suriname
  780:'AMRO',  // Trinité-et-Tobago
  840:'AMRO',  // États-Unis
  858:'AMRO',  // Uruguay
  862:'AMRO',  // Venezuela
  // ── WPRO (27 pays) ──────────────────────────────────
  36:'WPRO',   // Australie
  96:'WPRO',   // Brunei
  116:'WPRO',  // Cambodge
  156:'WPRO',  // Chine
  242:'WPRO',  // Fidji
  392:'WPRO',  // Japon
  296:'WPRO',  // Kiribati
  418:'WPRO',  // Laos
  458:'WPRO',  // Malaisie
  584:'WPRO',  // Îles Marshall
  583:'WPRO',  // Micronésie
  496:'WPRO',  // Mongolie
  520:'WPRO',  // Nauru
  554:'WPRO',  // Nouvelle-Zélande
  585:'WPRO',  // Palaos
  598:'WPRO',  // Papouasie-Nouvelle-Guinée
  608:'WPRO',  // Philippines
  882:'WPRO',  // Samoa
  90:'WPRO',   // Îles Salomon
  410:'WPRO',  // Corée du Sud
  702:'WPRO',  // Singapour
  158:'WPRO',  // Taïwan
  776:'WPRO',  // Tonga
  798:'WPRO',  // Tuvalu
  548:'WPRO',  // Vanuatu
  704:'WPRO',  // Vietnam
  184:'WPRO',  // Îles Cook
}

const TOP_PAYS = [
  { pays:'Grèce',     taux:52, region:'EURO',  flag:'🇬🇷' },
  { pays:'Inde',      taux:48, region:'SEARO', flag:'🇮🇳' },
  { pays:'Nigeria',   taux:46, region:'AFRO',  flag:'🇳🇬' },
  { pays:'Pakistan',  taux:45, region:'EMRO',  flag:'🇵🇰' },
  { pays:'Brésil',    taux:41, region:'AMRO',  flag:'🇧🇷' },
  { pays:'Togo',      taux:38, region:'AFRO',  flag:'🇹🇬' },
  { pays:'Indonésie', taux:37, region:'SEARO', flag:'🇮🇩' },
  { pays:'Irak',      taux:36, region:'EMRO',  flag:'🇮🇶' },
]

const PATHOGENES = [
  { pathogene:'E. coli',       AFRO:38, EURO:18, SEARO:42, AMRO:28, EMRO:35, WPRO:22 },
  { pathogene:'K. pneumoniae', AFRO:42, EURO:22, SEARO:38, AMRO:32, EMRO:40, WPRO:28 },
  { pathogene:'S. aureus',     AFRO:28, EURO:15, SEARO:32, AMRO:25, EMRO:30, WPRO:18 },
  { pathogene:'P. aeruginosa', AFRO:30, EURO:20, SEARO:35, AMRO:28, EMRO:32, WPRO:24 },
]

const ALERTES = [
  { pays:'Grèce',    region:'EURO',  pathogene:'K. pneumoniae KPC', niveau:'ROUGE',  taux:52 },
  { pays:'Inde',     region:'SEARO', pathogene:'Candida auris',     niveau:'ROUGE',  taux:91 },
  { pays:'Nigeria',  region:'AFRO',  pathogene:'E. coli MCR+',      niveau:'ORANGE', taux:46 },
  { pays:'Pakistan', region:'EMRO',  pathogene:'A. baumannii XDR',  niveau:'ROUGE',  taux:58 },
  { pays:'Togo',     region:'AFRO',  pathogene:'E. coli ESBL',      niveau:'ORANGE', taux:38 },
  { pays:'Brésil',   region:'AMRO',  pathogene:'S. aureus SARM',    niveau:'ORANGE', taux:28 },
]

const STATS_GLOBALES = [
  { label:'Pays surveillés',        val:'194',       color:'#00D4FF' },
  { label:'Régions OMS',            val:'6',         color:'#7B2FFF' },
  { label:'Antibiogrammes analysés',val:'1 088 340', color:'#00E676' },
  { label:'Taux résistance moyen',  val:'32.4%',     color:'#FF6B35' },
]

function getColor(taux) {
  if (taux >= 50) return '#FF1744'
  if (taux >= 35) return '#FF6B35'
  if (taux >= 20) return '#FFB300'
  return '#00E676'
}

function CarteD3({ regionSel, onRegionClick }) {
  const containerRef = useRef(null)
  const svgRef       = useRef(null)
  const [tooltip, setTooltip] = useState(null)
  const [status, setStatus]   = useState('loading')

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return

    const container = containerRef.current
    const W = container.clientWidth  || 800
    const H = container.clientHeight || 380

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()
    svg.attr('width', W).attr('height', H)

    svg.append('rect')
      .attr('width', W).attr('height', H)
      .attr('fill', '#0A0F1E')

    const projection = d3.geoNaturalEarth1()
      .scale(W / 6.3)
      .translate([W / 2, H / 2 + 20])

    const pathGen = d3.geoPath().projection(projection)

    const graticule = d3.geoGraticule().step([30, 30])
    svg.append('path')
      .datum(graticule())
      .attr('d', pathGen)
      .attr('fill', 'none')
      .attr('stroke', 'rgba(0,212,255,0.05)')
      .attr('stroke-width', 0.5)

    d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
      .then(world => {
        const countries = topojson.feature(world, world.objects.countries)

        svg.selectAll('path.country')
          .data(countries.features)
          .join('path')
          .attr('class', 'country')
          .attr('d', pathGen)
          .attr('fill', d => {
            const reg = COUNTRY_TO_REGION[+d.id]
            if (!reg) return '#0D1528'
            const r = REGIONS.find(x => x.region === reg)
            if (!r) return '#0D1528'
            if (regionSel && regionSel !== reg) return r.couleur + '33'
            return r.couleur + '99'
          })
          .attr('stroke', '#1B3A6B88')
          .attr('stroke-width', 0.4)
          .style('cursor', d => {
            const reg = COUNTRY_TO_REGION[+d.id]
            return reg ? 'pointer' : 'default'
          })
          .style('transition', 'fill 0.3s')
          .on('mouseover', function(event, d) {
            const reg = COUNTRY_TO_REGION[+d.id]
            if (!reg) return
            const r = REGIONS.find(x => x.region === reg)
            d3.select(this)
              .attr('stroke', r?.couleur || '#00D4FF')
              .attr('stroke-width', 1.2)
            const rect = container.getBoundingClientRect()
            setTooltip({
              x: event.clientX - rect.left,
              y: event.clientY - rect.top,
              region: r?.region,
              label:  r?.label,
              taux:   r?.taux,
              color:  r?.couleur,
            })
          })
          .on('mousemove', function(event) {
            const rect = container.getBoundingClientRect()
            setTooltip(prev => prev
              ? { ...prev, x: event.clientX - rect.left, y: event.clientY - rect.top }
              : null
            )
          })
          .on('mouseout', function(event, d) {
            const reg = COUNTRY_TO_REGION[+d.id]
            if (!reg) return
            d3.select(this)
              .attr('stroke', '#1B3A6B88')
              .attr('stroke-width', 0.4)
            setTooltip(null)
          })
          .on('click', (event, d) => {
            const reg = COUNTRY_TO_REGION[+d.id]
            if (reg) onRegionClick(reg)
          })

        setStatus('ready')
      })
      .catch(() => setStatus('error'))
  }, [regionSel])

  return (
    <div ref={containerRef}
      style={{ position:'relative', width:'100%', height:'100%' }}>
      <svg ref={svgRef}
        style={{ width:'100%', height:'100%', display:'block' }} />

      {status === 'loading' && (
        <div style={{
          position:'absolute', inset:0,
          display:'flex', flexDirection:'column',
          alignItems:'center', justifyContent:'center', gap:12,
        }}>
          <style>{`
            @keyframes spin { to { transform:rotate(360deg) } }
          `}</style>
          <div style={{
            width:40, height:40, borderRadius:'50%',
            border:'2px solid rgba(0,212,255,0.15)',
            borderTopColor:'#00D4FF',
            animation:'spin 1s linear infinite',
          }} />
          <p style={{ color:'rgba(148,163,184,0.5)', fontSize:13 }}>
            Chargement de la carte mondiale...
          </p>
        </div>
      )}

      {status === 'error' && (
        <div style={{
          position:'absolute', inset:0,
          display:'flex', flexDirection:'column',
          alignItems:'center', justifyContent:'center', gap:8,
        }}>
          <Globe2 size={32} color="rgba(148,163,184,0.2)" />
          <p style={{ color:'rgba(148,163,184,0.4)', fontSize:13 }}>
            Carte non disponible — données épidémio ci-dessous
          </p>
        </div>
      )}

      {tooltip && (
        <div style={{
          position:'absolute',
          left: Math.min(tooltip.x + 14, (containerRef.current?.clientWidth || 800) - 160),
          top:  Math.max(tooltip.y - 60, 8),
          background:'rgba(13,21,40,0.95)',
          border:`1px solid ${tooltip.color}50`,
          borderRadius:10,
          padding:'10px 14px',
          fontSize:12,
          pointerEvents:'none',
          zIndex:20,
          minWidth:150,
          backdropFilter:'blur(8px)',
        }}>
          <p style={{
            color:'#fff', fontWeight:700,
            marginBottom:4, fontSize:13
          }}>
            {tooltip.label}
          </p>
          <p style={{
            color: tooltip.color,
            fontWeight:700, fontSize:15,
            fontFamily:'JetBrains Mono, monospace',
            marginBottom:2,
          }}>
            {tooltip.taux}%
          </p>
          <p style={{ color:'rgba(148,163,184,0.6)', fontSize:11 }}>
            Région OMS : {tooltip.region}
          </p>
        </div>
      )}
    </div>
  )
}

function RadarSVG({ data, couleur = '#FF6B35' }) {
  const cx = 150, cy = 140, r = 95
  const n  = data.length
  const max = 55
  const angle = i => (2 * Math.PI * i / n) - Math.PI / 2
  const gridPts = ratio =>
    data.map((_, i) => {
      const a = angle(i)
      return `${cx + r * ratio * Math.cos(a)},${cy + r * ratio * Math.sin(a)}`
    }).join(' ')
  const dataPts = data.map((d, i) => {
    const a = angle(i), ratio = Math.min(d.taux / max, 1)
    return { x: cx + r * ratio * Math.cos(a), y: cy + r * ratio * Math.sin(a) }
  })
  const polygon = dataPts.map(p => `${p.x},${p.y}`).join(' ')
  const labelPts = data.map((d, i) => {
    const a = angle(i)
    return {
      x: cx + (r + 30) * Math.cos(a),
      y: cy + (r + 30) * Math.sin(a),
      label: d.region, taux: d.taux,
    }
  })
  return (
    <svg width="300" height="280" viewBox="0 0 300 280"
      style={{ overflow:'visible' }}>
      {[0.25,0.5,0.75,1].map(ratio => (
        <polygon key={ratio} points={gridPts(ratio)}
          fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="1" />
      ))}
      {data.map((_, i) => {
        const a = angle(i)
        return (
          <line key={i} x1={cx} y1={cy}
            x2={cx + r * Math.cos(a)} y2={cy + r * Math.sin(a)}
            stroke="rgba(255,255,255,0.07)" strokeWidth="1" />
        )
      })}
      <polygon points={polygon}
        fill={`${couleur}30`} stroke={couleur}
        strokeWidth="2" strokeLinejoin="round" />
      {dataPts.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r={4}
          fill={couleur} stroke="#0A0F1E" strokeWidth="2" />
      ))}
      {labelPts.map((p, i) => (
        <g key={i}>
          <text x={p.x} y={p.y-6} textAnchor="middle"
            fill="#94a3b8" fontSize="11" fontFamily="Inter, sans-serif">
            {p.label}
          </text>
          <text x={p.x} y={p.y+8} textAnchor="middle"
            fill={couleur} fontSize="11" fontWeight="bold"
            fontFamily="JetBrains Mono, monospace">
            {p.taux}%
          </text>
        </g>
      ))}
    </svg>
  )
}

export default function CarteEpidemio() {
  const [pathogene, setPathogene] = useState('E. coli')
  const [annee, setAnnee]         = useState('2025')
  const [regionSel, setRegionSel] = useState(null)

  const dataPat   = PATHOGENES.find(p => p.pathogene === pathogene) || PATHOGENES[0]
  const radarData = REGIONS.map(r => ({ region: r.region, taux: dataPat[r.region] || 0 }))
  const regionActive = REGIONS.find(r => r.region === regionSel)

  return (
    <div className="space-y-6 pb-10">

      <motion.div initial={{ opacity:0, y:-16 }} animate={{ opacity:1, y:0 }}
        className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">
            Carte épidémiologique mondiale
          </h2>
          <p className="text-blue-200/50 text-sm">
            Distribution de la résistance aux antibiotiques —
            194 pays, 6 régions OMS, données {annee}.
          </p>
        </div>
        <div className="flex gap-3">
          <select value={pathogene} onChange={e => setPathogene(e.target.value)}
            className="bg-night-800 border border-white/10 rounded-xl
              px-3 py-2 text-white text-sm outline-none cursor-pointer">
            {PATHOGENES.map(p => <option key={p.pathogene}>{p.pathogene}</option>)}
          </select>
          <select value={annee} onChange={e => setAnnee(e.target.value)}
            className="bg-night-800 border border-white/10 rounded-xl
              px-3 py-2 text-white text-sm outline-none cursor-pointer">
            {['2025','2024','2023','2022','2021'].map(a =>
              <option key={a}>{a}</option>
            )}
          </select>
        </div>
      </motion.div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {STATS_GLOBALES.map((s, i) => (
          <motion.div key={i}
            initial={{ opacity:0, y:16 }}
            animate={{ opacity:1, y:0 }}
            transition={{ delay: i * 0.08 }}
            whileHover={{
              scale: 1.04,
              boxShadow: `0 0 28px ${s.color}40`,
              transition: { duration:0.2 },
            }}
            className="glass border border-white/8 p-4 text-center
              rounded-xl cursor-default">
            <p className="text-2xl font-bold font-mono mb-1"
              style={{ color: s.color }}>
              {s.val}
            </p>
            <p className="text-xs text-blue-200/50">{s.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Carte D3 */}
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
        transition={{ delay:0.15 }}
        className="glass border border-cyan/10 rounded-2xl overflow-hidden">
        <div style={{ height:380, width:'100%', position:'relative' }}>
          <CarteD3
            regionSel={regionSel}
            onRegionClick={id => setRegionSel(regionSel === id ? null : id)}
          />
        </div>
        <div className="flex items-center justify-center gap-5 py-3
          border-t border-white/5 flex-wrap px-4">
          {REGIONS.map(r => (
            <div key={r.region} className="flex items-center gap-2 cursor-pointer"
              onClick={() => setRegionSel(regionSel === r.region ? null : r.region)}>
              <div className="w-3 h-3 rounded-sm"
                style={{ background: r.couleur }} />
              <span className="text-xs text-blue-200/50">
                {r.region} — {r.taux}%
              </span>
            </div>
          ))}
        </div>
      </motion.div>

      {regionActive && (
        <motion.div
          initial={{ opacity:0, y:10 }} animate={{ opacity:1, y:0 }}
          className="glass border p-5 rounded-2xl"
          style={{ borderColor: regionActive.couleur + '40' }}>
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 rounded-lg"
              style={{ background: regionActive.couleur + '20' }}>
              <Globe2 size={18} style={{ color: regionActive.couleur }} />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-white">
                {regionActive.region} — {regionActive.label}
              </h3>
              <p className="text-xs text-blue-200/50">
                {regionActive.pays} pays · Taux moyen : {regionActive.taux}%
              </p>
            </div>
            <button onClick={() => setRegionSel(null)}
              className="text-blue-200/30 hover:text-white text-xs
                px-3 py-1 rounded-lg glass border border-white/10">
              ✕ Fermer
            </button>
          </div>
          <div className="h-2 bg-white/5 rounded-full overflow-hidden">
            <motion.div
              initial={{ width:0 }}
              animate={{ width:`${regionActive.taux}%` }}
              transition={{ duration:0.8 }}
              className="h-full rounded-full"
              style={{
                background: regionActive.couleur,
                boxShadow: `0 0 10px ${regionActive.couleur}80`
              }} />
          </div>
        </motion.div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {REGIONS.map((r, i) => (
          <motion.button key={r.region}
            initial={{ opacity:0, y:20 }}
            animate={{ opacity:1, y:0 }}
            transition={{ delay: i * 0.07 }}
            whileHover={{
              scale: 1.05,
              boxShadow: `0 0 25px ${r.couleur}50`,
              transition: { duration:0.2 },
            }}
            whileTap={{ scale:0.97 }}
            onClick={() => setRegionSel(regionSel === r.region ? null : r.region)}
            style={{
              border:`1px solid ${regionSel===r.region ? r.couleur+'60' : 'rgba(255,255,255,0.08)'}`,
              boxShadow: regionSel===r.region ? `0 0 25px ${r.couleur}50` : 'none',
            }}
            className={`p-4 rounded-xl text-center transition-all
              ${regionSel===r.region ? 'bg-white/5' : 'glass hover:bg-white/5'}`}>
            <p className="text-3xl font-bold font-mono mb-1"
              style={{ color: r.couleur }}>{r.taux}%</p>
            <p className="text-sm font-bold text-white">{r.region}</p>
            <p className="text-xs text-blue-200/40 mt-0.5">{r.pays} pays</p>
          </motion.button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity:0, x:-20 }} animate={{ opacity:1, x:0 }}
          transition={{ delay:0.2 }}
          className="glass border border-cyan/10 p-5">
          <h3 className="font-bold text-white mb-5 flex items-center gap-2">
            <Globe2 size={16} className="text-cyan" />
            Résistance par région OMS — {annee}
          </h3>
          <div className="space-y-4">
            {REGIONS.map((r, i) => (
              <motion.div key={r.region}
                initial={{ opacity:0, x:-20 }}
                animate={{ opacity:1, x:0 }}
                transition={{ delay: i*0.08+0.2 }}
                className="flex items-center gap-3">
                <span className="text-xs font-bold text-blue-200/60 w-12">
                  {r.region}
                </span>
                <div className="flex-1 h-6 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width:0 }}
                    animate={{ width:`${(r.taux/50)*100}%` }}
                    transition={{ delay:i*0.08+0.4, duration:0.8 }}
                    className="h-full rounded-full flex items-center px-3"
                    style={{
                      background: r.couleur,
                      boxShadow: `0 0 8px ${r.couleur}60`,
                    }}>
                    <span className="text-xs font-bold font-mono"
                      style={{ color:'#0A0F1E' }}>
                      {r.taux}%
                    </span>
                  </motion.div>
                </div>
                <span className="text-xs text-blue-200/40 w-14">
                  {r.pays} pays
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity:0, x:20 }} animate={{ opacity:1, x:0 }}
          transition={{ delay:0.3 }}
          className="glass border border-cyan/10 p-5">
          <h3 className="font-bold text-white mb-1 flex items-center gap-2">
            <Activity size={16} className="text-amr" />
            Profil — {pathogene}
          </h3>
          <p className="text-xs text-blue-200/40 mb-2">
            Taux par région OMS — {annee}
          </p>
          <div className="flex justify-center">
            <RadarSVG data={radarData} couleur="#FF6B35" />
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
          transition={{ delay:0.4 }}
          className="glass border border-cyan/10 p-5">
          <h3 className="font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp size={16} className="text-danger" />
            Pays avec les taux les plus élevés
          </h3>
          <div className="space-y-3">
            {TOP_PAYS.map((p, i) => (
              <motion.div key={p.pays}
                initial={{ opacity:0, x:-10 }}
                animate={{ opacity:1, x:0 }}
                transition={{ delay:0.05*i+0.4 }}
                className="flex items-center gap-3">
                <span className="text-lg">{p.flag}</span>
                <div className="w-20">
                  <p className="text-sm text-white font-medium">{p.pays}</p>
                  <p className="text-xs text-blue-200/40">{p.region}</p>
                </div>
                <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width:0 }}
                    animate={{ width:`${p.taux}%` }}
                    transition={{ delay:0.05*i+0.6, duration:0.8 }}
                    className="h-full rounded-full"
                    style={{
                      background: getColor(p.taux),
                      boxShadow: `0 0 6px ${getColor(p.taux)}60`
                    }} />
                </div>
                <span className="text-sm font-mono font-bold w-10 text-right"
                  style={{ color: getColor(p.taux) }}>
                  {p.taux}%
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
          transition={{ delay:0.5 }}
          className="glass border border-cyan/10 p-5">
          <h3 className="font-bold text-white mb-4 flex items-center gap-2">
            <MapPin size={16} className="text-violet" />
            Alertes épidémiologiques actives
          </h3>
          <div className="space-y-2.5">
            {ALERTES.map((a, i) => (
              <motion.div key={i}
                initial={{ opacity:0, x:10 }}
                animate={{ opacity:1, x:0 }}
                transition={{ delay:0.05*i+0.5 }}
                style={{
                  background: a.niveau==='ROUGE'
                    ? 'rgba(255,23,68,0.05)' : 'rgba(255,107,53,0.05)',
                  border:`1px solid ${a.niveau==='ROUGE'
                    ? 'rgba(255,23,68,0.2)' : 'rgba(255,107,53,0.2)'}`,
                }}
                className="p-3 rounded-xl flex items-start gap-3">
                <AlertTriangle size={14}
                  style={{
                    color: a.niveau==='ROUGE'?'#FF1744':'#FF6B35',
                    marginTop:2, flexShrink:0,
                  }} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold"
                      style={{ color: a.niveau==='ROUGE'?'#FF1744':'#FF6B35' }}>
                      {a.niveau}
                    </span>
                    <span className="text-sm text-white font-medium truncate">
                      {a.pathogene}
                    </span>
                  </div>
                  <p className="text-xs text-blue-200/50 mt-0.5">
                    {a.pays} — {a.region} · Résistance : {a.taux}%
                  </p>
                </div>
                <span className="text-xs font-mono font-bold shrink-0"
                  style={{ color: a.niveau==='ROUGE'?'#FF1744':'#FF6B35' }}>
                  {a.taux}%
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}