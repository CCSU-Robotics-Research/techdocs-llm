import { Navigate, useNavigate } from 'react-router-dom'
import FeatureComponent from '../features/contextModification/components/FeatureComponent.tsx'
import { useContextModification } from '../features/contextModification/hooks/featureHook.ts'
import { useAppState } from '../hooks/globalHook.ts'

export default function ContextPage(){
    const navigate = useNavigate()
    const { video } = useAppState()
    const { context, setContext, status, errorMessage, isTooLong, canSubmit, handleSubmit } = useContextModification()
    if (!video) return <Navigate to="/upload" replace />

    return(
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
                if(result) navigate('/preview')//could be switched later to navigate to the progress bar if that becomes something we do
            }}
            />
    )
}