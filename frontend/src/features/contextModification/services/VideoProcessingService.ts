import type { ProcessResult } from '../components/types.ts'
//Service for submitting a video file to the backend for processing
export async function submitContext(video: File, _context: string): Promise<ProcessResult> {
    void _context
    const form = new FormData()

    form.append('video', video)

    const response = await fetch('/api/upload', {
        method: 'POST',
        body: form,
    })

    if (!response.ok) {
        throw new Error(`Video processing failed. Error: HTTP ${response.status}`)
    }

    return response.json()
}