import React, { useState, useEffect } from 'react'

// chakra ui
import { Input, Switch } from '@chakra-ui/react'

import { updateDataFormatting } from '../../../redux/slices/graphOptionsSlice'

// styles
import './DataFormatting.css'

export default function DataFormatting( { state, dispatch } ) {
  const dataFormatting = state.dataFormatting;

  const handleInputChange = (event, fieldName) => {
    const updatedDataFormatting = {
      ...state.dataFormatting,
      [fieldName]: {
        ...state.dataFormatting[fieldName],
        value: event.target.value
      }
    }
    dispatch(updateDataFormatting(updatedDataFormatting))
  }
  
  const handleSwitchChange = (event, fieldName) => {
    const updatedDataFormatting = {
      ...state.dataFormatting,
      [fieldName]: {
        ...state.dataFormatting[fieldName],
        enabled: event.target.checked
      }
    }
    dispatch(updateDataFormatting(updatedDataFormatting))
  }

  return (
    <div className="data-formatting-container">
    <h1>Data Formatting</h1>
    <div className="data-formatting-inputs-container">
      <div className="data-formatting-input-container">
        <div>Contexts</div>
        <Input value={dataFormatting.contexts.value} onChange={(e) => handleInputChange(e, 'contexts')} placeholder='NNN' size='xs' style={{ width: "50px" }}/>
      </div>
      <div className="data-formatting-input-container">
        <Switch isChecked={dataFormatting.countComplements.enabled} onChange={(e) => handleSwitchChange(e, 'countComplements')} size='sm'/>
        <div>Count Complements</div>
      </div>
      <div className="data-formatting-input-container">
        <Switch isChecked={dataFormatting.normalizeToContext.enabled} onChange={(e) => handleSwitchChange(e, 'normalizeToContext')} size='sm'  />
        <div>Normalize to Context</div>
      </div>
      <div className="data-formatting-input-container">
        <Switch isChecked={dataFormatting.normalizeToMedian.enabled} onChange={(e) => handleSwitchChange(e, 'normalizeToMedian')} size='sm'  />
        <div>Normalize to Median</div>
      </div>
    </div>
    <div className="remove-outliers-container">
        <Switch isChecked={dataFormatting.removeOutliers.enabled} onChange={(e) => handleSwitchChange(e, 'removeOutliers')} size='sm'  />
        <div>Remove Outliers</div>
        <Input value={dataFormatting.removeOutliers.value} onChange={(e) => handleInputChange(e, 'removeOutliers')} placeholder='2.5' size='xs' style={{ width: "50px" }}/>
    </div>
  </div>
  )
}
