import React, { useEffect } from 'react'

// redux
import { useSelector } from 'react-redux';

// styles
import './Analysis.css'

// components
import AnalysisBtnContainer from '../components/AnalysisBtnContainer'

export default function Analysis() {
  const files = useSelector(state => state.files);
  const graphOptions = useSelector(state => state.graphOptions);
  const genomeFile = files.genomeFile;
  const mutationFile = files.mutationFile;
  const nucleosomeMap = files.nucleosomeMap;

  useEffect(() => {
    console.log('files', files)
    console.log('graphOptions', graphOptions)
  }, [graphOptions])

  return (
    <div className="analysis-container">
      <div className="analysis-btns-container">
        <AnalysisBtnContainer name="Genome File" file={genomeFile} allowedFileTypes={['fa']} type="fasta"/>
        <AnalysisBtnContainer name="Mutation File" file={mutationFile} allowedFileTypes={['vcf', 'mut']} type="mutation"/>
        <AnalysisBtnContainer name="Nucleosome Map" file={nucleosomeMap} allowedFileTypes={['bed', 'nuc']} type="nucleosome"/>
      </div>
      <button>Run Analysis</button>
    </div>
  )
}
