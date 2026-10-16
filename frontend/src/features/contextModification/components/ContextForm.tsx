import Input from '../../../components/ui/Input/Input.tsx'
import Button from '../../../components/ui/Button/Button.tsx'
import { formatBytes } from '../../../utils/FormatBytes.ts'
import type { ProcessStatus } from './types.ts'

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
    return(
        <section className="context">
            <h2>Please Confirm: Is this the video file you want to process?</h2>
            <p className="context__meta">
                <strong>Video File: </strong>{videoName}
                <br />
                <strong>Size: </strong> {formatBytes(videoSizeBytes)}
            </p>
            <form className="context__form" onSubmit={(event) => {event.preventDefault(); onSubmit()}}>
                <Input name="context" label="Optionally, enter context for the video:" rows={10} value={context}
                        disabled={isSubmitting} error={contextError}
                        onChange={(event) => onContextChange(event.target.value)}/>
                <div className="context__actions">
                    <Button type="button" variant="secondary" onClick={onBack} disabled={isSubmitting}>
                        No, Back to the Main Page
                    </Button>
                    <Button type="submit" disabled={!canSubmit}>
                        {isSubmitting ? 'Processing...': 'Process Video'}
                    </Button>
                </div>
            </form>
        </section>
    )
}
