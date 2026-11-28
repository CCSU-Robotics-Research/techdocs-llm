import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import ResultPage from './ResultPage.tsx'
import { useAppState } from '../../hooks/globalHook.ts'
import { downloadDocument } from '../../features/documentSaving/documentDownload.ts'
import type { ProcessResult } from '../../features/contextModification/components/types.ts'

vi.mock('../../hooks/globalHook.ts', () => ({
    useAppState: vi.fn(),
}))

vi.mock('../../features/documentSaving/services/documentDownload.ts', () => ({
    downloadDocument: vi.fn(),
}))

const finalized: ProcessResult = { upload_id: 'abc123', status: 'keyframes_finalized', html_file: 'input_workdocs.html' }

function renderResultPage(result: ProcessResult | null) {
    vi.mocked(useAppState).mockReturnValue({
        theme: 'light',
        setTheme: () => undefined,
        video: null,
        context: '',
        result,
        setVideo: () => undefined,
        setContext: () => undefined,
        setResult: () => undefined,
    })
    return render(
        <MemoryRouter initialEntries={['/result']}>
            <Routes>
                <Route path="/result" element={<ResultPage />} />
                <Route path="/upload" element={<p>Upload page</p>} />
                <Route path="/image-selection" element={<p>Image selection page</p>} />
                <Route path="/preview" element={<p>Preview page</p>} />
            </Routes>
        </MemoryRouter>,
    )
}

describe('ResultPage', () => {
    afterEach(() => {
        cleanup()
        vi.resetAllMocks()
    })

    it('redirects to upload when there is no result', () => {
        renderResultPage(null)

        expect(screen.getByText('Upload page')).toBeTruthy()
    })

    it('redirects to image selection when the keyframes are not finalized', () => {
        renderResultPage({ ...finalized, status: 'done' })

        expect(screen.getByText('Image selection page')).toBeTruthy()
        expect(screen.queryByRole('button', { name: 'Download Documentation' })).toBeNull()
    })

    it('shows what the download contains', () => {
        renderResultPage(finalized)

        expect(screen.getByText('Video Processing Successful!')).toBeTruthy()
        expect(screen.getByText('input_workdocs.html')).toBeTruthy()
        expect(downloadDocument).not.toHaveBeenCalled()
    })

    it('downloads the document and reports the saved file', async () => {
        vi.mocked(downloadDocument).mockResolvedValue('documentation-abc123.zip')
        renderResultPage(finalized)

        fireEvent.click(screen.getByRole('button', { name: 'Download Documentation' }))

        const status = await screen.findByRole('status')
        expect(status.textContent).toContain('documentation-abc123.zip')
        expect(downloadDocument).toHaveBeenCalledWith('abc123')
        expect(screen.queryByRole('alert')).toBeNull()
    })

    it('disables the button while the download is being prepared', async () => {
        let finish: (name: string) => void = () => undefined
        vi.mocked(downloadDocument).mockReturnValue(new Promise<string>(resolve => { finish = resolve }))
        renderResultPage(finalized)

        fireEvent.click(screen.getByRole('button', { name: 'Download Documentation' }))

        const busy = await screen.findByRole('button', { name: 'Preparing download…' })
        expect((busy as HTMLButtonElement).disabled).toBe(true)

        finish('documentation-abc123.zip')
        await screen.findByRole('button', { name: 'Download Documentation' })
    })

    it('shows the backend error and lets the user try again', async () => {
        vi.mocked(downloadDocument)
            .mockRejectedValueOnce(new Error('Not all keyframes have been selected'))
            .mockResolvedValueOnce('documentation-abc123.zip')
        renderResultPage(finalized)

        fireEvent.click(screen.getByRole('button', { name: 'Download Documentation' }))

        const alert = await screen.findByRole('alert')
        expect(alert.textContent).toBe('Not all keyframes have been selected')
        expect(screen.queryByRole('status')).toBeNull()

        fireEvent.click(screen.getByRole('button', { name: 'Download Documentation' }))

        await waitFor(() => expect(screen.queryByRole('alert')).toBeNull())
        expect((await screen.findByRole('status')).textContent).toContain('documentation-abc123.zip')
    })

    it('goes back to the preview', () => {
        renderResultPage(finalized)

        fireEvent.click(screen.getByRole('button', { name: 'Back to Preview' }))

        expect(screen.getByText('Preview page')).toBeTruthy()
    })

    it('returns to the main page', () => {
        renderResultPage(finalized)

        fireEvent.click(screen.getByRole('button', { name: 'Back to Main Page' }))

        expect(screen.getByText('Upload page')).toBeTruthy()
    })
})
