import { Component } from 'react'
import { Globe2 } from 'lucide-react'

export default class MapErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }
  static getDerivedStateFromError() {
    return { hasError: true }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-full
          text-blue-200/30 gap-3">
          <Globe2 size={32} />
          <p className="text-sm">
            Carte interactive non disponible dans cette version.
          </p>
          <p className="text-xs">
            Les données épidémiologiques restent accessibles ci-dessous.
          </p>
        </div>
      )
    }
    return this.props.children
  }
}