import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import ProgressBar from './ProgressBar.tsx'

describe('ProgressBar', () => {
    afterEach(() => {
        cleanup()
    })

    it('shows the progress and the current stage message', () => {
        render(<ProgressBar label="Transcribing audio…" progress={50} />)

        const bar = screen.getByRole('progressbar', { name: 'Processing progress' })
        expect(bar.getAttribute('value')).toBe('50')
        expect(bar.getAttribute('max')).toBe('100')
        expect(screen.getByRole('status').textContent).toBe('Transcribing audio… (50%)')
    })
})
