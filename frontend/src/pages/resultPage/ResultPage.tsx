import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import Button from '../../components/ui/Button/Button.tsx'
import { downloadDocument } from '../../features/documentSaving/services/documentDownload.ts'
import { useAppState } from '../../hooks/globalHook.ts'

export default function ResultPage() {
    const navigate = useNavigate()
    const { result } = useAppState()

    const [saving, setSaving] = useState(false)
    const [savedFile, setSavedFile] = useState('')
    const [error, setError] = useState('')

    if (!result) return <Navigate to="/upload" replace />
    if (result.status !== 'keyframes_finalized') return <Navigate to="/image-selection" replace />

    const uploadId = result.upload_id

    async function handleSave() {
        setSaving(true)
        setSavedFile('')
        setError('')

        try {
            setSavedFile(await downloadDocument(uploadId))
        } catch (error) {
            setError(error instanceof Error ? error.message : 'Failed to save the document')
        } finally {
            setSaving(false)
        }
    }

    return (
        <section className="result">
            <h2>Video Processing Successful!</h2>
            <p className="result__meta">
                Your documentation and the keyframe images you selected are ready to save.
            </p>
            <p className="result__meta">
                The download is a .zip file containing <strong>{result.html_file}</strong> and the selected keyframe images.
            </p>

            <div className="result__actions">
                <Button onClick={handleSave} disabled={saving}>
                    {saving ? 'Preparing download…' : 'Download Documentation'}
                </Button>
            </div>

            {savedFile && (
                <p className="result__status" role="status">
                    Saved {savedFile}. Check your browser&apos;s downloads folder.
                </p>
            )}
            {error && (
                <p className="result__error" role="alert">
                    {error}
                </p>
            )}

            <div className="result__actions">
                <Button variant="secondary" onClick={() => navigate('/preview')}>Back to Preview</Button>
                <Button variant="secondary" onClick={() => navigate('/upload')}>Back to Main Page</Button>
            </div>
        </section>
    )
}
