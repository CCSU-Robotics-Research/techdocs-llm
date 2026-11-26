export type DocumentFormat = 'html'

function describeError(detail: unknown, status: number): string {
    if (typeof detail === 'string' && detail) return detail

    if (detail && typeof detail === 'object' && 'message' in detail && typeof detail.message === 'string') {
        return detail.message
    }

    return `Failed to save the document: HTTP ${status}`
}

function filenameFromHeader(header: string | null): string | null {
    const match = header?.match(/filename="?([^";]+)"?/i)
    return match ? match[1] : null
}

function saveBlob(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()

    setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export async function downloadDocument(uploadId: string, format: DocumentFormat = 'html'): Promise<string> {
    const response = await fetch(`/api/documents/${uploadId}/download?format=${format}`)

    if (!response.ok) {
        const body = await response.json().catch(() => null)
        throw new Error(describeError(body?.detail, response.status))
    }

    const filename = filenameFromHeader(response.headers.get('Content-Disposition')) ?? `documentation-${uploadId}.zip`
    saveBlob(await response.blob(), filename)

    return filename
}
