import React from 'react'

// chakra ui
import { Select, Switch } from '@chakra-ui/react'

export default function InterpolateMissingData() {
  return (
    <div className="data-formatting-container">
    <div className="data-formatting-with-switch">
        <h1>Interpolate Missing Data</h1>
        <Switch size='lg' />
    </div>
    <div className="data-formatting-with-switch">
        <div>Method</div>
        <Select placeholder='Select option' size='sm' >
            <option value='moving-average'>Linear</option>
            <option value='savgol-filter'>Quadratic</option>
            <option value='loess'>Cubic</option>
            <option value='median-filter'>Nearest</option>
        </Select>
    </div>
</div>
  )
}
