import { useNavigate } from 'react-router-dom'
import { useAppState } from '../../hooks/globalHook.ts'
import DragAndDrop from '../../features/videoUpload/components/dragAndDrop/DragAndDrop.tsx'
import BackendStatus from '../../components/ui/BackendStatus/BackendStatus.tsx'

export default function HomePage() {
    const navigate = useNavigate()
    const { setVideo } = useAppState()

    return (
        <section className="upload">
            {/*Store the confirmed video and navigate to the context page.*/}
            <DragAndDrop
                statusIndicator={<BackendStatus />}
                onFileSelected={(file) => {
                    setVideo(file)
                    navigate('/context')
                }}
            />
        </section>
    )
}
