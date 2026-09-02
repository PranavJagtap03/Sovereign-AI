import urllib.request
import json
import time

def call_api(payload):
    t0 = time.perf_counter()
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/agent/run',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode('utf-8'))
        elapsed = round(time.perf_counter() - t0, 2)
        return data, elapsed

print("=== 1. LIVE VISION TASK: Image 1 (Pump Defect Report) ===")
p1 = {
    "task": "Extract defect description, equipment ID, severity, and recommended actions.",
    "file_name": "pump_defect_report.png",
    "live_mode": True
}
res1, dur1 = call_api(p1)
print(f"Duration: {dur1}s | Model: {res1.get('model_used')} | Task Type: {res1.get('task_type')}")
print("Answer Preview:\n", res1.get('final_response', '')[:250])

print("\n=== 2. LIVE VISION TASK: Image 2 (Electrical Control Panel Report) ===")
p2 = {
    "task": "Extract defect description, equipment ID, severity, and recommended actions.",
    "file_name": "circuit_panel_report.png",
    "live_mode": True
}
res2, dur2 = call_api(p2)
print(f"Duration: {dur2}s | Model: {res2.get('model_used')} | Task Type: {res2.get('task_type')}")
print("Answer Preview:\n", res2.get('final_response', '')[:250])
print(f"Different Responses: {res1.get('final_response') != res2.get('final_response')}")

print("\n=== 3. LIVE TEXT TASK: DeepSeek-R1 (Swapping from Qwen to DeepSeek) ===")
p3 = {
    "task": "Explain on-premise sovereign AI security in 2 sentences.",
    "live_mode": True
}
res3, dur3 = call_api(p3)
print(f"Duration: {dur3}s | Model: {res3.get('model_used')} | Reasoning Length: {len(res3.get('reasoning_trace') or '')}")
print("Reasoning Sample:", repr((res3.get('reasoning_trace') or '')[:120]))
print("Answer Preview:\n", res3.get('final_response', '')[:200])

print("\n=== 4. LIVE VISION TASK: Swapping from DeepSeek back to Qwen ===")
res4, dur4 = call_api(p1)
print(f"Duration: {dur4}s | Model: {res4.get('model_used')} | Task Type: {res4.get('task_type')}")
print("Swap Back Success:", res4.get('model_used') == 'Qwen2.5-VL (Local GPU)')
