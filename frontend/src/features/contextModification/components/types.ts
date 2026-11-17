export type ProcessStatus = 'idle' | 'submitting' | 'error'

//Model for the 202 Accepted response from the backend when processing starts
export type ProcessStarted = {
    upload_id: string
    filename: string
    content_type: string
    status: string
}

//Model for the generated document and whether its keyframes have been finalized.
export type ProcessResult = {
    upload_id: string
    status: 'done' | 'keyframes_finalized'
    html_file: string
}
