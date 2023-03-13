import React, { useState } from 'react'

// styles
import './ControlsContainer.css'

// components
import Analysis from './pages/Analysis'
import GraphOptions from './pages/GraphOptions';

export default function ControlsContainer() {
  const [selectedTab, setSelectedTab] = useState('GraphOptions');
  
  const handleTabClick = (tab) => {
    setSelectedTab(tab);
  };

  return (
    <div className="container-for-controls-container">
    <div className="controls-tabs-container">
    <button
        className={selectedTab === 'Analysis' ? 'selected' : ''}
        onClick={() => handleTabClick('Analysis')}
      >
        Analysis
      </button>
      <button
        className={selectedTab === 'GraphOptions' ? 'selected' : ''}
        onClick={() => handleTabClick('GraphOptions')}
      >
        Graph Options
      </button>
    </div>
    <div className="controls-container">
      <div className={selectedTab === 'Analysis' ? '' : 'no-display'}>
        <Analysis/>
      </div>
      <div className={selectedTab === 'GraphOptions' ? '' : 'no-display'}>
        <GraphOptions/>
      </div>
    </div>
    </div>
  )
}
