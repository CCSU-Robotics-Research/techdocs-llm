import type { JobStage } from './types.ts'

//How often to check the progress of a job, in milliseconds.
export const POLL_INTERVAL_MS = 1500

//Message displayed under the progress bar for each stage.
export const STAGE_LABELS: Record<JobStage, string> = {
    uploaded: 'Video uploaded',
    extracting_audio: 'Extracting audio…',
    transcribing: 'Transcribing audio…',
    generating_page: 'Generating documentation…',
    done: 'Documentation ready',
}
