import React from 'react'

// chakra ui
import { Select, Switch } from '@chakra-ui/react'

// redux
import { updateInterpolateMissingData } from '../../../redux/slices/graphOptionsSlice'

export default function InterpolateMissingData( { state, dispatch }) {
  const interpolateMissingData = state.interpolateMissingData;

  const handleSwitchChange = (event) => {
    const updatedDataFormatting = {
      ...state.interpolateMissingData,
        enabled: event.target.checked
    }
    dispatch(updateInterpolateMissingData(updatedDataFormatting))
  }

  const handleSelectChange = (event) => {
    const updatedInterpolateMissingData = {
      ...state.interpolateMissingData,
      value: event.target.value,
    }
    dispatch(updateInterpolateMissingData(updatedInterpolateMissingData))
  }

  return (
    <div className="data-formatting-container">
    <div className="data-formatting-with-switch">
        <h1>Interpolate Missing Data</h1>
        <Switch isChecked={interpolateMissingData.enabled} size='lg' onChange={(e) => handleSwitchChange(e)}/>
    </div>
    <div className="data-formatting-with-switch">
        <div>Method</div>
        <Select placeholder='Select option' size='sm' value={interpolateMissingData.value} onChange={(e) => handleSelectChange(e)}>
            <option value='linear'>Linear</option>
            <option value='quadratic'>Quadratic</option>
            <option value='cubic'>Cubic</option>
            <option value='nearest'>Nearest</option>
        </Select>
    </div>
</div>
  )
}
