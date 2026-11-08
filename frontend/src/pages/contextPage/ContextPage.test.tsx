import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import ContextPage from './ContextPage.tsx'
import { useAppState } from '../../hooks/globalHook.ts'
import { useContextModification } from '../../features/contextModification/hooks/useContextForm.ts'
import { useJobProgress } from '../../features/progressStages/hooks/useJobProgress.ts'
import type { ProcessStarted } from '../../features/contextModification/components/types.ts'
import type { JobStatus } from '../../features/progressStages/components/types.ts'

vi.mock('../../hooks/globalHook.ts', () => ({
    useAppState: vi.fn(),
}))

vi.mock('../../features/contextModification/hooks/useContextForm.ts', () => ({
    useContextModification: vi.fn(),
}))

vi.mock('../../features/progressStages/hooks/useJobProgress.ts', () => ({
    useJobProgress: vi.fn(),
}))

const uploadId = '8aa96b1cba6842da92122a17db757aac'

const startedJob: ProcessStarted = {
    upload_id: uploadId,
    filename: 'demo.mp4',
    content_type: 'video/mp4',
    status: 'processing',
}

const mockHandleSubmit = vi.fn<() => Promise<ProcessStarted | null>>()
const mockSetResult = vi.fn()

//Report the given job status once a job has started, and no progress before that.
function mockJobProgress(job: JobStatus) {
    vi.mocked(useJobProgress).mockImplementation((id) => ({
        job: id ? job : null,
        errorMessage: null,
    }))
}

function renderContextPage() {
    return render(
        <MemoryRouter initialEntries={['/context']}>
            <Routes>
                <Route path="/context" element={<ContextPage />} />
                <Route path="/upload" element={<p>Upload page</p>} />
                <Route path="/preview" element={<p>Preview page</p>} />
            </Routes>
        </MemoryRouter>,
    )
}

describe('ContextPage', () => {
    afterEach(() => {
        cleanup()
    })

    beforeEach(() => {
        vi.clearAllMocks()
        vi.mocked(useAppState).mockReturnValue({
            video: new File(['video'], 'demo.mp4', { type: 'video/mp4' }),
            context: '',
            result: null,
            setVideo: () => undefined,
            setContext: () => undefined,
            setResult: mockSetResult,
        })
        vi.mocked(useContextModification).mockReturnValue({
            context: 'Handle the robot safely.',
            setContext: vi.fn(),
            status: 'idle',
            errorMessage: null,
            isTooLong: false,
            canSubmit: true,
            handleSubmit: mockHandleSubmit,
        })
        vi.mocked(useJobProgress).mockReturnValue({ job: null, errorMessage: null })
        mockHandleSubmit.mockResolvedValue(startedJob)
    })

    it('redirects to upload when no video is selected', () => {
        vi.mocked(useAppState).mockReturnValue({
            video: null,
            context: '',
            result: null,
            setVideo: () => undefined,
            setContext: () => undefined,
            setResult: () => undefined,
        })

        renderContextPage()

        expect(screen.getByText('Upload page')).toBeTruthy()
    })

    it('shows the selected video and context form without a progress bar', () => {
        renderContextPage()

        expect(screen.getByText('demo.mp4', { exact: false })).toBeTruthy()
        expect(screen.getByRole('textbox', { name: 'Optionally, enter context for the video:' })).toBeTruthy()
        expect(screen.getByRole('button', { name: 'Process Video' })).toBeTruthy()
        expect(screen.queryByRole('progressbar')).toBeNull()
    })

    it('shows the current stage and progress while the video is processing', async () => {
        mockJobProgress({ upload_id: uploadId, stage: 'transcribing', progress: 50 })
        renderContextPage()

        fireEvent.click(screen.getByRole('button', { name: 'Process Video' }))

        expect(await screen.findByText('Transcribing audio… (50%)')).toBeTruthy()
        expect(screen.getByRole('progressbar').getAttribute('value')).toBe('50')
        expect(vi.mocked(useJobProgress)).toHaveBeenLastCalledWith(uploadId)
        expect(screen.getByRole('button', { name: 'Processing...' }).hasAttribute('disabled')).toBe(true)
    })

    it('goes to the preview page when processing is done', async () => {
        mockJobProgress({ upload_id: uploadId, stage: 'done', progress: 100, html_file: 'input_workdocs.html' })
        renderContextPage()

        fireEvent.click(screen.getByRole('button', { name: 'Process Video' }))

        expect(await screen.findByText('Preview page')).toBeTruthy()
        expect(mockSetResult).toHaveBeenCalledWith({ upload_id: uploadId, status: 'done', html_file: 'input_workdocs.html' })
        expect(mockHandleSubmit).toHaveBeenCalledOnce()
    })

    it('shows the error and allows resubmitting when processing fails', async () => {
        mockJobProgress({ upload_id: uploadId, stage: 'transcribing', progress: 50, failed: true, detail: 'Processing failed.' })
        renderContextPage()

        fireEvent.click(screen.getByRole('button', { name: 'Process Video' }))

        expect(await screen.findByText('Processing failed.')).toBeTruthy()
        expect(screen.queryByRole('progressbar')).toBeNull()
        expect(screen.getByRole('button', { name: 'Process Video' }).hasAttribute('disabled')).toBe(false)
        expect(mockSetResult).not.toHaveBeenCalled()
    })
})
