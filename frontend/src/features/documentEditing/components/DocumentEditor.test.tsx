import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import DocumentEditor from './DocumentEditor.tsx'
import { useAppState } from '../../../hooks/globalHook.ts'
import { getDocument, saveDocument } from '../services/service.ts'

vi.mock('../../../hooks/globalHook.ts', () => ({
    useAppState: vi.fn(),
}))

vi.mock('../services/service.ts', () => ({
    getDocument: vi.fn(),
    saveDocument: vi.fn(),
}))

const uploadId = '8aa96b1cba6842da92122a17db757aac'
const originalHtml = '<!DOCTYPE html><html><head></head><body><p>original</p></body></html>'
const savedHtml = '<!DOCTYPE html><html><head></head><body><p>saved by the backend</p></body></html>'

function renderEditor() {
    return render(
        <MemoryRouter initialEntries={['/document-editor']}>
            <Routes>
                <Route path="/document-editor" element={<DocumentEditor />} />
                <Route path="/preview" element={<p>Preview page</p>} />
            </Routes>
        </MemoryRouter>,
    )
}

//Wait for the document to load and return its iframe.
async function findFrame() {
    return await screen.findByTitle('Generated documentation') as HTMLIFrameElement
}

//Start editing and change the text inside the iframe, the way a user typing would.
async function editDocument(text: string) {
    const frame = await findFrame()
    fireEvent.click(screen.getByRole('button', { name: 'Edit Document' }))
    const body = frame.contentDocument!.body
    body.setAttribute('contenteditable', 'true')
    body.innerHTML = `<p>${text}</p>`
    return frame
}

//Click a button and let the save request finish.
async function clickAndWait(name: string) {
    await act(async () => {
        fireEvent.click(screen.getByRole('button', { name }))
    })
}

describe('DocumentEditor', () => {
    afterEach(() => {
        cleanup()
    })

    beforeEach(() => {
        vi.clearAllMocks()
        vi.mocked(useAppState).mockReturnValue({
            video: null,
            context: '',
            result: { upload_id: uploadId, status: 'keyframes_finalized', html_file: 'input_workdocs.html' },
            setVideo: () => undefined,
            setContext: () => undefined,
            setResult: () => undefined,
        })
        vi.mocked(getDocument).mockResolvedValue(originalHtml)
        vi.mocked(saveDocument).mockResolvedValue(savedHtml)
    })

    it('loads and shows the document for the current upload', async () => {
        renderEditor()

        expect(screen.getByText('Loading document...')).toBeTruthy()
        expect((await findFrame()).getAttribute('srcdoc')).toBe(originalHtml)
        expect(getDocument).toHaveBeenCalledWith(uploadId)
        expect(screen.getByRole('button', { name: 'Edit Document' })).toBeTruthy()
    })

    it('shows an error instead of the document when it cannot be loaded', async () => {
        vi.mocked(getDocument).mockRejectedValue(new Error('Failed to load document: HTTP 404'))
        renderEditor()

        expect(await screen.findByText('Failed to load document: HTTP 404')).toBeTruthy()
        expect(screen.queryByTitle('Generated documentation')).toBeNull()
    })

    it('saves the edits without contenteditable and shows what the backend saved', async () => {
        renderEditor()
        await editDocument('USER EDIT')

        await clickAndWait('Done Editing')

        const [id, sentHtml] = vi.mocked(saveDocument).mock.calls[0]
        expect(id).toBe(uploadId)
        expect(sentHtml).toContain('USER EDIT')
        expect(sentHtml).not.toContain('contenteditable')
        expect((await findFrame()).getAttribute('srcdoc')).toBe(savedHtml)
        expect(screen.getByRole('button', { name: 'Edit Document' })).toBeTruthy()
    })

    it('keeps the document and edits on screen when saving fails, then saves on retry', async () => {
        vi.mocked(saveDocument).mockRejectedValueOnce(new Error('Failed to save document: HTTP 500'))
        renderEditor()
        const frame = await editDocument('USER EDIT')

        await clickAndWait('Done Editing')

        expect(screen.getByRole('alert').textContent).toBe('Failed to save document: HTTP 500')
        expect(screen.getByTitle('Generated documentation')).toBe(frame)
        expect(frame.contentDocument!.body.innerHTML).toContain('USER EDIT')

        await clickAndWait('Done Editing')

        expect(vi.mocked(saveDocument).mock.calls[1][1]).toContain('USER EDIT')
        expect(screen.queryByRole('alert')).toBeNull()
    })

    it('throws away unsaved edits when editing is cancelled', async () => {
        renderEditor()
        const frame = await editDocument('UNWANTED EDIT')

        fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))

        const reloaded = await findFrame()
        expect(reloaded).not.toBe(frame)
        expect(reloaded.getAttribute('srcdoc')).toBe(originalHtml)
        expect(saveDocument).not.toHaveBeenCalled()
        expect(screen.getByRole('button', { name: 'Edit Document' })).toBeTruthy()
    })

    it('goes to the preview without saving when there are no unsaved edits', async () => {
        renderEditor()
        await findFrame()

        await clickAndWait('Finish')

        expect(screen.getByText('Preview page')).toBeTruthy()
        expect(saveDocument).not.toHaveBeenCalled()
    })

    it('saves unsaved edits before going to the preview', async () => {
        renderEditor()
        await editDocument('USER EDIT')

        await clickAndWait('Finish')

        expect(vi.mocked(saveDocument).mock.calls[0][1]).toContain('USER EDIT')
        expect(screen.getByText('Preview page')).toBeTruthy()
    })

    it('stays on the editor when saving fails while finishing', async () => {
        vi.mocked(saveDocument).mockRejectedValue(new Error('Failed to save document: HTTP 500'))
        renderEditor()
        await editDocument('USER EDIT')

        await clickAndWait('Finish')

        expect(screen.queryByText('Preview page')).toBeNull()
        expect(screen.getByRole('alert').textContent).toBe('Failed to save document: HTTP 500')
    })

    it('warns before leaving the page only while there are unsaved edits', async () => {
        renderEditor()
        await findFrame()
        const leave = () => {
            const event = new Event('beforeunload', { cancelable: true })
            window.dispatchEvent(event)
            return event.defaultPrevented
        }

        expect(leave()).toBe(false)
        await editDocument('USER EDIT')
        expect(leave()).toBe(true)
        await clickAndWait('Done Editing')
        expect(leave()).toBe(false)
    })
})
