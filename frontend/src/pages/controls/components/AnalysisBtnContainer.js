import React, { useState } from 'react'

// chakra ui
import { CheckIcon, WarningTwoIcon } from '@chakra-ui/icons'
import { Spinner } from '@chakra-ui/react'

// redux
import { useDispatch  } from 'react-redux';
import { setGenomeFile, setMutationFile, setNucleosomeMap, setPreprocessed } from '../../../redux/slices/filesSlice'

// components
import AnalysisBtn from './AnalysisBtn'

export default function AnalysisBtnContainer( { name, file, allowedFileTypes, type } ) {
    const [isLoading, setIsLoading] = useState(false)
    const dispatch = useDispatch()
    
    const showLoading = (loading) => {
        setIsLoading(loading)
    }

    const handleFileSelect = (selectedFile, preProcessed) => {
      switch (type) {
        case 'fasta':
          dispatch(setGenomeFile(selectedFile));
          dispatch(setPreprocessed({ fileType: 'genomeFile', value: preProcessed }));
          break;
        case 'mutation':
          dispatch(setMutationFile(selectedFile));
          dispatch(setPreprocessed({ fileType: 'mutationFile', value: preProcessed }));
          break;
        case 'nucleosome':
          dispatch(setNucleosomeMap(selectedFile));
          dispatch(setPreprocessed({ fileType: 'nucleosomeMap', value: preProcessed }));
          break;
        default:
          break;
      }
    };

  return (
    <div className="analysis-btn-container">
        <AnalysisBtn name={name} handleFileSelect={handleFileSelect} allowedFileTypes={allowedFileTypes} type={type} showLoading={showLoading}/>
        {isLoading ? <Spinner w={6} h={6} className="spinner"/> : null}
        {file.preProcessed ? <CheckIcon w={6} h={6} color='#4CAF50'/> : file.file && <WarningTwoIcon w={6} h={6} color='red.500' />}
  </div>
  )
}
