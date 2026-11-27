import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import DocumentEditingPage from './DocumentEditingPage.tsx'
import { useAppState } from '../../hooks/globalHook.ts'
import type { ProcessResult } from '../../features/contextModification/components/types.ts'

vi.mock('../../hooks/globalHook.ts', () => ({
    useAppState: vi.fn(),
}))

vi.mock('../../features/documentEditing/components/DocumentEditor.tsx', () => ({
    default: () => <p>Document editor</p>,
}))

function renderDocumentEditingPage(result: ProcessResult | null) {
    vi.mocked(useAppState).mockReturnValue({
        video: null,
        context: '',
        result,
        setVideo: () => undefined,
        setContext: () => undefined,
        setResult: () => undefined,
    })
    return render(
        <MemoryRouter initialEntries={['/document-editor']}>
            <Routes>
                <Route path="/document-editor" element={<DocumentEditingPage />} />
                <Route path="/upload" element={<p>Upload page</p>} />
            </Routes>
        </MemoryRouter>,
    )
}

describe('DocumentEditingPage', () => {
    afterEach(() => {
        cleanup()
    })

    it('redirects to upload when there is no result', () => {
        renderDocumentEditingPage(null)

        expect(screen.getByText('Upload page')).toBeTruthy()
    })

    it('shows the heading and the document editor', () => {
        renderDocumentEditingPage({ upload_id: 'abc123', status: 'keyframes_finalized', html_file: 'input_workdocs.html' })

        expect(screen.getByRole('heading', { name: 'Edit Generated Documentation' })).toBeTruthy()
        expect(screen.getByText('Document editor')).toBeTruthy()
    })
})
