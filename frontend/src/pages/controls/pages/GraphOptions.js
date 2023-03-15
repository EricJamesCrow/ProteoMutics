import React from 'react'

// redux
import { useSelector, useDispatch } from 'react-redux';
import { setGraphHtml, setGraphHtmlLoading } from '../../../redux/slices/graphHtmlSlice'

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
    const response = await fetch('http://localhost:8000/api/generate_graph', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({mutation_file_path: filePath})
    });
    const data = await response.json();
    const graphHtml = data.graph_html;
    dispatch(setGraphHtml(graphHtml));
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
