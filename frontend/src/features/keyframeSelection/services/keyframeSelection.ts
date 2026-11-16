
// Information returned by the backend for each image
export type KeyframeResponse = {
    upload_id: string
    status: string
    intervals: {
        frame: number
        alt_text: string
        start: number
        end: number
        fps: number
        selected: string | null
        images: {
            name: string
            index: number
            timestamp: number
            url: string
        }[]
    }[]

    // case of no images
    missing_frames: number[]
}

// Extract keyframes from the uploaded video
export async function extractKeyframes(uploadId: string): Promise<KeyframeResponse> {
    const response = await fetch(`/api/keyframes/${uploadId}/extract`, {
        method: 'POST'
    })

    // If the request failed return the error
    if (!response.ok) {
        throw new Error(`Failed to extract keyframes: HTTP ${response.status}`)
    }

    return await response.json()
}

// Get the current extracted keyframes
export async function getKeyframes(uploadId: string): Promise<KeyframeResponse> {
    const response = await fetch(`/api/keyframes/${uploadId}`)

    if (!response.ok) {
        throw new Error(`Failed to get keyframes: HTTP ${response.status}`)
    }

    return await response.json()
}

// Save the selected image for documentation card image
export async function selectKeyframe(uploadId: string, frame: number, image: string) {

    const response = await fetch(`/api/keyframes/${uploadId}/select`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ frame, image })
    })

    if (!response.ok) {
        throw new Error(`Failed to select keyframe: HTTP ${response.status}`)
    }

    return await response.json()
}

// Finalize the selected keyframes
export async function finalizeKeyframes(uploadId: string) {
    const response = await fetch(`/api/keyframes/${uploadId}/finalize`, {
        method: 'POST'
    })

    // Get error response
    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || `HTTP ${response.status}`)
    }
    return await response.json()
}
