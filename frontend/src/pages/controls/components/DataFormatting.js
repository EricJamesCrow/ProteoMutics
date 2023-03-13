import React from 'react'

// chakra ui
import { Input, Switch } from '@chakra-ui/react'

// styles
import './DataFormatting.css'

export default function DataFormatting() {
  return (
    <div className="data-formatting-container">
    <h1>Data Formatting</h1>
    <div className="data-formatting-inputs-container">
      <div className="data-formatting-input-container">
        <div>Contexts</div>
        <Input placeholder='NNN' size='xs' style={{ width: "50px" }}/>
      </div>
      <div className="data-formatting-input-container">
        <Switch size='sm' />
        <div>Count Complements</div>
      </div>
      <div className="data-formatting-input-container">
        <Switch size='sm'  />
        <div>Normalize to Context</div>
      </div>
      <div className="data-formatting-input-container">
        <Switch size='sm'  />
        <div>Normalize to Median</div>
      </div>
    </div>
    <div className="remove-outliers-container">
        <Switch size='sm'  />
        <div>Remove Outliers</div>
        <Input placeholder='2.5' size='xs' style={{ width: "50px" }}/>
    </div>
  </div>
  )
}
