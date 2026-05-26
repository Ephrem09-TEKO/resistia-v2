import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bot, Send, User, Sparkles, Loader2,
         RotateCcw, BookOpen, Globe2, FlaskConical } from 'lucide-react'
import { apiAssistant } from '../services/api'

const SUGGESTIONS = [
  { icon:FlaskConical, text:"Qu'est-ce qu'une ESBL et comment la traiter ?" },
  { icon:Globe2,       text:"Quel est le taux de résistance de E. coli au Togo ?" },
  { icon:BookOpen,     text:"Quels sont les antibiotiques de dernier recours ?" },
  { icon:Sparkles,     text:"Comment prévenir la résistance aux antibiotiques ?" },
]

const BASE_REPONSES = {
  'esbl': "Les ESBL (Extended-Spectrum Beta-Lactamases) sont des enzymes produites par certaines bactéries comme E. coli et K. pneumoniae qui détruisent la plupart des pénicillines et céphalosporines. Pour les traiter : les carbapénèmes (imipénem, méropénem) restent généralement actifs. Les gènes impliqués incluent blaCTX-M, blaTEM et blaSHV. En Afrique, les ESBL représentent 35-55% des E. coli cliniques.",
  'togo': "D'après la base ResistIA (données 2025), le taux de résistance de E. coli à la ciprofloxacine au Togo est de 68.8% — résistance majoritaire. La nitrofurantoïne (8%) et la fosfomycine (4%) restent les meilleures options pour les infections urinaires non compliquées.",
  'dernier': "Les antibiotiques de dernier recours selon l'OMS (catégorie RÉSERVE) incluent : la colistine, la polymyxine B, le céfidérocol, l'aztréonam-avibactam, l'imipénem-relebactam et la ceftazidime-avibactam. Ils ne doivent être utilisés qu'en l'absence totale d'alternative documentée.",
  'prévenir': "Pour prévenir la résistance aux antibiotiques : 1) Prescrire uniquement si infection bactérienne confirmée, 2) Choisir le spectre le plus étroit possible, 3) Respecter la durée minimale efficace, 4) Guider le traitement par l'antibiogramme, 5) Hygiène des mains stricte en milieu de soins, 6) Vaccination pour réduire les infections bactériennes.",
  'sarm': "Le SARM (S. aureus Résistant à la Méticilline) possède le gène mecA qui code une protéine PBP2a résistante à tous les bêta-lactamines. Traitement de choix : vancomycine 15-20mg/kg IV toutes les 8-12h. Alternatives : linézolide, daptomycine. Le SARM est classé PRIORITÉ HAUTE par l'OMS.",
  'default': "Je suis ResistIA Brain, spécialisé en résistance aux antibiotiques. Je peux vous répondre sur les mécanismes de résistance, les pathogènes critiques, les stratégies thérapeutiques, et les données épidémiologiques mondiales. Posez-moi une question spécifique pour une réponse précise.",
}

function getReponse(question) {
  const q = question.toLowerCase()
  if (q.includes('esbl') || q.includes('bêta-lactamase') || q.includes('beta')) return BASE_REPONSES.esbl
  if (q.includes('togo') || q.includes('ciprofloxacine') && q.includes('coli')) return BASE_REPONSES.togo
  if (q.includes('dernier recours') || q.includes('réserve') || q.includes('last resort')) return BASE_REPONSES.dernier
  if (q.includes('prévenir') || q.includes('prévention') || q.includes('stewardship')) return BASE_REPONSES.prévenir
  if (q.includes('sarm') || q.includes('mrsa') || q.includes('méticilline')) return BASE_REPONSES.sarm
  return BASE_REPONSES.default
}

export default function Assistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Bonjour ! Je suis ResistIA Brain 🧠, votre assistant spécialisé en résistance aux antibiotiques. Je peux vous aider à comprendre les mécanismes de résistance, trouver les données épidémiologiques, ou vous guider dans le choix d'un traitement. Comment puis-je vous aider ?",
      time: new Date().toLocaleTimeString('fr-FR', {hour:'2-digit',minute:'2-digit'}),
    }
  ])
  const [input, setInput]     = useState('')
  const [loading, setLoading] = useState(false)
  const endRef                = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior:'smooth' })
  }, [messages])

  const envoyer = async (texte) => {
  const question = texte || input.trim()
  if (!question) return
  setInput('')

  const now = new Date().toLocaleTimeString('fr-FR',
    { hour:'2-digit', minute:'2-digit' })

  setMessages(prev => [...prev, {
    role:'user', content:question, time:now
  }])
  setLoading(true)

  // Appel API backend
  const data = await apiAssistant.chat(question)

  const reponse = data?.reponse || getReponse(question)
  const content = typeof reponse === 'string' ? reponse : reponse.reponse

  setMessages(prev => [...prev, {
    role:    'assistant',
    content: content,
    sources: data?.sources || [],
    confiance: data?.confiance || null,
    time: new Date().toLocaleTimeString('fr-FR',
      { hour:'2-digit', minute:'2-digit' }),
  }])
  setLoading(false)
}

  const reset = () => setMessages([{
    role:'assistant',
    content:"Conversation réinitialisée. Comment puis-je vous aider ?",
    time: new Date().toLocaleTimeString('fr-FR', {hour:'2-digit',minute:'2-digit'}),
  }])

  return (
    <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-8rem)] pb-4">

      {/* En-tête */}
      <motion.div initial={{opacity:0,y:-16}} animate={{opacity:1,y:0}}
        className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-br from-cyan to-violet glow-cyan">
            <Bot size={20} className="text-night"/>
          </div>
          <div>
            <h2 className="font-bold text-white leading-none">Brain Chat</h2>
            <p className="text-xs text-bio flex items-center gap-1 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-bio animate-pulse"/>
              ResistIA Brain 🧠 — en ligne
            </p>
          </div>
        </div>
        <button onClick={reset}
          className="flex items-center gap-2 px-3 py-2 rounded-xl
            glass border border-white/10 text-blue-200/50 hover:text-white
            text-xs transition-all">
          <RotateCcw size={12}/> Nouvelle conversation
        </button>
      </motion.div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 mb-4">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div key={i}
              initial={{opacity:0, y:10, scale:0.98}}
              animate={{opacity:1, y:0, scale:1}}
              className={`flex gap-3 ${msg.role==='user'?'flex-row-reverse':''}`}>

              {/* Avatar */}
              <div className={`w-8 h-8 rounded-xl flex items-center justify-center
                shrink-0 ${msg.role==='assistant'
                  ? 'bg-gradient-to-br from-cyan to-violet'
                  : 'bg-white/10 border border-white/20'}`}>
                {msg.role==='assistant'
                  ? <Bot size={14} className="text-night"/>
                  : <User size={14} className="text-white"/>}
              </div>

              {/* Bulle */}
              <div className={`max-w-[80%] space-y-1
                ${msg.role==='user'?'items-end':'items-start'} flex flex-col`}>
                <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed
                  ${msg.role==='assistant'
                    ? 'glass border border-cyan/10 text-blue-100'
                    : 'bg-gradient-to-br from-cyan/20 to-violet/20 border border-cyan/20 text-white'}`}>
                  {msg.content}
                </div>
                <span className="text-xs text-blue-200/30 px-1">{msg.time}</span>
              </div>
            </motion.div>
          ))}

          {loading && (
            <motion.div key="loading"
              initial={{opacity:0,y:10}} animate={{opacity:1,y:0}}
              className="flex gap-3">
              <div className="w-8 h-8 rounded-xl flex items-center justify-center
                bg-gradient-to-br from-cyan to-violet shrink-0">
                <Bot size={14} className="text-night"/>
              </div>
              <div className="glass border border-cyan/10 px-4 py-3 rounded-2xl">
                <div className="flex items-center gap-2">
                  <Loader2 size={14} className="text-cyan animate-spin"/>
                  <span className="text-sm text-blue-200/60">
                    ResistIA Brain analyse votre question...
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={endRef}/>
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <motion.div initial={{opacity:0}} animate={{opacity:1}}
          className="grid grid-cols-2 gap-2 mb-4">
          {SUGGESTIONS.map((s, i) => (
            <button key={i} onClick={() => envoyer(s.text)}
              className="glass border border-white/8 p-3 rounded-xl text-left
                text-xs text-blue-200/60 hover:text-white hover:border-cyan/20
                transition-all flex items-start gap-2">
              <s.icon size={14} className="text-cyan mt-0.5 shrink-0"/>
              {s.text}
            </button>
          ))}
        </motion.div>
      )}

      {/* Input */}
      <div className="glass border border-cyan/20 p-3 flex items-end gap-3">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key==='Enter' && !e.shiftKey) {
              e.preventDefault()
              envoyer()
            }
          }}
          placeholder="Posez votre question sur la résistance aux antibiotiques..."
          rows={1}
          className="flex-1 bg-transparent text-white text-sm
            placeholder-blue-200/30 outline-none resize-none
            leading-relaxed min-h-[36px] max-h-32"
          style={{scrollbarWidth:'none'}}
        />
        <motion.button
          whileHover={{scale:1.05}} whileTap={{scale:0.95}}
          onClick={() => envoyer()}
          disabled={!input.trim() || loading}
          className={`p-2.5 rounded-xl transition-all shrink-0
            ${input.trim() && !loading
              ? 'bg-cyan text-night shadow-[0_0_15px_rgba(0,212,255,0.4)]'
              : 'bg-white/10 text-blue-200/30 cursor-not-allowed'}`}>
          <Send size={16}/>
        </motion.button>
      </div>
    </div>
  )
}