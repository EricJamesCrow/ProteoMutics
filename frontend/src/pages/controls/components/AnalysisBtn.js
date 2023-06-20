import React from 'react'

// styles
import './AnalysisBtn.css'

export default function AnalysisBtn( { name, handleFileSelect, allowedFileTypes, type, showLoading } ) {
    const handleClick = async () => {
      const response = await myApp.showFileDialog(allowedFileTypes);
      if(!response) return;
      showLoading(true)
      const result = await checkIfPreprocessed(response, type)
      handleFileSelect(response, result)
      showLoading(false)
    }

    const checkIfPreprocessed = async (file_path, file_type) => {
      const response = await fetch('http://localhost:8000/api/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({file_path: file_path, type: file_type})
      });
      const data = await response.json();
      return data.is_preprocessed;
    }

  return (
    <button className="analysis-btn" onClick={handleClick}>{name}</button>

  )
}
