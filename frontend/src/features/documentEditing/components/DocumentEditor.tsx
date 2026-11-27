
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '../../../components/ui/Button/Button.tsx'
import { useAppState } from '../../../hooks/globalHook.ts'
import { getDocument, saveDocument } from '../services/service.ts'

export default function DocumentEditor() {
    const navigate = useNavigate()
    const { result } = useAppState()
    const uploadId = result?.upload_id

    // State to store the generated document
    const [documentHtml, setDocumentHtml] = useState('')

    // State to track if the document is being edited
    const [editing, setEditing] = useState(false)

    // Changing the version reloads the iframe, which throws away unsaved edits
    const [version, setVersion] = useState(0)

    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState('')

    // Kept separate from the loading error so a failed save does not hide the document and lose the edits
    const [saveError, setSaveError] = useState('')

    // Reference to the iframe
    const iframeRef = useRef<HTMLIFrameElement>(null)

    // Retrieve the generated document from the backend
    useEffect(() => {
        if (!uploadId) return
        const documentId = uploadId

        let cancelled = false

        async function loadDocument() {
            setLoading(true)
            setError('')

            try {
                const html = await getDocument(documentId)

                if (!cancelled) {
                    setDocumentHtml(html)
                }
            } catch (error) {
                if (!cancelled) {
                    setError(error instanceof Error ? error.message : 'Failed to load document')
                }
            } finally {
                if (!cancelled) setLoading(false)
            }
        }

        loadDocument()

        return () => {
            cancelled = true
        }
    }, [uploadId])

    // Warn before refreshing or closing the tab while there are unsaved edits
    useEffect(() => {
        if (!editing) return

        function handleBeforeUnload(event: BeforeUnloadEvent) {
            event.preventDefault()
            // Older browsers need returnValue set to show the warning
            event.returnValue = ''
        }

        window.addEventListener('beforeunload', handleBeforeUnload)

        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload)
        }
    }, [editing])

    // Nothing to display if no video was uploaded
    if (!uploadId) return <p>No document available. Please upload a video first.</p>
    // Keep the checked ID for the functions below, which TypeScript does not narrow
    const documentId = uploadId

    // Enable or disable editing inside the iframe
    // Used the contentEditable property to allow the user to edit the document
    function setEditable(value: boolean) {
        const body = iframeRef.current?.contentDocument?.body

        if (body) {
            body.contentEditable = String(value)
        }
    }

    // Set editing when the document loads
    function handleLoad() {
        setEditable(editing)
    }

    // Allow the user to edit the document
    function handleEdit() {
        setEditable(true)
        setEditing(true)
        setSaveError('')
    }

    // Save the edited document to the backend and return whether it worked
    async function handleSave() {
        const doc = iframeRef.current?.contentDocument

        if (!doc?.body) return false

        // Get the updated HTML from a copy of the page without contentEditable, so the saved document is not editable
        // The copy keeps the page on screen editable in case the save fails
        const page = doc.documentElement.cloneNode(true) as HTMLElement
        page.querySelector('body')?.removeAttribute('contenteditable')
        const html = '<!DOCTYPE html>' + page.outerHTML

        setSaving(true)
        setSaveError('')

        try {
            // Send the edited document to FastAPI
            const savedHtml = await saveDocument(documentId, html)

            // Show the document the backend saved, since it removes anything unsafe
            setDocumentHtml(savedHtml)
            setVersion(previous => previous + 1)
            setEditable(false)
            setEditing(false)
            return true

        } catch (error) {
            // Keep the document and edits on screen so the user can try saving again
            setSaveError(error instanceof Error ? error.message : 'Failed to save document')
            return false
        } finally {
            setSaving(false)
        }
    }

    // Throw away unsaved edits by reloading the last saved document
    function handleCancel() {
        setEditing(false)
        setSaveError('')
        setVersion(previous => previous + 1)
    }

    // Save any unsaved edits, then show the finished document
    async function handleFinish() {
        if (editing && !(await handleSave())) return

        navigate('/preview')
    }

    return (
        <div className="document-editor">

            {/* Display loading message while retrieving the document */}
            {loading && <p>Loading document...</p>}

            {/* Display error if the document cannot be loaded */}
            {error && <p>{error}</p>}

            {/* Display the generated document */}
            {!loading && !error && (
                <>
                    <iframe
                        key={version}
                        ref={iframeRef}
                        className="preview__document"
                        title="Generated documentation"
                        sandbox="allow-same-origin"
                        srcDoc={documentHtml}
                        onLoad={handleLoad}
                    />

                    {/* Display error if the document cannot be saved */}
                    {saveError && <p role="alert">{saveError}</p>}

                    {/* Buttons for editing the document */}
                    <div className="document-editor__actions">

                        {!editing ? (
                            <Button onClick={handleEdit}>
                                Edit Document
                            </Button>
                        ) : (
                            <>
                                <Button onClick={handleSave} disabled={saving}>
                                    {saving ? 'Saving...' : 'Done Editing'}
                                </Button>

                                <Button variant="secondary" onClick={handleCancel} disabled={saving}>
                                    Cancel
                                </Button>
                            </>
                        )}

                        {/* Saves any unsaved edits before showing the finished document */}
                        <Button onClick={handleFinish} disabled={saving}>
                            Finish
                        </Button>

                    </div>
                </>
            )}

        </div>
    )
}
