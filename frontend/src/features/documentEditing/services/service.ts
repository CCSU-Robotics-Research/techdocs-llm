
// Retrieve the generated HTML document from FastAPI
export async function getDocument(uploadId: string): Promise<string> {

    const response = await fetch(`/api/documents/${uploadId}`)

    // If the request failed return the error
    if (!response.ok) {
        throw new Error(`Failed to load document: HTTP ${response.status}`)
    }

    return await response.text()
}

// Store the edited changes and return the saved document
// The backend removes anything unsafe, so the returned HTML can differ from what was sent
export async function saveDocument(uploadId: string, html: string): Promise<string> {
    const response = await fetch(`/api/documents/${uploadId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'text/html'
        },
        body: html
    })

    if (!response.ok) {
        throw new Error(`Failed to save document: HTTP ${response.status}`)
    }

    return await response.text()
}