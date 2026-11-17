//Stages a documentation job moves through on the backend, in order.
export type JobStage = 'uploaded' | 'extracting_audio' | 'transcribing' | 'generating_page' | 'done'

//Model for the response from the backend when checking the progress of a job
export type JobStatus = {
    upload_id: string
    stage: JobStage
    progress: number
    html_file?: string
    failed?: boolean
    detail?: string
}
