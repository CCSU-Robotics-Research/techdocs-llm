import type { JobStatus } from '../components/types.ts'

//Service for checking the current stage and progress of a documentation job
export async function getJobStatus(uploadId: string, signal?: AbortSignal): Promise<JobStatus> {
    //Request the latest progress without using a cached response
    const response = await fetch(`/api/jobs/${uploadId}`, {signal, cache: 'no-store'})
    //Error Handling: If the check fails, throw an error with the HTTP status code
    if (!response.ok)
    {
        throw new Error(`Failed to check processing progress: HTTP ${response.status}`)
    }
    //Parse the response from the backend and return the job status
    const job: JobStatus = await response.json()
    return job
}
