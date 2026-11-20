import { useAppState } from '../../../hooks/globalHook'
import styles from './ThemeToggle.module.css'

export default function ThemeToggle() {
    //Use the same theme selection as the document preview
    const { theme, setTheme } = useAppState()

    return (
        <button
            type="button"
            className={styles.toggle}
            aria-pressed={theme === 'dark'}
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
        >
            Dark mode
        </button>
    )
}
