import React from 'react'

// redux
import { useSelector, useDispatch } from 'react-redux';
import { setGraphHtml, setGraphHtmlLoading } from '../../../redux/slices/graphHtmlSlice'
import { setPeriodicity, setSignalToNoiseRatio, setConfidence } from '../../../redux/slices/statisticsSlice';

// styles
import './GraphOptions.css'

// components
import DataFormatting from '../components/DataFormatting'
import DataSmoothing from '../components/DataSmoothing'
import InterpolateMissingData from '../components/InterpolateMissingData'

export default function GraphOptions() {
  const dispatch = useDispatch()
  const graphOptions = useSelector(state => state.graphOptions);

  const handleClick = async () => {
    const allowedFileTypes = ['data']
    const response = await myApp.showFileDialog(allowedFileTypes);
    if(!response) return;
    await graphData(response);
  }

  const graphData = async (filePath) => {
    dispatch(setGraphHtmlLoading(true));
    dispatch(setGraphHtml(null));
    dispatch(setPeriodicity(null));
    dispatch(setSignalToNoiseRatio(null));
    dispatch(setConfidence(null));
    const response = await fetch('http://localhost:8000/api/generate_graph', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({mutation_file_path: filePath})
    });
    const data = await response.json();
    const graphHtml = data.graph_html;
    const period = data.period;
    const confidence = data.confidence;
    const signalToNoise = data.signal_to_noise;
    dispatch(setGraphHtml(graphHtml));
    dispatch(setPeriodicity(period));
    dispatch(setSignalToNoiseRatio(signalToNoise));
    dispatch(setConfidence(confidence));
  }

  return (
    <div className="graph-options-container">
      <div className="graph-data-btn-container">
        <button onClick={handleClick}>Graph Data</button>
      </div>
      <DataFormatting state={graphOptions} dispatch={dispatch}/>
      <DataSmoothing state={graphOptions} dispatch={dispatch}/>
      <InterpolateMissingData state={graphOptions} dispatch={dispatch}/>
    </div>
  )
}
