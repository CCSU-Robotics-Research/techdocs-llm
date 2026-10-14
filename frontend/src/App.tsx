import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './layouts/Layout.tsx'
import HomePage from './pages/HomePage.tsx'
import ContextPage from './pages/ContextPage.tsx'
import PreviewPage from './pages/PreviewPage.tsx'
import ImageSelectionPage from './pages/ImageSelectionPage.tsx'
import ResultPage from './pages/ResultPage.tsx'
import { AppStateProvider } from './hooks/globalHook.ts'

export default function App(){
    return(
        <AppStateProvider>
            <BrowserRouter>
                <Routes>
                    <Route element={<Layout />}>
                        <Route index element={<HomePage />} />
                        <Route path="/upload" element={<HomePage />} />
                        <Route path="/context" element={<ContextPage />} />
                        <Route path="/preview" element={<PreviewPage />} />
                        <Route path="/image-selection" element={<ImageSelectionPage />} />
                        <Route path="/result" element={<ResultPage />} />
                        <Route path="*" element={<Navigate to="/upload" replace />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </AppStateProvider>
    )
}