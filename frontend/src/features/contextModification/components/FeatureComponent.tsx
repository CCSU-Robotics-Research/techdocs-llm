

import type { ProcessStatus } from '../types.ts'

type FeatureComponentProps = {
    videoName: string
    videoSizeBytes: number
    context: string
    status: ProcessStatus
    errorMessage: string | null
    canSubmit: boolean
    isTooLong: boolean
    onContextChange: (value: string) => void
    onBack: () => void
    onSubmit: () => void
}

export default function FeatureComponent(props: FeatureComponentProps){
    const{
        videoName, videoSizeBytes, context, status, errorMessage, canSubmit, isTooLong, onContextChange, onBack, onSubmit
    } = props

    const isSubmitting = status === 'submitting'
    const contextError = errorMessage ?? (isTooLong ? 'Context is too long.' : undefined)
    //missing a function to format the size of the video in bytes...
    return(
        <section className="context">
            <h2>Please Confirm: Is this the video file you want to process?</h2>
            <p className="context__meta">
                <strong>Video File:</strong>{videoName}
                <br />
                <strong>Size:</strong> {formatBytes(videoSizeBytes)}
            </p>
            <form className="context__form" onSubmit={(event) => {event.preventDefault(); onSubmit()}}>
                <label>Optionally, enter context for the video: </label>
                <textarea name="context" rows={10} value={context} disabled={isSubmitting} aria-invalid={Boolean(contextError)}
                onChange={(event) => onContextChange(event.target.value)}/>
                {contextError && <p role="alert">{contextError}</p>}
            </form>
        </section>
    )
}
