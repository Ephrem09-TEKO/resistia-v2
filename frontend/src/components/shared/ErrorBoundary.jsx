import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('[ResistIA] Erreur capturée:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          background: '#0A0F1E',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          gap: 16,
          fontFamily: 'Inter, sans-serif',
          color: '#E8F4FD',
          textAlign: 'center',
          padding: 24,
        }}>
          <div style={{ fontSize: 48 }}>🧬</div>
          <h1 style={{ color:'#00D4FF', fontSize:22, fontWeight:700 }}>
            ResistIA — Erreur de chargement
          </h1>
          <p style={{ color:'rgba(148,163,184,0.7)', maxWidth:400 }}>
            Une erreur est survenue. Cela peut arriver après une mise à jour
            du cache. Rechargez la page.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding:'10px 24px', borderRadius:12,
              background:'#00D4FF', color:'#0A0F1E',
              fontWeight:700, fontSize:14, border:'none',
              cursor:'pointer', marginTop:8,
            }}>
            🔄 Recharger ResistIA
          </button>
        </div>
      )
    }
    return this.props.children
  }
}