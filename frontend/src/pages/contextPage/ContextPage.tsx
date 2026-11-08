import { useEffect, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import FeatureComponent from '../../features/contextModification/components/ContextForm.tsx'
import { useContextModification } from '../../features/contextModification/hooks/useContextForm.ts'
import ProgressBar from '../../features/progressStages/components/progressBar/ProgressBar.tsx'
import { STAGE_LABELS } from '../../features/progressStages/components/constants.ts'
import { useJobProgress } from '../../features/progressStages/hooks/useJobProgress.ts'
import { useAppState } from '../../hooks/globalHook.ts'

export default function ContextPage(){
    const navigate = useNavigate()
    const { video, setResult } = useAppState()
    const { context, setContext, status, errorMessage, isTooLong, canSubmit, handleSubmit } = useContextModification()
    const [uploadId, setUploadId] = useState<string | null>(null)
    const { job, errorMessage: progressError } = useJobProgress(uploadId)

    //Open the preview once the backend reports the documentation is ready.
    useEffect(() => {
        if (job?.stage === 'done' && job.html_file) {
            setResult({ upload_id: job.upload_id, status: job.stage, html_file: job.html_file })
            navigate('/preview')
        }
    }, [job, setResult, navigate])

    if (!video) return <Navigate to="/upload" replace />

    //Processing continues after the upload finishes, until the job is done or fails.
    const isProcessing = uploadId !== null && !job?.failed && !progressError
    const showProgress = status === 'submitting' || isProcessing

    return(
        <>
            <FeatureComponent
                videoName={video.name}
                videoSizeBytes={video.size}
                context={context}
                status={isProcessing ? 'submitting' : status}
                errorMessage={errorMessage ?? progressError ?? job?.detail ?? null}
                canSubmit={canSubmit && !isProcessing}
                isTooLong={isTooLong}
                onContextChange={setContext}
                onBack={()=> navigate('/upload')}
                onSubmit={async () =>{
                    const started = await handleSubmit()
                    if(started) setUploadId(started.upload_id)
                }}
            />
            {showProgress && (
                <ProgressBar
                    label={job ? STAGE_LABELS[job.stage] : 'Uploading video…'}
                    progress={job?.progress ?? 0}
                />
            )}
        </>
    )
}
