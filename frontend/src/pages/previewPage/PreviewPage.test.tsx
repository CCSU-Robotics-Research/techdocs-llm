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
                <Route path="/image-selection" element={<p>Image selection page</p>} />
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

    it('redirects to image selection when the document is still a draft', () => {
        renderPreviewPage({ upload_id: 'abc123', status: 'done', html_file: 'input_workdocs.html' })

        expect(screen.getByText('Image selection page')).toBeTruthy()
        expect(screen.queryByRole('progressbar')).toBeNull()
    })

    it('shows the finished document at 100% and returns to upload', () => {
        renderPreviewPage({ upload_id: 'abc123', status: 'keyframes_finalized', html_file: 'input_workdocs.html' })

        const frame = screen.getByTitle('Generated documentation')
        expect(screen.getByRole('progressbar').getAttribute('value')).toBe('100')
        expect(frame.getAttribute('src')).toBe('/api/documents/abc123')
        expect(frame.getAttribute('sandbox')).toBe('')

        fireEvent.click(screen.getByRole('button', { name: 'Process Another Video' }))

        expect(screen.getByText('Upload page')).toBeTruthy()
    })
})
