import styles from './ProgressBar.module.css'

type ProgressBarProps = {
    label: string
    progress: number
}

//Component to show how far a video has gone through processing, with a message for the current stage.
export default function ProgressBar({ label, progress }: ProgressBarProps){
    return(
        <div className={styles.progress}>
            {/*The built-in progress element is announced as a progress bar by screen readers.*/}
            <progress className={styles.bar} max={100} value={progress} aria-label="Processing progress" />
            <p className={styles.label} role="status">{label} ({progress}%)</p>
        </div>
    )
}
