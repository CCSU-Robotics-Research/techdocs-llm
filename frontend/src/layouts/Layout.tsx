import { Outlet } from 'react-router-dom'
// import logo from '../assets/images/CCSU-LOGO.png'

export default function Layout(){
    return(
        <div className="layout">
            <header className="layout__header">
                {/* <img src={logo} width="200" alt="CCSU Robotics Research" className="layout__logo" /> */}
                {/* if we want to reinclude the img */}
                <h1>Video to Instruction Manual</h1>
            </header>
            <main className="layout__main">
                <Outlet />
            </main>
            <footer className="layout__footer">&copy; 2026 Team Git Up | CCSU Robotics Research</footer>
        </div>
    )
}