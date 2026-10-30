import type { ProcessResult, UploadResult } from '../components/types.ts'


//Service for submitting a video file to the backend for processing
export async function submitContext(video: File, videoContext: string): Promise<ProcessResult> {
    const form = new FormData()
    form.append('video', video)
    //Submit the video file to the backend for processing
    const uploadResponse = await fetch('/api/upload', {method: 'POST', body: form,})
    //Error Handling: If the upload fails, throw an error with the HTTP status code
        if (!uploadResponse.ok) 
        {
        throw new Error('Failed to upload video file, or audio extraction failed: HTTP ${uploadResponse.status}',)
        }
    //Parse the response from the backend and return the result
    const upload: UploadResult = await uploadResponse.json()
    //Submit the upload ID and context to the backend for processing
    const processResponse = await fetch('/api/generate',{method: 'POST', headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({upload_id: upload.upload_id, context: videoContext})})

        //Error Handling: If the processing fails, throw an error with the HTTP status code
        if(!processResponse.ok)
        {
            throw new Error('Failed to process video file: HTTP ${processResponse.status}',)

        }
        //Parse the response from the backend and return the result
        const result: ProcessResult = await processResponse.json()
        return result

    }