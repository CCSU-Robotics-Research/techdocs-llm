import { useState } from 'react'
import Button from '../../../components/ui/Button/Button.tsx'
import styles from './KeyframeSelection.module.css'

// Information needed for each extracted frame - revised to match Colin's API
export type Keyframe = {
    id: string
    frame: number
    image: string
    imageUrl: string
    timestamp: number
    altText: string
}

// Props for the KeyframeSelection component
// This function handles uder selecting images, refining images, and confirming selection
type KeyframeSelectionProps = {
    keyframes: Keyframe[]
    onSelect: (frame: number, image: string) => Promise<void>
    onRefine: (frame: number, images: string[]) => Promise<Keyframe[]>
    onConfirm: () => Promise<void>
}

// Definition of the KeyframeSelection component
export default function KeyframeSelection({
    keyframes,
    onSelect,
    onRefine,
    onConfirm
}: KeyframeSelectionProps) {

    // State to track the current page of the slection process
    const [currentIndex, setCurrentIndex] = useState(0)

    // State for selecting two images to refine multiple images and then store them
    const [selectMultiple, setSelectMultiple] = useState(false)
    const [refineImages, setRefineImages] = useState<Keyframe[]>([])
    const [newImages, setNewImages] = useState<Keyframe[] | null>(null)

    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    // Grabs the sorted list of the keyframes and then sorts them 
    const frameNumbers = [...new Set(keyframes.map(frame => frame.frame))]
        .sort((a, b) => a - b)

    const currentFrame = frameNumbers[currentIndex]

    // Only display images for the current selection page
    // After refining, reflects the newly generated images instead
    const currentImages = newImages ??
        keyframes.filter(frame => frame.frame === currentFrame)

    // Prompt text is for the top of the page and is based off the alt text of the images
    const currentPrompt = currentImages[0]?.altText ?? ''

    // Handles loading and error state for any call to the backend
    async function run(action: () => Promise<void>) {

        setLoading(true)
        setError('')

        try {
            await action()
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : 'Something went wrong'
            )
        } finally {
            setLoading(false)
        }
    }

    // Select an image or choose two images for refinement
    async function toggleSelection(frame: Keyframe) {

        // Ignore clicks while a request is still running
        if (loading) return

        if (selectMultiple) {

            // Add or remove the clicked image from the refine list
            const picked = refineImages.some(image => image.id === frame.id)
                ? refineImages.filter(image => image.id !== frame.id)
                : [...refineImages, frame]

            setRefineImages(picked)

            // Two images chosen - generate new ones between them
            if (picked.length === 2) {
                await run(async () => {

                    // Earlier image first so the backend knows the range
                    const [first, second] = [...picked]
                        .sort((a, b) => a.timestamp - b.timestamp)

                    const refined = await onRefine(
                        currentFrame,
                        [first.image, second.image]
                    )

                    setNewImages(refined)
                    setSelectMultiple(false)
                    setRefineImages([])
                })
            }

            return
        }

        await run(async () => {

            // Save the selected image to the backend
            await onSelect(frame.frame, frame.image)

            // Move to the next prompt
            if (currentIndex + 1 < frameNumbers.length) {
                setCurrentIndex(currentIndex + 1)
                setNewImages(null)
                setRefineImages([])
            } else {
                // All prompts have been completed
                await onConfirm()
            }
        })
    }

    // Switch between normal selection and selecting two images
    function toggleMultiple() {
        setSelectMultiple(previous => !previous)
        setRefineImages([])
        setError('')
    }

    // Setting up the UI for the component
    return (
        <div className={styles.container}>

            {/* Instructions for user*/}
            <div className={styles.instructions}>
                <p>
                    1. Select the image that best represents the prompt.
                    <br />
                    2. If no images match, click "Select Multiple Images".
                    <br />
                    3. Choose two images to generate nine new images
                    between the selected frames.
                </p>

                <p>
                    Prompt {currentIndex + 1} of {frameNumbers.length}
                </p>

                <p className={styles.prompt}>
                    Prompt: {currentPrompt}
                </p>

                {selectMultiple && (
                    <p>
                        Select two images ({refineImages.length}/2)
                    </p>
                )}
            </div>

            {/* Keyframe images */}
            {/* Creates a grid of image cards */}
            <div className={styles.imageGrid}>

                {/* Maps through each keyframe and creates an image card */}
                {currentImages.length > 0 ? (
                    currentImages.map((frame) => {

                        const isSelected = refineImages.some(
                            image => image.id === frame.id
                        )

                        return (
                            <div
                                key={frame.id}

                                // This gives a card base and highlight styling
                                // Makes it easier for the user to see which image is selected
                                className={`${styles.imageCard} ${isSelected ? styles.selected : ''}`}
                                onClick={() => toggleSelection(frame)}
                            >
                                {/* Image and alt text */}
                                <img
                                    src={frame.imageUrl}
                                    alt={frame.altText}
                                />

                                {/* Timestamp of the keyframe*/}
                                <div className={styles.timestamp}>
                                    {frame.timestamp.toFixed(1)} seconds
                                </div>
                            </div>
                        )
                    })
                ) : (
                    <p>No keyframes available yet.</p>
                )}
            </div>

            {/* Only show text while new images are being generated */}
            {loading && selectMultiple && <p>Generating new images</p>}
            {error && <p>{error}</p>}

            {/* Select two images if none match the prompt */}
            <div className={styles.actions}>
                <Button
                    type="button"
                    onClick={toggleMultiple}
                >
                    {selectMultiple
                        ? 'Cancel Multiple Selection'
                        : 'Select Multiple Images'}
                </Button>
            </div>

        </div>
    )
}