import { useState } from 'react'
import { DEFAULT_CONTEXT, MAX_CONTEXT_LENGTH } from '../constants.ts'
import { submitContext } from '../services/service.ts'
import { useAppState } from '../../../hooks/globalHook.ts'
import type { ProcessStatus } from '../types.ts'

export function useContextModification(){
    const { video, setContext: persistContext, setResult }= useAppState()
    const [context, setContextText] = useState(DEFAULT_CONTEXT)
    const [status, setStatus] = useState<ProcessStatus>('idle')
    const [errorMessage, setErrorMessage] = useState<string | null>(null)

    const isTooLong = context.length > MAX_CONTEXT_LENGTH
    const canSubmit = Boolean(video) && context.length > 0 && !isTooLong && status !== 'submitting'
}