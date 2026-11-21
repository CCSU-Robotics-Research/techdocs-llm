
import { useEffect, useRef, useState } from 'react'
import { Navigate } from 'react-router-dom'
import Button from '../../../components/ui/Button/Button.tsx'
import { useAppState } from '../../../hooks/globalHook.ts'
import { getDocument } from '../services/service.ts'

export default function DocumentEditor() {
    const { result } = useAppState()

    // State to store the generated document
    const [documentHtml, setDocumentHtml] = useState('')

    // State to track editing and reloading the document
    const [editing, setEditing] = useState(false)
    const [version, setVersion] = useState(0)

    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    // Reference to the iframe
    const iframeRef = useRef<HTMLIFrameElement>(null)

    // Retrieve the gnerated document from the backend
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
    }

    // Keep the edited document once thet are done with editing
    // Do not send the updated document to the backend yet, just store it in state
    // Will have to send it to the backend when the user confirms the document is ready to be finalized 
    function handleSave() {
        const doc = iframeRef.current?.contentDocument

        if (!doc?.body) return

        setEditable(false)

        // Store the updated HTML
        setDocumentHtml('<!DOCTYPE html>' + doc.documentElement.outerHTML)
        setEditing(false)
    }

    // Cancel editing and reload the previous document
    function handleCancel() {
        setEditing(false)
        setVersion(previous => previous + 1)
    }

    return (
        <div className="document-editor">

            {/* Display loading message while retrieving the document just for testing*/}
            {loading && <p>Loading document...</p>}

            {/* Display error if the document cannot be loaded */}
            {error && <p>{error}</p>}

            {/* Displays the generated document */}
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

                    {/* Buttons for editing the document - Might remove just to keep the interface simple */}
                    <div className="document-editor__actions">

                        {!editing ? (
                            <Button onClick={handleEdit}>
                                Edit Document
                            </Button>
                        ) : (
                            <>
                                <Button onClick={handleSave}>
                                    Done Editing
                                </Button>

                                <Button onClick={handleCancel}>
                                    Cancel
                                </Button>
                            </>
                        )}

                    </div>
                </>
            )}

        </div>
    )
}
