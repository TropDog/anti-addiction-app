import React, { useState } from "react";
import { loginApi, TokenResponse } from "../api/auth.ts";

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const resp: TokenResponse = await loginApi({ email, password });
      setToken(resp.access_token);
      // zapis tokenu w localStorage
      localStorage.setItem("access_token", resp.access_token);
    } catch (err: any) {
      setError(err.message || "Login error");
    }
  };

  if (token) {
    return (
      <div>
        <h2>Logged in!</h2>
        <p>Token: {token}</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Email: </label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
        </div>
        <div>
          <label>Password: </label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
        </div>
        <button type="submit">Log in</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default LoginPage;
