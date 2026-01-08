// src/api/spider.js
import http from "./http";

export const runSpider = async () => (await http.post("/api/spider/run")).data;
export const spiderStatus = async (taskId) => (await http.get(`/api/spider/status/${taskId}`)).data;
export const spiderResult = async (taskId) => (await http.get(`/api/spider/result/${taskId}`)).data;
