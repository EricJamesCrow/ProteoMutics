import React, { useState } from 'react'

import './ControlsContainer.css'

export default function ControlsContainer() {
  const [selectedTab, setSelectedTab] = useState('General');
  
  const handleTabClick = (tab) => {
    console.log(tab)
    setSelectedTab(tab);
  };

  return (
    <div className="container-for-controls-container">
    <div className="controls-tabs-container">
    <button
        className={selectedTab === 'General' ? 'selected' : ''}
        onClick={() => handleTabClick('General')}
      >
        General
      </button>
      <button
        className={selectedTab === 'Settings' ? 'selected' : ''}
        onClick={() => handleTabClick('Settings')}
      >
        Settings
      </button>
    </div>
    <div className="controls-container">
    </div>
    </div>
  )
}
