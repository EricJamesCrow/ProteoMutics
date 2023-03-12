import React, { useState } from 'react'

// styles
import './ControlsContainer.css'

// components
import Analysis from './pages/Analysis'
import GraphOptions from './pages/GraphOptions';

export default function ControlsContainer() {
  const [selectedTab, setSelectedTab] = useState('Analysis');
  
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
      {selectedTab === 'Analysis' && <Analysis/>}
      {selectedTab === 'GraphOptions' && <GraphOptions/>}
    </div>
    </div>
  )
}
