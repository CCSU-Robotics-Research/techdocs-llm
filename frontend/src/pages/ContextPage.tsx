import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import FeatureComponent from '../features/contextModification/components/ContextForm.tsx'
import { useContextModification } from '../features/contextModification/hooks/useContextForm.ts'
import { useAppState } from '../hooks/globalHook.ts'

export default function ContextPage(){
    const navigate = useNavigate()
    const [showSuccess, setShowSuccess] = useState(false)
    const { video } = useAppState()
    const { context, setContext, status, errorMessage, isTooLong, canSubmit, handleSubmit } = useContextModification()
    if (!video) return <Navigate to="/upload" replace />

    return(
        <>
            <FeatureComponent
                videoName={video.name}
                videoSizeBytes={video.size}
                context={context}
                status={status}
                errorMessage={errorMessage}
                canSubmit={canSubmit}
                isTooLong={isTooLong}
                onContextChange={setContext}
                onBack={()=> navigate('/upload')}
                onSubmit={async () =>{
                    const result = await handleSubmit()
                    if(result) setShowSuccess(true)
                }}
            />
            {/* temporary pushes user back to upload afterclosing */}
            {showSuccess && (
                <div className="success-popup-backdrop">
                    <section
                        className="success-popup"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="success-popup-title"
                    >
                        <h2 id="success-popup-title">Video submitted successfully</h2>
                        <p>Your video has been submitted for processing.</p>
                        <button type="button" autoFocus onClick={() => navigate('/upload')}>
                            Close
                        </button>
                    </section>
                </div>
            )}
        </>
    )
}