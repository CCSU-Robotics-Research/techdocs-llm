
import { useEffect, useRef, useState } from 'react'
import Button from '../../../components/ui/Button/Button.tsx'
import { useAppState } from '../../../hooks/globalHook.ts'
import { getDocument, saveDocument } from '../services/service.ts'

export default function DocumentEditor() {
    const { result } = useAppState()

    // State to store the generated document
    const [documentHtml, setDocumentHtml] = useState('')

    // State to track if the document is being edited
    const [editing, setEditing] = useState(false)

    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState('')

    // Kept separate from the loading error so a failed save does not hide the document and lose the edits
    const [saveError, setSaveError] = useState('')

    // Reference to the iframe
    const iframeRef = useRef<HTMLIFrameElement>(null)

    // Retrieve the generated document from the backend
    useEffect(() => {
        if (!result) return

        let cancelled = false

        async function loadDocument() {
            setLoading(true)
            setError('')

            try {
                const html = await getDocument(result!.upload_id)

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
    }, [result?.upload_id])

    // Nothing to display if no video was uploaded
    if (!result) return <p>No document available. Please upload a video first.</p>

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

    // Save the edited document to the backend
    async function handleSave() {
        const doc = iframeRef.current?.contentDocument

        if (!doc?.body || !result) return

        // Get the updated HTML
        const html = '<!DOCTYPE html>' + doc.documentElement.outerHTML

        setSaving(true)
        setSaveError('')

        try {
            // Send the edited document to FastAPI
            await saveDocument(result.upload_id, html)

            // Keep the updated document
            setDocumentHtml(html)
            setEditable(false)
            setEditing(false)

        } catch (error) {
            // Keep the document and edits on screen so the user can try saving again
            setSaveError(error instanceof Error ? error.message : 'Failed to save document')
        } finally {
            setSaving(false)
        }
    }

    // Open the saved document in a new tab
    function handlePreview() {
        if (!result) return

        window.open(`/api/documents/${result.upload_id}`, '_blank')
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
                            <>
                                <Button onClick={handleEdit}>
                                    Edit Document
                                </Button>

                                <Button onClick={handlePreview}>
                                    View Saved Document
                                </Button>
                            </>
                        ) : (
                            <Button onClick={handleSave} disabled={saving}>
                                {saving ? 'Saving...' : 'Done Editing'}
                            </Button>
                        )}

                    </div>
                </>
            )}

        </div>
    )
}
