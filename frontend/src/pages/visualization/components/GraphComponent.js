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
    
          const mpld3Script = graphContainer.current.querySelector('script');
          if (mpld3Script) {
            eval(mpld3Script.innerHTML);
          }
          console.log(graphHtml)
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
