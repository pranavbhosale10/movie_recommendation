import React, { useState, useEffect } from "react";
import Cookies from "js-cookie"; // Import js-cookie for CSRF handling

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // Fetch CSRF token when the component mounts
  useEffect(() => {
    async function fetchCSRFToken() {
      try {
        await fetch("http://127.0.0.1:8000/csrf/", {
          method: "GET",
          credentials: "include", // Ensure cookies are included
        });
        console.log("CSRF token fetched!");
      } catch (error) {
        console.error("Error fetching CSRF token:", error);
      }
    }
    fetchCSRFToken();
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();

    // Retrieve CSRF token from cookies
    const csrfToken = Cookies.get("csrftoken");
    if (!csrfToken) {
      console.error("CSRF token not found!");
      alert("CSRF token is missing. Please try again.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken, // Include CSRF token
        },
        credentials: "include", // Ensure cookies are sent with request
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (response.ok) {
        alert("Login successful!");
        localStorage.setItem("user", JSON.stringify(data)); // Save user session
      } else {
        alert(data.error || "Login failed");
      }
    } catch (error) {
      console.error("Login failed:", error);
      alert("An error occurred during login.");
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
