import type {TextareaHTMLAttributes } from 'react'
import {inputStyles } from './styles.ts'

type InputProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
    label: string
    hint?: string
    error?: string
}

export default function Input({label, hint, error, id, className = '', ...rest}: InputProps){
    const inputId = id ?? rest.name ?? 'context-input'
    return (
        <div className={inputStyles.field}>
            <label className={inputStyles.label} htmlFor={inputId}>{label}</label>
            <textarea id={inputId} className={`${inputStyles.textarea} ${className}`.trim()}
                aria-invalid={error ? true : undefined} aria-describedby={hint ? `${inputId}-hint` : undefined} {...rest}/>
            {hint && <p id={`${inputId}-hint`} className={inputStyles.hint}>{hint}</p>}
            {error && <p role="alert" className={inputStyles.error}>{error}</p>}
        </div>
    )
}