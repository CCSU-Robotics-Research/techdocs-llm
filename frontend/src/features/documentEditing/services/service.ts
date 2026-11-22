
// Retrieve the generated HTML document from FastAPI
export async function getDocument(uploadId: string): Promise<string> {

    const response = await fetch(`/api/documents/${uploadId}`)

    // If the request failed return the error
    if (!response.ok) {
        throw new Error(`Failed to load document: HTTP ${response.status}`)
    }

    return await response.text()
}

// This is able to store the edited changes - need to create endpoint in main.py
export async function saveDocument(uploadId: string, html: string) {
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

    return await response.json()
}