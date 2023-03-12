import React from 'react'

// styles
import './Analysis.css'

// components
import AnalysisBtnContainer from '../components/AnalysisBtnContainer'

export default function Analysis() {
  return (
    <div className="analysis-container">
      <div className="analysis-btns-container">
        <AnalysisBtnContainer name="Genome File"/>
        <AnalysisBtnContainer name="Mutation File"/>
        <AnalysisBtnContainer name="Nucleosome Map"/>
      </div>
      <button>Run Analysis</button>
    </div>
  )
}
