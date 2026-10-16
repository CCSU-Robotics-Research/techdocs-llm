import type { ProcessResult } from '../components/types'

export async function submitContext(video: File, context: string): Promise<ProcessResult> {
    const base = video.name.replace(/\.[^.]+$/, '')
    return{
        jobId: `local-${Date.now()}`,
        htmlFile: `${base}.html`,
        outputDir: `output/${base}`,
    }
}