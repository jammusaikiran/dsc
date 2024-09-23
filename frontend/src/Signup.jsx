import React, { useState } from 'react';
import axios from 'axios'; // Import Axios for API calls
import { FaUser, FaEnvelope, FaLock } from 'react-icons/fa'; // Import icons

const Signup = () => {
  const [isSignIn, setIsSignIn] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });

  const handleSignInClick = () => {
    setIsSignIn(true);
    setFormData({ username: '', email: '', password: '' }); // Clear form data
  };

  const handleSignUpClick = async () => {
    setIsSignIn(false);

    // Post form data to your backend API for signup
    try {
      const response = await axios.post('http://localhost:5000/signup', formData);
      console.log(response.data.message);
    } catch (error) {
      console.error('Error signing up:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className='signup'>
      <div className='form-box'>
        <h1 id='title'>{isSignIn ? 'Sign In' : 'Sign Up'}</h1>
        <form onSubmit={(e) => e.preventDefault()}>
          <div className='input-group'>
            {!isSignIn && (
              <div className='input-field' id='name-field'>
                <FaUser /> {/* Username icon */}
                <input
                  type='text'
                  name='username'
                  placeholder='Username'
                  value={formData.username}
                  onChange={handleChange}
                  required={!isSignIn}
                />
              </div>
            )}
            <div className='input-field'>
              <FaEnvelope /> {/* Email icon */}
              <input
                type='email'
                name='email'
                placeholder='Email'
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className='input-field'>
              <FaLock /> {/* Password icon */}
              <input
                type='password'
                name='password'
                placeholder='Password'
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            <p>Lost Password <a href='#'> Click Here</a></p>
          </div>
          <div className="btn-field">
            <button type='button' id='signupbtn' onClick={handleSignUpClick}> Sign Up</button>
            <button type='button' id='signinbtn' onClick={handleSignInClick}> Sign In</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Signup;
