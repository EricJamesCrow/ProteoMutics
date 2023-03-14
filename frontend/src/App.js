import React from 'react'

// styles
import './App.css'

// components
import TitleBar from './components/TitleBar'

// pages
import Home from './pages/home/Home'

// images
import Resize from './images/resize_icon.svg'

export default function App() {
  return (
    <>
    <div className="container-for-title-bar-component">
      <TitleBar/>
    </div>
    <Home/>
    <Resize className="footer"/>
    </>
  )
}
