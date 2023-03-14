import React from 'react'

// chakra ui
import { Input, Select, Switch } from '@chakra-ui/react'

// redux
import { updateDataSmoothing } from '../../../redux/slices/graphOptionsSlice'

// styles
import './DataSmoothing.css'

export default function DataSmoothing( { state, dispatch }) {
    const dataSmoothing = state.dataSmoothing;

    const handleSwitchChange = (event) => {
      const updatedDataSmoothing = {
        ...state.dataSmoothing,
          enabled: event.target.checked
      }
      dispatch(updateDataSmoothing(updatedDataSmoothing))
    }

    const handleSelectChange = (event) => {
      const updatedDataSmoothing = {
        ...state.dataSmoothing,
        method: event.target.value,
      }
      dispatch(updateDataSmoothing(updatedDataSmoothing))
    }

  return (
    <div className="data-formatting-container smoothing">
        <div className="data-formatting-with-switch">
            <h1>Data Smoothing</h1>
            <Switch size='lg' isChecked={dataSmoothing.enabled} onChange={(e) => handleSwitchChange(e)}/>
        </div>
        <div className="data-formatting-with-switch">
            <div>Method</div>
            <Select placeholder='Select option' size='sm' value={dataSmoothing.method} onChange={(e) => handleSelectChange(e)}>
                <option value='moving-average'>Moving Average</option>
                <option value='savgol-filter'>Savgol Filter</option>
                <option value='loess'>Loess</option>
                <option value='median-filter'>Median Filter</option>
                <option value='gaussian-filter'>Gaussian Filter</option>
                <option value='exponential-smoothing'>Exponential Smoothing</option>
            </Select>
        </div>
        {dataSmoothing.method=== 'moving-average' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Window Size</div>
            <Input placeholder='5' size='sm'/>
          </div>
        </>
      )}
        {dataSmoothing.method=== 'savgol-filter' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Window Size</div>
            <Input placeholder='5' size='sm'/>
          </div>
          <div className="data-formatting-with-switch">
            <div>Poly Order</div>
            <Input placeholder='5' size='sm'/>
          </div>
        </>
      )}
        {dataSmoothing.method=== 'loess' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Window Size</div>
            <Input placeholder='5' size='sm'/>
          </div>
        </>
      )}
        {dataSmoothing.method=== 'median-filter' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Window Size</div>
            <Input placeholder='5' size='sm'/>
          </div>
        </>
      )}
        {dataSmoothing.method=== 'gaussian-filter' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Sigma</div>
            <Input placeholder='5' size='sm'/>
          </div>
          <div className="data-formatting-with-switch">
            <div>Mode</div>
            <Input placeholder='5' size='sm'/>
          </div>
        </>
      )}
        {dataSmoothing.method=== 'exponential-smoothing' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Alpha</div>
            <Input placeholder='5' size='sm'/>
          </div>
        </>
      )}
  </div>
  )
}
