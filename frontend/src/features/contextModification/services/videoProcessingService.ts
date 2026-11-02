import type { ProcessResult } from '../components/types.ts'


//Service for submitting a video file and its context to the backend for processing
export async function submitContext(video: File, videoContext: string): Promise<ProcessResult> {
    const form = new FormData()
    form.append('video', video)
    form.append('context', videoContext)
    //Submit the video file and context to the backend for processing
    const response = await fetch('/api/generate-documentation', {method: 'POST', body: form,})
    //Error Handling: If the processing fails, throw an error with the HTTP status code
    if (!response.ok)
    {
        throw new Error(`Failed to process video file: HTTP ${response.status}`)
    }
    //Parse the response from the backend and return the result
    const result: ProcessResult = await response.json()
    return result
}
