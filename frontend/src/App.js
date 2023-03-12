import React from 'react'

// styles
import './App.css'

// components
import TitleBar from './components/TitleBar'

// images
import Resize from './images/resize_icon.svg'

export default function App() {
  return (
    <>
    <TitleBar/>
    <Resize className="footer"/>
    </>
  )
}
