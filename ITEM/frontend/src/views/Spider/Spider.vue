<template>
  <div class="page">
    <h1>爬虫控制台</h1>

    <div class="card">
      <button :disabled="running" @click="start">启动爬虫</button>
      <p class="muted">点击后会返回 task_id，并开始轮询任务状态。</p>

      <div v-if="taskId" class="kv">
        <div><strong>task_id：</strong>{{ taskId }}</div>
        <div><strong>状态：</strong>{{ status }}</div>
        <div v-if="error" class="error"><strong>错误：</strong>{{ error }}</div>
      </div>
    </div>

    <div v-if="result" class="card">
      <h3>结果</h3>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from "vue";
import { runSpider, spiderStatus, spiderResult } from "@/api/spider";

const taskId = ref("");
const status = ref("");
const error = ref("");
const result = ref("");
const running = ref(false);

let timer = null;

async function start() {
  error.value = "";
  result.value = "";
  status.value = "";

  const resp = await runSpider();
  taskId.value = resp.task_id;
  status.value = "PENDING";
  running.value = true;

  // 轮询状态
  timer = setInterval(async () => {
    try {
      const s = await spiderStatus(taskId.value);
      status.value = s.data.status;
      error.value = s.data.error || "";

      if (status.value === "SUCCESS") {
        clearInterval(timer);
        timer = null;
        const r = await spiderResult(taskId.value);
        result.value = JSON.stringify(r.data, null, 2);
        running.value = false;
      }

      if (status.value === "FAILED") {
        clearInterval(timer);
        timer = null;
        running.value = false;
      }
    } catch (e) {
      error.value = e?.message || "轮询失败";
      clearInterval(timer);
      timer = null;
      running.value = false;
    }
  }, 1500);
}

onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.page { padding: 24px; max-width: 980px; margin: 0 auto; }
.card { background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 16px; margin-top: 16px; }
button { padding: 10px 14px; border-radius: 10px; border: none; cursor: pointer; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.kv { margin-top: 12px; display: grid; gap: 6px; }
.muted { color: #666; font-size: 13px; margin-top: 10px; }
.error { color: #c00; }
pre { background: #f7f7f7; padding: 12px; border-radius: 10px; overflow: auto; }
</style>
