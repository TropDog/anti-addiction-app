export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: string;
}

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export async function loginApi(data: LoginRequest): Promise<TokenResponse> {
  const res = await fetch(`${API_URL}/users/api/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    let message = "Nie udało się zalogować.";
    try {
      const err = await res.json();
      message = err.detail || message;
    } catch {}
    throw new Error(message);
  }

  const json = (await res.json()) as TokenResponse;
  localStorage.setItem("access_token", json.access_token);
  localStorage.setItem("user_id", json.user_id);
  return json;
}

export interface RegisterRequest {
  email: string;
  password: string;
  addiction_type: string; // jeśli Twój backend wymaga tego pola
}

export interface RegisterResponse {
  message: string;
  user_id: string;
}


export async function registerApi(data: RegisterRequest): Promise<RegisterResponse> {
  const res = await fetch(`${API_URL}/users/api/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    let message = "Registration failed.";
    try {
      const err = await res.json();
      message = err.detail || message;
    } catch {}
    throw new Error(message);
  }

  const json = (await res.json()) as RegisterResponse;
  return json;
}

