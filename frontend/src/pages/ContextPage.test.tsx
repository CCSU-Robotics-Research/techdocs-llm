import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import ContextPage from './ContextPage.tsx'
import { useAppState } from '../hooks/globalHook.ts'
import { useContextModification } from '../features/contextModification/hooks/useContextForm.ts'
import type { ProcessResult } from '../features/contextModification/components/types.ts'

vi.mock('../hooks/globalHook.ts', () => ({
    useAppState: vi.fn(),
}))

vi.mock('../features/contextModification/hooks/useContextForm.ts', () => ({
    useContextModification: vi.fn(),
}))

const submittedResult: ProcessResult = {
    upload_id: '8aa96b1cba6842da92122a17db757aac',
    status: 'page ready',
    html_file: 'input_workdocs.html',
}

const mockHandleSubmit = vi.fn<() => Promise<ProcessResult | null>>()

function renderContextPage() {
    return render(
        <MemoryRouter initialEntries={['/context']}>
            <Routes>
                <Route path="/context" element={<ContextPage />} />
                <Route path="/upload" element={<p>Upload page</p>} />
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
            setResult: () => undefined,
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
        mockHandleSubmit.mockResolvedValue(submittedResult)
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

    it('shows the selected video and context form', () => {
        renderContextPage()

        expect(screen.getByText('demo.mp4', { exact: false })).toBeTruthy()
        expect(screen.getByRole('textbox', { name: 'Optionally, enter context for the video:' })).toBeTruthy()
        expect(screen.getByRole('button', { name: 'Process Video' })).toBeTruthy()
    })

    it('shows a success dialog after submission and returns to upload when closed', async () => {
        renderContextPage()

        fireEvent.click(screen.getByRole('button', { name: 'Process Video' }))

        expect(await screen.findByRole('dialog')).toBeTruthy()
        expect(mockHandleSubmit).toHaveBeenCalledOnce()

        fireEvent.click(screen.getByRole('button', { name: 'Close' }))

        expect(screen.getByText('Upload page')).toBeTruthy()
    })
})
