import { createContext, createElement, use, useEffect, useState, type ReactNode } from 'react'
import type { ProcessResult } from '../features/contextModification/components/types.ts'

export type Theme = 'light' | 'dark'

type AppStateValue = {
    theme: Theme
    setTheme: (theme: Theme) => void
    video: File | null
    context: string
    result: ProcessResult | null
    setVideo: (video: File | null) => void
    setContext: (context: string) => void
    setResult: (result: ProcessResult) => void
}

const AppStateContext = createContext<AppStateValue | null>(null)

export function AppStateProvider({ children }: {children: ReactNode }){
    //Start in light mode and share the selection with the document preview
    const [theme, setTheme] = useState<Theme>('light')

    //Apply the selected theme to all app pages
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme)
    }, [theme])

    const[video, setVideo] = useState<File | null>(null)
    const[context, setContext] = useState('')
    const[result, setResult] = useState<ProcessResult | null>(null)

    return createElement(
        AppStateContext,
        { value: { video, context, result, setVideo, setContext, setResult, theme, setTheme } },
        children,
    )
}

export function useAppState(){
    const value = use(AppStateContext)
    if(!value) throw new Error('useAppState must be used inside AppStateProvider')
        return value
}
