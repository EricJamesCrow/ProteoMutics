import React, { useEffect } from 'react'

// redux
import { useSelector } from 'react-redux'

// styles
import './StatisticsComponent.css'

export default function StatisticsComponent() {
  const statistics = useSelector(state => state.statistics);
  const periodicity = statistics.periodicity;
  const signalToNoiseRatio = statistics.signalToNoiseRatio;
  const confidence = statistics.confidence;

  return (
    <div className="statistics-component-container">
        <div className="data-formatting-with-switch">
            <h1>Statistics</h1>
        </div>
        <ul>
            <li>Periodicity: <span className="statistics-span">{periodicity}</span></li>
            <li>Signal to Noise ratio: <span className="statistics-span">{signalToNoiseRatio}</span></li>
            <li>Confidence: <span className="statistics-span">{confidence}</span></li>
        </ul>
    </div>
  )
}
