import React, { useEffect, useRef } from 'react'

// redux
import { useSelector } from 'react-redux';

export default function GraphComponent() {
    const graphContainer = useRef(null);
    const graphHtml = useSelector((state) => state.graphHtml);

    // useEffect(() => {
    //     if (graphContainer.current) {
    //       graphContainer.current.innerHTML = graphHtml;
    //     }
    //   }, [graphHtml]);

    useEffect(() => {
        if (graphHtml && graphContainer.current) {
          graphContainer.current.innerHTML = graphHtml;
    
          const mpld3Script = graphContainer.current.querySelector('script');
          if (mpld3Script) {
            eval(mpld3Script.innerHTML);
          }
        }
      }, [graphHtml]);
    

  return (
    <div ref={graphContainer}></div>
  )
}
