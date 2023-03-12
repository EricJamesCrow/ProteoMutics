import React, { useState } from 'react'

// chakra ui
import { CheckIcon } from '@chakra-ui/icons'
import { Spinner } from '@chakra-ui/react'

// components
import AnalysisBtn from './AnalysisBtn'

export default function AnalysisBtnContainer( { name, allowedFileTypes } ) {
    const [isLoading, setIsLoading] = useState(false)
    const [isPreProcessed, setIsPreProcessed] = useState(false)

  return (
    <div className="analysis-btn-container">
        <AnalysisBtn name={name} allowedFileTypes={allowedFileTypes}/>
        {isLoading ? <Spinner w={6} h={6} className="spinner"/> : null}
        {isPreProcessed ? <CheckIcon w={6} h={6}/> : null}
  </div>
  )
}
