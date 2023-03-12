import React from 'react'

import './VisualizationContainer.css'

export default function VisualizationContainer() {
  return (
    <div className="visualization-container">
      <div className="display-graphs-container"></div>
      <div className="visualization-btns-container">
        <button className="preview-graph-btn">Preview</button>
        <button className="save-graph-btn">Save</button>
      </div>
    </div>
  )
}
