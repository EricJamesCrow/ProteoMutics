import React from 'react'

// styles
import './Analysis.css'

// components
import AnalysisBtnContainer from '../components/AnalysisBtnContainer'

export default function Analysis() {
  return (
    <div className="analysis-container">
      <div className="analysis-btns-container">
        <AnalysisBtnContainer name="Genome File" allowedFileTypes={['fa']}/>
        <AnalysisBtnContainer name="Mutation File" allowedFileTypes={['vcf']}/>
        <AnalysisBtnContainer name="Nucleosome Map" allowedFileTypes={['bed']}/>
      </div>
      <button>Run Analysis</button>
    </div>
  )
}
