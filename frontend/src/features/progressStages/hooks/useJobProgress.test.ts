import { act, cleanup, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useJobProgress } from './useJobProgress.ts'
import { getJobStatus } from '../services/service.ts'
import { POLL_INTERVAL_MS } from '../components/constants.ts'
import type { JobStatus } from '../components/types.ts'

vi.mock('../services/service.ts', () => ({
    getJobStatus: vi.fn(),
}))

const uploadId = '8aa96b1cba6842da92122a17db757aac'
const transcribing: JobStatus = { upload_id: uploadId, stage: 'transcribing', progress: 50 }
const done: JobStatus = { upload_id: uploadId, stage: 'done', progress: 100, html_file: 'input_workdocs.html' }

//Move the fake clock forward and let any pending progress checks finish.
async function advance(ms: number) {
    await act(async () => {
        await vi.advanceTimersByTimeAsync(ms)
    })
}

describe('useJobProgress', () => {
    beforeEach(() => {
        vi.useFakeTimers()
        vi.clearAllMocks()
    })

    afterEach(() => {
        cleanup()
        vi.useRealTimers()
    })

    it('does not check progress before a job starts', async () => {
        const { result } = renderHook(() => useJobProgress(null))
        await advance(POLL_INTERVAL_MS * 3)

        expect(getJobStatus).not.toHaveBeenCalled()
        expect(result.current).toEqual({ job: null, errorMessage: null })
    })

    it('checks progress until the job is done, then stops', async () => {
        vi.mocked(getJobStatus).mockResolvedValueOnce(transcribing).mockResolvedValueOnce(done)
        const { result } = renderHook(() => useJobProgress(uploadId))

        await advance(0)
        expect(result.current.job).toEqual(transcribing)

        await advance(POLL_INTERVAL_MS)
        expect(result.current.job).toEqual(done)

        await advance(POLL_INTERVAL_MS * 5)
        expect(getJobStatus).toHaveBeenCalledTimes(2)
        expect(vi.mocked(getJobStatus).mock.calls[0][0]).toBe(uploadId)
    })

    it('stops checking when the job fails', async () => {
        vi.mocked(getJobStatus).mockResolvedValue({ ...transcribing, failed: true, detail: 'Processing failed.' })
        const { result } = renderHook(() => useJobProgress(uploadId))

        await advance(POLL_INTERVAL_MS * 5)

        expect(result.current.job?.failed).toBe(true)
        expect(getJobStatus).toHaveBeenCalledTimes(1)
    })

    it('keeps the last progress and reports an error when a check fails', async () => {
        vi.mocked(getJobStatus)
            .mockResolvedValueOnce(transcribing)
            .mockRejectedValueOnce(new Error('Failed to check processing progress: HTTP 500'))
        const { result } = renderHook(() => useJobProgress(uploadId))

        await advance(POLL_INTERVAL_MS)

        expect(result.current.job).toEqual(transcribing)
        expect(result.current.errorMessage).toBe('Failed to check processing progress: HTTP 500')
        await advance(POLL_INTERVAL_MS * 5)
        expect(getJobStatus).toHaveBeenCalledTimes(2)
    })

    it('stops checking when the component unmounts', async () => {
        vi.mocked(getJobStatus).mockResolvedValue(transcribing)
        const { unmount } = renderHook(() => useJobProgress(uploadId))

        await advance(0)
        unmount()
        await advance(POLL_INTERVAL_MS * 5)

        expect(getJobStatus).toHaveBeenCalledTimes(1)
    })
})
