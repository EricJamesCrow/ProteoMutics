import React, { useEffect } from 'react'

// redux
import { useSelector } from 'react-redux';

// styles
import './Analysis.css'

// components
import AnalysisBtnContainer from '../components/AnalysisBtnContainer'

export default function Analysis() {
  const files = useSelector(state => state.files);
  const genomeFile = files.genomeFile;
  const mutationFile = files.mutationFile;
  const nucleosomeMap = files.nucleosomeMap;

  const handleClick = async () => {
    await runAnalysis();
  }

  const runAnalysis = async () => {
    const response = await fetch('http://localhost:8000/api/run_analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({fasta_file_path: genomeFile.file, mutation_file_path: mutationFile.file, nucleosome_file_path: nucleosomeMap.file}),
    });
    const data = await response.json();
    console.log(data);
  }



  return (
    <div className="analysis-container">
      <div className="analysis-btns-container">
        <AnalysisBtnContainer name="Genome File" file={genomeFile} allowedFileTypes={['fa']} type="fasta"/>
        <AnalysisBtnContainer name="Mutation File" file={mutationFile} allowedFileTypes={['vcf', 'mut']} type="mutation"/>
        <AnalysisBtnContainer name="Nucleosome Map" file={nucleosomeMap} allowedFileTypes={['bed', 'nuc']} type="nucleosome"/>
      </div>
      <button onClick={handleClick}>Run Analysis</button>
    </div>
  )
}
