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
    };

    const handleSelectChange = (event) => {
      const updatedDataSmoothing = {
        ...state.dataSmoothing,
        method: event.target.value,
      }
      dispatch(updateDataSmoothing(updatedDataSmoothing))
    };

    const handleInputChange = (event, fieldName) => {
      const updatedDataSmoothing = {
        ...state.dataSmoothing,
        [dataSmoothing.method]: {
          ...state.dataSmoothing[dataSmoothing.method],
          [fieldName]: event.target.value
        }
      }
      dispatch(updateDataSmoothing(updatedDataSmoothing))
    };

  return (
    <div className="data-formatting-container smoothing">
        <div className="data-formatting-with-switch">
            <h1>Data Smoothing</h1>
            <Switch size='lg' isChecked={dataSmoothing.enabled} onChange={(e) => handleSwitchChange(e)}/>
        </div>
        <div className="data-formatting-with-switch">
            <div>Method</div>
            <Select placeholder='Select option' size='sm' value={dataSmoothing.method} onChange={(e) => handleSelectChange(e)}>
                <option value='moving'>Moving Average</option>
                <option value='savgol'>Savgol Filter</option>
                <option value='loess'>Loess</option>
                <option value='median'>Median Filter</option>
                <option value='gaussian'>Gaussian Filter</option>
                <option value='exponential'>Exponential Smoothing</option>
            </Select>
        </div>
        {dataSmoothing.method=== 'moving' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Window Size</div>
            <Input placeholder='5' size='sm' value={dataSmoothing.moving.windowSize} onChange={(e) => handleInputChange(e, 'windowSize')}/>
          </div>
        </>
      )}
        {dataSmoothing.method=== 'savgol' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Window Size</div>
            <Input placeholder='5' size='sm' value={dataSmoothing.savgol.windowSize} onChange={(e) => handleInputChange(e, 'windowSize')}/>
          </div>
          <div className="data-formatting-with-switch">
            <div>Poly Order</div>
            <Input placeholder='5' size='sm' value={dataSmoothing.savgol.polyOrder} onChange={(e) => handleInputChange(e, 'polyOrder')}/>
          </div>
        </>
      )}
        {dataSmoothing.method=== 'loess' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Window Size</div>
            <Input placeholder='5' size='sm' value={dataSmoothing.loess.windowSize} onChange={(e) => handleInputChange(e, 'windowSize')}/>
          </div>
        </>
      )}
        {dataSmoothing.method=== 'median' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Window Size</div>
            <Input placeholder='5' size='sm' value={dataSmoothing.median.windowSize} onChange={(e) => handleInputChange(e, 'windowSize')}/>
          </div>
        </>
      )}
        {dataSmoothing.method=== 'gaussian' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Sigma</div>
            <Input placeholder='5' size='sm' value={dataSmoothing.gaussian.sigma} onChange={(e) => handleInputChange(e, 'sigma')}/>
          </div>
          <div className="data-formatting-with-switch">
            <div>Mode</div>
            <Input placeholder='5' size='sm' value={dataSmoothing.gaussian.mode} onChange={(e) => handleInputChange(e, 'mode')}/>
          </div>
        </>
      )}
        {dataSmoothing.method=== 'exponential' && (
        <>
          <div className="data-formatting-with-switch">
            <div>Alpha</div>
            <Input placeholder='5' size='sm' value={dataSmoothing.exponential.alpha} onChange={(e) => handleInputChange(e, 'alpha')}/>
          </div>
        </>
      )}
  </div>
  )
}
