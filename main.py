import requests, time, random, threading, hashlib, base64, json

BASE = "https://wrcenmardnbprfpqhrqe.supabase.co/functions/v1/peanut-mining"

AGENTS = [
    {"agent_id":"Qinglong","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048","workers":2,"delay":[0.6,1.4]},
    {"agent_id":"Baihu","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048","workers":1,"delay":[0.8,1.6]},
    {"agent_id":"Zhuque","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048","workers":2,"delay":[0.5,1.2]},
    {"agent_id":"Xuanwu","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048","workers":1,"delay":[1.0,1.8]},
    {"agent_id":"Fenghuang","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048","workers":2,"delay":[0.4,1.0]},
    {"agent_id":"Taotie","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048","workers":1,"delay":[0.9,1.7]},
    {"agent_id":"Pixiu","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048","workers":2,"delay":[0.5,1.3]},
    {"agent_id":"Qilin","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048","workers":1,"delay":[1.1,2.0]},
    {"agent_id":"Yinglong","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048","workers":1,"delay":[0.7,1.5]},
    {"agent_id":"Zhulong","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048","workers":1,"delay":[0.8,1.6]},
]

lock = threading.Lock()
stats = {"accepted":0,"failed":0}

def solve(prefix, difficulty):
    nonce = random.randint(0, 10**6)
    while True:
        h = hashlib.sha256(f"{prefix}{nonce}".encode()).hexdigest()
        if h.startswith("0"*difficulty):
            return nonce, h
        nonce += 1

def worker(agent):
    while True:
        try:
            task = requests.get(f"{BASE}/tasks/current").json()
            payload = json.loads(base64.b64decode(task["payload"]))

            nonce, h = solve(payload["nonce_prefix"], task["difficulty"])

            res = requests.post(f"{BASE}/submit", json={
                "task_id": task["task_id"],
                "agent_id": agent["agent_id"],
                "nonce": nonce,
                "hash": h
            })

            if res.status_code == 200:
                with lock:
                    stats["accepted"] += 1
                print(f"[{agent['agent_id']}] OK {nonce}")
                # adaptive speed up
                agent["delay"][0] *= 0.98
                agent["delay"][1] *= 0.98
            else:
                with lock:
                    stats["failed"] += 1
                # adaptive slow down
                agent["delay"][0] *= 1.2
                agent["delay"][1] *= 1.2

            # jitter
            time.sleep(random.uniform(*agent["delay"]))

        except:
            time.sleep(random.uniform(1,3))

def dashboard():
    while True:
        time.sleep(30)
        with lock:
            acc = stats["accepted"]
            fail = stats["failed"]
        rate = acc / 0.5 if acc else 0
        print(f"\n=== DASHBOARD === accepted:{acc} failed:{fail} rate:{rate:.2f}/min\n")

threads = []

for agent in AGENTS:
    for _ in range(agent["workers"]):
        t = threading.Thread(target=worker, args=(agent,))
        t.start()
        threads.append(t)

threading.Thread(target=dashboard, daemon=True).start()

for t in threads:
    t.join()
