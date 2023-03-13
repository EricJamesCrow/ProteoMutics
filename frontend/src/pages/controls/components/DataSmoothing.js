import React from 'react'

// chakra ui
import { Input, Select, Switch } from '@chakra-ui/react'

// styles
import './DataSmoothing.css'

export default function DataSmoothing() {
  return (
    <div className="data-formatting-container">
        <div className="data-formatting-with-switch">
            <h1>Data Smoothing</h1>
            <Switch size='lg' />
        </div>
        <div className="data-formatting-with-switch">
            <div>Method</div>
            <Select placeholder='Select option' size='sm'>
                <option value='moving-average'>Moving Average</option>
                <option value='savgol-filter'>Savgol Filter</option>
                <option value='loess'>Loess</option>
                <option value='median-filter'>Median Filter</option>
                <option value='gaussian-filter'>Gaussian Filter</option>
                <option value='exponential-smoothing'>Exponential Smoothing</option>
            </Select>
        </div>
        <div className="data-formatting-with-switch">
            <div>Window Size</div>
            <Input placeholder='5' size='sm'/>
        </div>
        <div className="data-formatting-with-switch">
            <div>Poly Order</div>
            <Input placeholder='5' size='sm'/>
        </div>
  </div>
  )
}
