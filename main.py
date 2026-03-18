import requests, time, random, threading, hashlib, base64, json

BASE = "https://wrcenmardnbprfpqhrqe.supabase.co/functions/v1/peanut-mining"

AGENTS = [
    {"agent_id":"SuzakuGenesis","public_key":"0x490987c1dd695cd6295452ac7e180ebca94c9048"},
]

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

            requests.post(f"{BASE}/submit", json={
                "task_id": task["task_id"],
                "agent_id": agent["agent_id"],
                "nonce": nonce,
                "hash": h
            })

            print(f"[{agent['agent_id']}] accepted {nonce}")

            time.sleep(random.uniform(0.3, 1.2))
        except:
            time.sleep(2)

threads = []

for agent in AGENTS:
    for _ in range(4):  # 4 worker per agent
        t = threading.Thread(target=worker, args=(agent,))
        t.start()
        threads.append(t)

for t in threads:
    t.join()
