export type ProcessStatus = 'idle' | 'submitting' | 'error'

//Model for the response from the backend when a file is uploaded
export type ProcessResult = {
    upload_id: string
    filename: string
    content_type: string
    status: string
    audio_path: string
}