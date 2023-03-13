import React, { useState } from 'react'

// chakra ui
import { CheckIcon, WarningTwoIcon } from '@chakra-ui/icons'
import { Spinner } from '@chakra-ui/react'

// components
import AnalysisBtn from './AnalysisBtn'

export default function AnalysisBtnContainer( { name, allowedFileTypes, type } ) {
    const [isLoading, setIsLoading] = useState(false)
    const [isPreProcessed, setIsPreProcessed] = useState(false)
    
    const showLoading = (loading) => {
        setIsLoading(loading)
    }

    const showPreProcessed = (preProcessed) => {
        setIsPreProcessed(preProcessed)
    }

  return (
    <div className="analysis-btn-container">
        <AnalysisBtn name={name} allowedFileTypes={allowedFileTypes} type={type} showLoading={showLoading} showPreProcessed={showPreProcessed}/>
        {isLoading ? <Spinner w={6} h={6} className="spinner"/> : null}
        {isPreProcessed ? <CheckIcon w={6} h={6} color='#4CAF50'/> : <WarningTwoIcon w={6} h={6} color='red.500'/>}
  </div>
  )
}
