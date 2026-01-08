// src/api/auth.js
import http from "./http";

export async function loginApi(payload) {
  const res = await http.post("/api/auth/login", payload);
  return res.data; // {code,message,data}
}

export async function profileApi() {
  const res = await http.get("/api/auth/profile");
  return res.data;
}
