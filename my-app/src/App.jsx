import React from 'react';
import ReactDOM from 'react-dom/client';

async function clicked () {
    const result = await myApp.sayHello("hello from the renderer is here!");
    console.log(result)
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <div>
        <button onClick={clicked}>Click me!</button>
        <h1>Hello from React!</h1>
    </div>
);