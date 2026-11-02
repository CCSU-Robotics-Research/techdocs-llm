import { Navigate, useNavigate } from 'react-router-dom'
import Button from '../components/ui/Button/Button.tsx'
import { useAppState } from '../hooks/globalHook.ts'

export default function PreviewPage(){
    const navigate = useNavigate()
    const { result } = useAppState()
    if (!result) return <Navigate to="/upload" replace />

    return(
        <section className="preview">
            <h2>Generated Documentation</h2>
            {/* Empty sandbox keeps any scripts in the generated HTML from running */}
            <iframe
                className="preview__document"
                title="Generated documentation"
                sandbox=""
                src={`/api/documents/${result.upload_id}`}
            />
            <Button onClick={() => navigate('/upload')}>Process Another Video</Button>
        </section>
    )
}
