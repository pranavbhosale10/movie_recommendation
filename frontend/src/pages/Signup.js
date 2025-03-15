import React, { useState, useEffect } from "react";
import Cookies from "js-cookie"; // Import js-cookie for handling CSRF token

const Signup = () => {
  // State for form inputs
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });

  // Handle input changes
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // Fetch CSRF token when the component mounts
  useEffect(() => {
    async function fetchCSRFToken() {
      try {
        await fetch("http://127.0.0.1:8000/csrf/", {
          method: "GET",
          credentials: "include", // Ensures cookies are included
        });
        console.log("CSRF token fetched!");
      } catch (error) {
        console.error("Error fetching CSRF token:", error);
      }
    }
    fetchCSRFToken();
  }, []);

  // Handle form submission
  const handleSignup = async (e) => {
    e.preventDefault();

    // Retrieve CSRF token from cookies
    const csrfToken = Cookies.get("csrftoken");
    if (!csrfToken) {
      console.error("CSRF token not found!");
      alert("CSRF token is missing. Please try again.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/signup/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken, // Include CSRF token
        },
        credentials: "include", // Ensure cookies are sent with request
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (response.ok) {
        alert("Signup successful!");
      } else {
        alert(data.error || "Signup failed. Please try again.");
      }
    } catch (error) {
      console.error("Signup failed:", error);
      alert("An error occurred during signup.");
    }
  };

  return (
    <div>
      <h2>Signup</h2>
      <form onSubmit={handleSignup}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit">Signup</button>
      </form>
    </div>
  );
};

export default Signup;
