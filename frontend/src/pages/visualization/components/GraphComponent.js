import React, { useEffect, useRef } from 'react'


// chakra ui
import { Spinner } from '@chakra-ui/react';

// redux
import { useSelector, useDispatch } from 'react-redux';
import { setGraphHtmlLoading } from '../../../redux/slices/graphHtmlSlice'

export default function GraphComponent() {
    const dispatch = useDispatch();
    const graphContainer = useRef(null);
    const graphHtml = useSelector((state) => state.graphHtml.graph);
    const loading = useSelector((state) => state.graphHtml.loading);

    useEffect(() => {
        dispatch(setGraphHtmlLoading(false));
        if (graphHtml && graphContainer.current) {
          graphContainer.current.innerHTML = graphHtml;
    
          const graphScript = graphContainer.current.querySelector('script');
          if (graphScript) {
            eval(graphScript.innerHTML);
          }
        } else if (loading && graphContainer.current) {
          graphContainer.current.innerHTML = "";
        };
      }, [graphHtml]);
    

  return (
    <>
    {loading &&
        <Spinner
        thickness="4px"
        speed="0.65s"
        emptyColor="gray.200"
        color="blue.500"
        size="xl"
        />
    }
    <div ref={graphContainer}>
    </div>
    </>
  )
}
