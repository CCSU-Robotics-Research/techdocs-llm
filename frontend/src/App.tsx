import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './layouts/Layout.tsx'
import HomePage from '../src/pages/homePage/HomePage.tsx'
import ContextPage from '../src/pages/contextPage/ContextPage.tsx'
import DocumentEditor from '../src/pages/documentEditingPage/DocumentEditingPage.tsx'
import PreviewPage from '../src/pages/previewPage/PreviewPage.tsx'
import ImageSelectionPage from '../src/pages/imageSelectionPage/ImageSelectionPage.tsx'
import ResultPage from '../src/pages/resultPage/ResultPage.tsx'
import { AppStateProvider } from './hooks/globalHook.ts'

export default function App() {
    return (
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
                        <Route path="/document-editor" element={<DocumentEditor />} />
                        <Route path="*" element={<Navigate to="/upload" replace />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </AppStateProvider>
    )
}
