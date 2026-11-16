import { Navigate, useNavigate } from 'react-router-dom'
import Button from '../../components/ui/Button/Button.tsx'
import { useAppState } from '../../hooks/globalHook.ts'

export default function ResultPage() {
    const navigate = useNavigate()
    const { result } = useAppState()
    if (!result) return <Navigate to="/upload" replace />

    return (
        <section className="result">
            <h3>Video Processing Successful!</h3>
            {/* Empty sandbox keeps any scripts in the generated HTML from running */}
            <p>Documentation and keyframes have been saved!</p>
            <Button onClick={() => navigate('/upload')}>Back to Main Page</Button>
        </section>
    )
}
