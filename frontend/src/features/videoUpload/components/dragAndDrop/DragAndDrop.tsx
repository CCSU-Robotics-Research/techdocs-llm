import { useRef, useState } from 'react'

import Button from '../../../../components/ui/Button/Button.tsx'
import styles from './DragAndDrop.module.css'

const VALID_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv']

type VideoUploadProps = {
    onFileSelected: (file: File) => void
}

export default function VideoUpload({ onFileSelected }: VideoUploadProps) {

    // Reference and state variables
    const [video, setVideo] = useState<File | null>(null)
    const [message, setMessage] = useState('')
    const [isError, setIsError] = useState(false)

    const fileInputRef = useRef<HTMLInputElement>(null)

    // Validate selected video
    function chooseFile(file?: File) {
        if (!file) return

        // Lowercase comparison, so .MOV, .Mp4, etc. all work
        const name = file.name.toLowerCase()
        const isValid = VALID_EXTENSIONS.some(ext => name.endsWith(ext))

        // If the file is not valid, reset state and show error message
        if (!isValid) {
            setVideo(null)
            setIsError(true)
            setMessage('Please select a valid video file.')
            return
        }

        setVideo(file)
        setMessage('')
        setIsError(false)
    }

    // Handle drag and drop
    function handleDrop(event: React.DragEvent<HTMLDivElement>) {
        event.preventDefault()
        chooseFile(event.dataTransfer.files[0])
    }

    // Hand the confirmed file to the page
    function handleConfirm() {
        if (!video) return
        onFileSelected(video)
    }

    return (

        // Drop box container --> instructions, drop box, file input, and buttons
        <div className={styles.container}>
            <h2>
                Please upload video
            </h2>
            <p className={styles.instructions}>
                Drag and drop a video or select one below.
            </p>

            <div
                className={styles.dropBox}
                onDragOver={(event) => event.preventDefault()}
                onDrop={handleDrop}
            >
                {video ? video.name : 'Drag and Drop Video Here'}
            </div>

            <input
                ref={fileInputRef}
                type="file"
                accept=".mp4,.mov,.avi,.mkv"
                onChange={(event) => {
                    chooseFile(event.target.files?.[0])
                    event.target.value = '' // lets the same file be re-picked
                }}
                hidden
            />

            <Button
                type="button"
                variant="secondary"
                onClick={() => fileInputRef.current?.click()}
            >
                Browse Files
            </Button>

            {video && (
                <Button type="button" onClick={handleConfirm}>
                    Confirm Video
                </Button>
            )}

            {/* Display message -> Error */}
            {message && (
                <p className={isError ? styles.error : styles.success}>
                    {message}
                </p>
            )}
        </div>
    )
}