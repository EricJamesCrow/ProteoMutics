import React from 'react'

// styles
import './VisualizationContainer.css'

// components
import GraphComponent from './components/GraphComponent'

export default function VisualizationContainer() {

  return (
    <div className="visualization-container">
      <div className="display-graphs-container">
        <GraphComponent />
      </div>
      <div className="visualization-btns-container">
        <button className="preview-graph-btn">Preview</button>
        <button className="save-graph-btn">Save</button>
      </div>
    </div>
  )
}
