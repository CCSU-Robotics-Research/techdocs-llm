import { useNavigate } from 'react-router-dom'
import { useAppState } from '../hooks/globalHook.ts'
import DragAndDrop from '../features/videoUpload/components/dragAndDrop/DragAndDrop.tsx'


export default function HomePage() {
  const navigate = useNavigate()
  const { setVideo } = useAppState()
  return (
    <section className="upload">
      <DragAndDrop
        onFileSelected={(file) => {
          setVideo(file)
          navigate('/context')
        }}
      />
    </section>
  )
}