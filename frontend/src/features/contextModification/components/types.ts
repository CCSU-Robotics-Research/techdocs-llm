export type ProcessStatus = 'idle' | 'submitting' | 'error'

//Model for the 202 Accepted response from the backend when processing starts
export type ProcessStarted = {
    upload_id: string
    filename: string
    content_type: string
    status: string
}

//Model for a finished job, used to display the generated documentation
export type ProcessResult = {
    upload_id: string
    status: string
    html_file: string
}