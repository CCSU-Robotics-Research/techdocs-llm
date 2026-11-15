import { useState } from 'react'
import Button from '../../../components/ui/Button/Button.tsx'
import styles from './KeyframeSelection.module.css'

// Information needed to display each extracted frame - from transcribe.py
export type Keyframe = {
    id: string
    frame: number
    image: string
    imageUrl: string
    timestamp: number
    altText: string
}

// What inputs are being required from the parent page
type KeyframeSelectionProps = {
    keyframes: Keyframe[]
    prompt?: string
    onConfirm: (selectedFrames: Keyframe[]) => void
}

//
export default function KeyframeSelection({
    keyframes,
    prompt,
    onConfirm

}: KeyframeSelectionProps) {

    // State to track which images are selected
    const [selectedFrames, setSelectedFrames] = useState<string[]>([])

    // Selects or deselects an image
    function toggleSelection(id: string) {

        const clickedFrame = keyframes.find(frame => frame.id === id)

        if (!clickedFrame) return

        // Check if clicked image is in the selected list - add or remove accordingly
        setSelectedFrames(previous => {

            if (previous.includes(id)) {
                return previous.filter(frame => frame !== id)
            }

            // Only allow one selected image per documentation frame
            const otherFrames = previous.filter(selectedId => {
                const selectedFrame = keyframes.find(frame => frame.id === selectedId)
                return selectedFrame?.frame !== clickedFrame.frame
            })

            return [...otherFrames, id]
        })
    }

    // Send selected images to the parent page
    function handleConfirm() {

        // This will filter the keyframes array to include the selected frames based on IDs
        const selected = keyframes.filter(frame =>
            selectedFrames.includes(frame.id)
        )

        onConfirm(selected)
    }

    // Setting up the UI for the component
    return (
        <div className={styles.container}>

            {/* Instructions for user*/}
            <div className={styles.instructions}>
                <p>
                    Select one keyframe for each image in the generated documentation.
                    Click an image to select or deselect it.
                </p>

                {prompt && (
                    <p className={styles.prompt}>
                        Prompt: {prompt}
                    </p>
                )}
            </div>

            {/* Keyframe images */}
            {/* Creates a grid of image cards */}
            <div className={styles.imageGrid}>

                {/* Maps through each keyframe and creates an image card */}
                {keyframes.length > 0 ? (
                    keyframes.map((frame) => {
                        const isSelected = selectedFrames.includes(frame.id)

                        return (
                            <div
                                key={frame.id}
                                // This gives a card base and highlight styling
                                className={`${styles.imageCard} ${isSelected ? styles.selected : ''}`}
                                onClick={() => toggleSelection(frame.id)}
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
                    // If there are no keyframes that were generated in the grid
                ) : (
                    <p>No keyframes available yet.</p>
                )}
            </div>

            {/* Continue to generated document - Temporary: subject to be changed */}
            <div className={styles.actions}>
                <Button
                    type="button"
                    onClick={handleConfirm}
                >
                    Continue to Generated Documentation ({selectedFrames.length})
                </Button>
            </div>

        </div>
    )
}