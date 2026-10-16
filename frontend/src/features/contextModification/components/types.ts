export type ProcessStatus = 'idle' | 'submitting' | 'error'

export type ProcessResult = {
    jobId:string
    htmlFile:string
    outputDir:string
}