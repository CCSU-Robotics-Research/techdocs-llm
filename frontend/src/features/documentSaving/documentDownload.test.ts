import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { downloadDocument } from './documentDownload.ts'

function jsonResponse(body: unknown, status: number) {
    return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

describe('downloadDocument', () => {
    let clicked: HTMLAnchorElement[]

    beforeEach(() => {
        clicked = []
        // jsdom has no object URLs or file saving, so record the link the browser would click
        URL.createObjectURL = vi.fn(() => 'blob:mock')
        URL.revokeObjectURL = vi.fn()
        vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (this: HTMLAnchorElement) {
            clicked.push(this)
        })
    })

    afterEach(() => {
        vi.restoreAllMocks()
        vi.unstubAllGlobals()
    })

    it('requests the zip and saves it under the name the backend suggests', async () => {
        const fetchMock = vi.fn().mockResolvedValue(new Response('zip-bytes', {
            status: 200,
            headers: { 'Content-Disposition': 'attachment; filename="documentation-abc123.zip"' },
        }))
        vi.stubGlobal('fetch', fetchMock)

        const filename = await downloadDocument('abc123')

        expect(fetchMock).toHaveBeenCalledWith('/api/documents/abc123/download?format=html')
        expect(filename).toBe('documentation-abc123.zip')
        expect(clicked).toHaveLength(1)
        expect(clicked[0].download).toBe('documentation-abc123.zip')
        expect(clicked[0].href).toBe('blob:mock')
    })

    it('falls back to a default file name when the header is missing', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('zip-bytes', { status: 200 })))

        expect(await downloadDocument('abc123')).toBe('documentation-abc123.zip')
    })

    it('throws the backend message for a string error detail', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ detail: 'Document or selected keyframe file not found.' }, 404)))

        await expect(downloadDocument('abc123')).rejects.toThrow('Document or selected keyframe file not found.')
        expect(clicked).toHaveLength(0)
    })

    it('throws the message from an object error detail', async () => {
        const detail = { message: 'Not all keyframes have been selected', missing_frames: [2, 3] }
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ detail }, 409)))

        await expect(downloadDocument('abc123')).rejects.toThrow('Not all keyframes have been selected')
    })

    it('reports the status code when the error is not JSON', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('Bad gateway', { status: 502 })))

        await expect(downloadDocument('abc123')).rejects.toThrow('Failed to save the document: HTTP 502')
    })
})
