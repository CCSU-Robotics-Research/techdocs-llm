import type { ProcessResult } from '../components/types.ts'

export async function submitContext(video: File, _context: string): Promise<ProcessResult> {
    void _context
    const base = video.name.replace(/\.[^.]+$/, '')
    return{
        jobId: `local-${Date.now()}`,
        htmlFile: `${base}.html`,
        outputDir: `output/${base}`,
    }
}