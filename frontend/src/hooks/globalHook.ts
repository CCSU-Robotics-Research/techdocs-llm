import { createContext, createElement, use, useState, type ReactNode } from 'react'
import type { ProcessResult } from '../features/contextModification/types.ts'

type AppStateValue = {
    video: File | null
    context: string
    result: ProcessResult | null
    setVideo: (video: File | null) => void
    setContext: (context: string) => void
    setResult: (result: ProcessResult) => void
}

const AppStateContext = createContext<AppStateValue | null>(null)

export function AppStateProvider({ children }: {children: ReactNode }){
    const[video, setVideo] = useState<File | null>(null)
    const[context, setContext] = useState('')
    const[result, setResult] = useState<ProcessResult | null>(null)

    return createElement(
        AppStateContext,
        { value: { video, context, result, setVideo, setContext, setResult } },
        children,
    )
}

export function useAppState(){
    const value = use(AppStateContext)
    if(!value) throw new Error('useAppState must be used inside AppStateProvider')
        return value
}