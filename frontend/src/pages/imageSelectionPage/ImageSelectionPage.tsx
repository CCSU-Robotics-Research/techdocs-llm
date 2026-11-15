
import { Navigate, useNavigate } from 'react-router-dom'
import { useAppState } from '../../hooks/globalHook.ts'
import KeyframeSelection, {
    type Keyframe
} from '../../features/keyframeSelection/components/KeyframeSelection.tsx'

export default function ImageSelectionPage() {
    const navigate = useNavigate()
    const { result } = useAppState()

    if (!result) return <Navigate to="/upload" replace />

    function handleConfirm(selectedFrames: Keyframe[]) {
        console.log('Selected frames:', selectedFrames)
        navigate('/preview')
    }

    return (
        <section className="image-selection">
            <KeyframeSelection
                keyframes={[]}
                prompt=""
                onConfirm={handleConfirm}
            />
        </section>
    )
}
