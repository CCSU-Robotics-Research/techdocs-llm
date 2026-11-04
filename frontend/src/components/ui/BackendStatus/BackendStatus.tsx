import { useEffect, useState } from 'react'
import styles from './BackendStatus.module.css'

//Possible states for the backend connection.
type HealthStatus = 'checking' | 'connected' | 'unavailable'

//Messages displayed for each connection state.
const messages = {
    checking: 'Checking connection…',
    connected: 'Processing service connected',
    unavailable: 'Processing service unavailable. Check if the API Server is running on localhost and refresh the page.',
}

//Component to check the backend connection when the homepage opens.
export default function BackendStatus() {
    const [status, setStatus] = useState<HealthStatus>('checking')

    useEffect(() => {
        //Controller to cancel the request and track whether the component is active.
        const controller = new AbortController()
        let active = true

        //Cancel the request if the backend does not respond within five seconds.
        const timeout = window.setTimeout(() => controller.abort(), 5000)

        async function checkHealth() {
            try {
                //Request the current health status without using a cached response.
                const response = await fetch('/api/health', {
                    signal: controller.signal,
                    cache: 'no-store',
                })

                //Error Handling: Treat unsuccessful HTTP responses as connection failures.
                if (!response.ok) {
                    throw new Error('Health request failed')
                }

                const data = await response.json()

                //Update the status only if the component is still active.
                if (active) {
                    setStatus(
                        data.status === 'healthy' ? 'connected' : 'unavailable',
                    )
                }
            } catch {
                //Error Handling: Display unavailable if the request fails or times out.
                if (active) setStatus('unavailable')
            } finally {
                //Clear the timeout after the request finishes.
                window.clearTimeout(timeout)
            }
        }

        //Run the health check when the component mounts.
        checkHealth()

        //Clean up the request and timeout when the component unmounts.
        return () => {
            active = false
            window.clearTimeout(timeout)
            controller.abort()
        }
    }, [])
    return (
        //Display the connection message and its matching status light.
        <p className={`${styles.status} ${styles[status]}`} role="status">
            {/*The message describes the status, so hide the decorative dot from screen readers.*/}
            <span className={styles.dot} aria-hidden="true" />
            {messages[status]}
        </p>
    )
}
