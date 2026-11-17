import { useEffect, useState } from 'react'
import { POLL_INTERVAL_MS } from '../components/constants.ts'
import { getJobStatus } from '../services/service.ts'
import type { JobStatus } from '../components/types.ts'

//Latest progress check, tagged with the job it belongs to so a new job never shows an old job's progress.
type ProgressState = {
    uploadId: string
    job: JobStatus | null
    errorMessage: string | null
}

//Hook to poll the backend for the progress of a job until it is done or fails.
export function useJobProgress(uploadId: string | null){
    const [progress, setProgress] = useState<ProgressState | null>(null)

    useEffect(() => {
        if (!uploadId) return
        const jobId = uploadId

        //Controller to cancel the request and track whether the component is active.
        const controller = new AbortController()
        let active = true
        let timeout: number | undefined

        async function checkProgress(){
            try{
                const job = await getJobStatus(jobId, controller.signal)
                //Update the progress only if the component is still active.
                if (!active) return
                setProgress({ uploadId: jobId, job, errorMessage: null })

                //Check again after a short wait until the job is done or fails.
                if (job.stage !== 'done' && !job.failed) {
                    timeout = window.setTimeout(checkProgress, POLL_INTERVAL_MS)
                }
            }catch(error){
                //Error Handling: Stop checking and keep the last progress shown alongside the error.
                if (!active) return
                setProgress((previous) => ({
                    uploadId: jobId,
                    job: previous?.uploadId === jobId ? previous.job : null,
                    errorMessage: error instanceof Error ? error.message : 'Failed to check processing progress.',
                }))
            }
        }

        //Run the first check as soon as the job starts.
        checkProgress()

        //Stop checking and cancel the request when the job changes or the component unmounts.
        return () => {
            active = false
            window.clearTimeout(timeout)
            controller.abort()
        }
    }, [uploadId])

    const current = progress?.uploadId === uploadId ? progress : null
    return { job: current?.job ?? null, errorMessage: current?.errorMessage ?? null }
}
