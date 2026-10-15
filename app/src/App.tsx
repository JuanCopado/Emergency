import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import Home from './pages/Home';
import DrugList from './pages/DrugList';
import DrugDetail from './pages/DrugDetail';
import NotFound from './pages/NotFound';

const Calculator = lazy(() => import('./pages/Calculator'));
const Settings = lazy(() => import('./pages/Settings'));
const About = lazy(() => import('./pages/About'));
const ClinicalNote = lazy(() => import('./pages/ClinicalNote'));
const ClinicalGuides = lazy(() => import('./pages/ClinicalGuides'));
const ClinicalLibrary = lazy(() => import('./pages/ClinicalLibrary'));
const PediatricOutpatient = lazy(() => import('./pages/PediatricOutpatient'));
const Procedures = lazy(() => import('./pages/Procedures'));
const ClinicalScores = lazy(() => import('./pages/ClinicalScores'));
const AcuteMedications = lazy(() => import('./pages/AcuteMedications'));

export default function App() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-muted">…</div>}>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="drugs" element={<DrugList />} />
          <Route path="drugs/:id" element={<DrugDetail />} />
          <Route path="calculator" element={<Calculator />} />
          <Route path="acute-medications" element={<AcuteMedications />} />
          <Route path="scores" element={<ClinicalScores />} />
          <Route path="pediatrics" element={<PediatricOutpatient />} />
          <Route path="procedures" element={<Procedures />} />
          <Route path="procedures/:id" element={<Procedures />} />
          <Route path="clinical-note" element={<ClinicalNote />} />
          <Route path="clinical" element={<ClinicalLibrary />} />
          <Route path="clinical/:id" element={<ClinicalLibrary />} />
          <Route path="guides" element={<ClinicalGuides />} />
          <Route path="guides/:id" element={<ClinicalGuides />} />
          <Route path="settings" element={<Settings />} />
          <Route path="about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
