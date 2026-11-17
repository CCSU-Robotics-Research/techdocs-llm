import type { JobStage } from './types.ts'

//How often to check the progress of a job, in milliseconds.
export const POLL_INTERVAL_MS = 1500

//Message displayed under the progress bar for each stage.
export const STAGE_LABELS: Record<JobStage, string> = {
    uploaded: 'Video uploaded',
    extracting_audio: 'Extracting audio…',
    transcribing: 'Transcribing audio and drafting instructions…',
    generating_page: 'Building document…',
    done: 'Extracting candidate images…',
}

//Workflow milestones leave room for keyframe selection after the draft is ready.
export const KEYFRAME_PROGRESS = { extracting: 80, selecting: 90, complete: 100 }

export const STAGE_PROGRESS: Record<JobStage, number> = {
    uploaded: 10,
    extracting_audio: 25,
    transcribing: 50,
    generating_page: 65,
    done: KEYFRAME_PROGRESS.extracting,
}
