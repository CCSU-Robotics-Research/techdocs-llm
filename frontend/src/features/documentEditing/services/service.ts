
// Retrieve the generated HTML document from FastAPI
export async function getDocument(uploadId: string): Promise<string> {

    const response = await fetch(`/api/documents/${uploadId}`)

    // If the request failed return the error
    if (!response.ok) {
        throw new Error(`Failed to load document: HTTP ${response.status}`)
    }

    return await response.text()
}
