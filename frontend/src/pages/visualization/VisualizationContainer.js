import React from 'react'

// styles
import './VisualizationContainer.css'

// redux
import { useSelector } from 'react-redux';

// components
import GraphComponent from './components/GraphComponent'

export default function VisualizationContainer() {
  const loading = useSelector((state) => state.graphHtml.loading);

  return (
    <div className="visualization-container">
      <div className={loading ? "display-graphs-container loading" : "display-graphs-container"}>
        <GraphComponent />
      </div>
      <div className="visualization-btns-container">
        <button className="preview-graph-btn">Preview</button>
        <button className="save-graph-btn">Save</button>
      </div>
    </div>
  )
}
