import { useState } from 'react'
import './App.css'
import Signup from './Signup'
function App() {
  const [count, setCount] = useState(0)
//routes here
  return (
    <>
      <div className='App'>
        <Signup/>
      </div>
    </>
  )
}

export default App
