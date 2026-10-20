import {useNavigate} from 'react-router-dom'
import {useAppState} from '../hooks/globalHook.ts'


export default function HomePage() {
  const navigate = useNavigate()
  const { setVideo } = useAppState()
  return (
    <section className="upload">
      <h2>Choose a video to process</h2>
      <input
        type="file"
        accept=".mp4,.mov,.avi,.mkv,video/*"
        onChange={(event) => {
          const file = event.target.files?.[0]
          if (!file) return
          setVideo(file)
          navigate('/context')
        }}
      />
    </section>
  )
}