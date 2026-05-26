import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Analyse from './pages/Analyse'
import BaseBacterienne from './pages/BaseBacterienne'
import CarteEpidemio from './pages/CarteEpidemio'
import DrugDiscovery from './pages/DrugDiscovery'
import SimBio from './pages/SimBio'
import Assistant from './pages/Assistant'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index          element={<Dashboard />} />
          <Route path="analyse" element={<Analyse />} />
          <Route path="bacteries" element={<BaseBacterienne />} />
          <Route path="carte"   element={<CarteEpidemio />} />
          <Route path="discovery" element={<DrugDiscovery />} />
          <Route path="simbio"  element={<SimBio />} />
          <Route path="assistant" element={<Assistant />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App