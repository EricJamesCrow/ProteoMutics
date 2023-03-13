import React from 'react'

// styles
import './GraphOptions.css'

// components
import DataFormatting from '../components/DataFormatting'
import DataSmoothing from '../components/DataSmoothing'
import InterpolateMissingData from '../components/InterpolateMissingData'

export default function GraphOptions() {
  return (
    <div className="graph-options-container">
      <div className="graph-data-btn-container">
        <button>Graph Data</button>
      </div>
      <DataFormatting/>
      <DataSmoothing/>
      <InterpolateMissingData/>
    </div>
  )
}
