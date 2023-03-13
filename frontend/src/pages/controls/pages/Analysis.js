import React from 'react'

// styles
import './Analysis.css'

// components
import AnalysisBtnContainer from '../components/AnalysisBtnContainer'

export default function Analysis() {
  return (
    <div className="analysis-container">
      <div className="analysis-btns-container">
        <AnalysisBtnContainer name="Genome File" allowedFileTypes={['fa']} type="fasta"/>
        <AnalysisBtnContainer name="Mutation File" allowedFileTypes={['vcf', 'mut']} type="mutation"/>
        <AnalysisBtnContainer name="Nucleosome Map" allowedFileTypes={['bed', 'nuc']} type="nucleosome"/>
      </div>
      <button>Run Analysis</button>
    </div>
  )
}
