import { useState } from 'react'
import './App.css'
import Navbar from './components/Navbar'
import CardForm from './components/CardForm'

function App() {
  return (
    <>
      <Navbar />
      <br />
      <div className='landing'>
        <div className="row">
          <div className='col-lg-6 col-md-6 col-sm-12'>
            <h1>Find the prime seats for getting dingers.</h1>
            <p>AI-powered system that identifies optimal seating locations to catch home run balls</p>
            <button id='get-tickets'>Get Tickets</button>
          </div>
          <div className='col-lg-6 col-md-6 col-sm-12'>
            <CardForm />
          </div>
        </div>
      </div>
    </>
  )
}

export default App;
