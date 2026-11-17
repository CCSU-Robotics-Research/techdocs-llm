
import { useEffect, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAppState } from '../../hooks/globalHook.ts'
import { KEYFRAME_PROGRESS, STAGE_LABELS } from '../../features/progressStages/components/constants.ts'
import ProgressBar from '../../features/progressStages/components/progressBar/ProgressBar.tsx'
import KeyframeSelection, {
    type Keyframe
} from '../../features/keyframeSelection/components/KeyframeSelection.tsx'

// These are the services that communicate with the FastAPI backend 
// to extract, select, refine, and finalize keyframes
import {
    extractKeyframes,
    getKeyframes,
    selectKeyframe,
    refineKeyframe,
    finalizeKeyframes
} from '../../features/keyframeSelection/services/keyframeSelection.ts'

// Component which handles the user selecting of keyframes
export default function ImageSelectionPage() {
    const navigate = useNavigate()
    const { result, setResult } = useAppState()

    // Store the state variables for images, laoding, and error statees
    const [keyframes, setKeyframes] = useState<Keyframe[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    // Convert the backend intervals into keyframes for the component
    function convertKeyframes(data: Awaited<ReturnType<typeof getKeyframes>>) {
        const images: Keyframe[] = []

        for (const interval of data.intervals) {
            for (const image of interval.images) {
                images.push({
                    id: `${interval.frame}-${image.name}`,
                    frame: interval.frame,
                    image: image.name,
                    imageUrl: image.url,
                    timestamp: image.timestamp,
                    altText: interval.alt_text
                })
            }
        }

        return images
    }

    // Extract keyframes when the page loads
    useEffect(() => {
        if (!result) return

        let cancelled = false

        async function loadKeyframes() {
            try {
                const data = await extractKeyframes(result!.upload_id)

                if (!cancelled) {
                    setKeyframes(convertKeyframes(data))
                }
            } catch (error) {
                if (!cancelled) {
                    setError(error instanceof Error ? error.message : 'Failed to load keyframes')
                }
            } finally {
                if (!cancelled) setLoading(false)
            }
        }

        loadKeyframes()

        return () => {
            cancelled = true
        }
    }, [result?.upload_id])

    if (!result) return <Navigate to="/upload" replace />

    // Save the selected image for the current documentation frame
    async function handleSelect(frame: number, image: string) {
        await selectKeyframe(result!.upload_id, frame, image)
    }

    // Generate nine new images between the two selected images
    async function handleRefine(frame: number, images: string[]) {
        await refineKeyframe(result!.upload_id, frame, images)

        // Get the updated images after refinement
        const data = await getKeyframes(result!.upload_id)
        const updated = convertKeyframes(data)

        setKeyframes(updated)

        return updated.filter(image => image.frame === frame)
    }

    // Open the finished document after the image selections are finalized.
    async function handleConfirm() {
        if (!result) return
        await finalizeKeyframes(result.upload_id)
        setResult({ ...result, status: 'keyframes_finalized' })
        navigate('/preview')
    }

    return (
        <section className="image-selection">

            {!error && (
                <ProgressBar
                    label={loading ? STAGE_LABELS.done : 'Select an image for each prompt'}
                    progress={loading ? KEYFRAME_PROGRESS.extracting : KEYFRAME_PROGRESS.selecting}
                />
            )}

            {/* Display error if extraction fails */}
            {error && <p>{error}</p>}

            {/* This will display all the extracted images */}
            {!loading && !error && (
                <KeyframeSelection
                    keyframes={keyframes}
                    onSelect={handleSelect}
                    onRefine={handleRefine}
                    onConfirm={handleConfirm}
                />
            )}

        </section>
    )
}
