import { useState } from 'react'
import { DEFAULT_CONTEXT, MAX_CONTEXT_LENGTH } from '../components/constants.ts'
import { submitContext } from '../services/VideoProcessingService.ts'
import { useAppState } from '../../../hooks/globalHook.ts'
import type { ProcessStatus } from '../components/types.ts'

export function useContextModification(){
    const { video, setContext: persistContext, setResult }= useAppState()
    const [context, setContextText] = useState(DEFAULT_CONTEXT)
    const [status, setStatus] = useState<ProcessStatus>('idle')
    const [errorMessage, setErrorMessage] = useState<string | null>(null)

    const isTooLong = context.length > MAX_CONTEXT_LENGTH
    const canSubmit = Boolean(video) && !isTooLong && status !== 'submitting'

    async function handleSubmit(){
        if(!video){
            setStatus('error')
            setErrorMessage('No video selected. Return to the upload step and choose a file.')
            return null
        }
        setStatus('submitting')
        setErrorMessage(null)
        persistContext(context)
        try{
            const result = await submitContext(video, context)
            setResult(result)
            setStatus('idle')
            return result
        }catch(error){
            setStatus('error')
            setErrorMessage(error instanceof Error ? error.message : 'Failed to process the video.')
            return null
        }
    }

    return{ context, setContext: setContextText, status, errorMessage, isTooLong, canSubmit, handleSubmit }
}