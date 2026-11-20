import { Navigate, useNavigate } from 'react-router-dom'
import Button from '../../components/ui/Button/Button.tsx'
import { KEYFRAME_PROGRESS } from '../../features/progressStages/components/constants.ts'
import ProgressBar from '../../features/progressStages/components/progressBar/ProgressBar.tsx'
import { useAppState } from '../../hooks/globalHook.ts'

export default function PreviewPage(){
    const navigate = useNavigate()
    const { result, theme } = useAppState()
    if (!result) return <Navigate to="/upload" replace />
    if (result.status !== 'keyframes_finalized') return <Navigate to="/image-selection" replace />

    return(
        <section className="preview">
            <h2>Generated Documentation</h2>
            <ProgressBar label="Documentation ready" progress={KEYFRAME_PROGRESS.complete} />
            {/* Empty sandbox keeps any scripts in the generated HTML from running */}
            <iframe
                className="preview__document"
                title="Generated documentation"
                sandbox=""
                src={`/api/documents/${result.upload_id}?theme=${theme}`}
            />
            <Button onClick={() => navigate('/upload')}>Process Another Video</Button>
        </section>
    )
}
