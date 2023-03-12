import React from 'react'

// styles
import "./Home.css"

// components
import ControlsContainer from '../controls/ControlsContainer'
import VisualizationContainer from '../visualization/VisualizationContainer'

export default function Home() {
  return (
    <div className="home-container">
        <h1>Nucleomutics</h1>
        <div className="ui-container">
        <ControlsContainer/>
        <VisualizationContainer/>
        </div>
    </div>
  )
}
