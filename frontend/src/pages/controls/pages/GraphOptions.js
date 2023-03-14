import React, { useEffect } from 'react'

// redux
import { useSelector, useDispatch } from 'react-redux';

// styles
import './GraphOptions.css'

// components
import DataFormatting from '../components/DataFormatting'
import DataSmoothing from '../components/DataSmoothing'
import InterpolateMissingData from '../components/InterpolateMissingData'

export default function GraphOptions() {
  const dispatch = useDispatch( )
  const graphOptions = useSelector(state => state.graphOptions);

  return (
    <div className="graph-options-container">
      <div className="graph-data-btn-container">
        <button>Graph Data</button>
      </div>
      <DataFormatting state={graphOptions} dispatch={dispatch}/>
      <DataSmoothing state={graphOptions} dispatch={dispatch}/>
      <InterpolateMissingData state={graphOptions} dispatch={dispatch}/>
    </div>
  )
}
