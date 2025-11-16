import React, { useState } from "react";
import { registerApi, RegisterRequest } from "../api/auth";
import { useNavigate } from "react-router-dom";

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState<RegisterRequest>({
    email: "",
    password: "",
    addiction_type: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const res = await registerApi(form);
      setSuccess(res.message);
      setTimeout(() => {
        navigate("/login");
      }, 1500);
    } catch (err: any) {
      setError(err.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gradient-to-br from-purple-500 to-purple-700">
      <div className="bg-purple-400/30 backdrop-blur-md p-10 rounded-2xl shadow-2xl w-96">
        <h1 className="text-3xl font-semibold text-white text-center mb-6">Register</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="email"
            name="email"
            placeholder="Email"
            className="p-3 rounded-lg bg-purple-200/40 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white"
            value={form.email}
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            className="p-3 rounded-lg bg-purple-200/40 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white"
            value={form.password}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="addiction_type"
            placeholder="Addiction type"
            className="p-3 rounded-lg bg-purple-200/40 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white"
            value={form.addiction_type}
            onChange={handleChange}
            required
          />
          {error && <p className="text-red-200 text-sm text-center">{error}</p>}
          {success && <p className="text-green-200 text-sm text-center">{success}</p>}
          <button
            type="submit"
            disabled={loading}
            className="mt-2 py-3 rounded-lg bg-purple-500 hover:bg-purple-600 transition-colors text-white font-medium disabled:opacity-50"
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default RegisterPage;
