
import { Navigate } from 'react-router-dom'
import { useAppState } from '../../hooks/globalHook.ts'
import DocumentEditor from '../../features/documentEditing/components/DocumentEditor.tsx'

export default function DocumentEditorPage() {
    const { result } = useAppState()

    // Return to upload if no video has been processed
    if (!result) return <Navigate to="/upload" replace />

    return (
        <section className="document-editor-page">

            {/* Display the document editor */}
            <h2>Edit Generated Documentation</h2>

            <DocumentEditor />

        </section>
    )
}
