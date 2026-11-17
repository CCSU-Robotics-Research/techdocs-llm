import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import PreviewPage from './PreviewPage.tsx'
import { useAppState } from '../../hooks/globalHook.ts'
import type { ProcessResult } from '../../features/contextModification/components/types.ts'

vi.mock('../../hooks/globalHook.ts', () => ({
    useAppState: vi.fn(),
}))

function renderPreviewPage(result: ProcessResult | null) {
    vi.mocked(useAppState).mockReturnValue({
        video: null,
        context: '',
        result,
        setVideo: () => undefined,
        setContext: () => undefined,
        setResult: () => undefined,
    })
    return render(
        <MemoryRouter initialEntries={['/preview']}>
            <Routes>
                <Route path="/preview" element={<PreviewPage />} />
                <Route path="/upload" element={<p>Upload page</p>} />
            </Routes>
        </MemoryRouter>,
    )
}

describe('PreviewPage', () => {
    afterEach(() => {
        cleanup()
    })

    it('redirects to upload when there is no result', () => {
        renderPreviewPage(null)

        expect(screen.getByText('Upload page')).toBeTruthy()
    })

    it('shows the generated document and returns to upload', () => {
        renderPreviewPage({ upload_id: 'abc123', status: 'page ready', html_file: 'input_workdocs.html' })

        const frame = screen.getByTitle('Generated documentation')
        expect(frame.getAttribute('src')).toBe('/api/documents/abc123')
        expect(frame.getAttribute('sandbox')).toBe('')

        fireEvent.click(screen.getByRole('button', { name: 'Process Another Video' }))

        expect(screen.getByText('Upload page')).toBeTruthy()
    })
})
