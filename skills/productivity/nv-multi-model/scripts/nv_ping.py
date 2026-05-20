#!/usr/bin/env python3
"""
NVIDIA NIM Ping 脚本 — 每半小时执行一次
API Key 从 macOS Keychain 读取，不硬编码
"""
import os, sys, json, time, asyncio, ssl, urllib.request, urllib.error, subprocess
from datetime import datetime

BASE = os.path.expanduser("~/.hermes/data/NVping/tmp")
KEY_SVC = "nvidia_api_key"
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
EXPIRE = "2027-05-17"
PROMPT = "hi"
MAX_TOKENS = 5

def get_key():
    r = subprocess.run(["security","find-generic-password","-w","-s",KEY_SVC],
                       capture_output=True,text=True,timeout=5)
    return r.stdout.strip()

async def ping(sem, model, key, res):
    async with sem:
        payload = {"model":model,"messages":[{"role":"user","content":PROMPT}],
                   "max_tokens":MAX_TOKENS,"temperature":0.1}
        data = json.dumps(payload).encode()
        req = urllib.request.Request(f"{API_URL}/chat/completions",data=data,
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            method="POST")
        start = time.time()
        try:
            ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
            loop = asyncio.get_event_loop()
            def do(): 
                with urllib.request.urlopen(req,timeout=20,context=ctx) as r:
                    return json.loads(r.read().decode())
            result = await loop.run_in_executor(None, do)
            ms = round((time.time()-start)*1000)
            res.append({"model":model,"ms":ms,"ok":True})
            print(f"  ✅ {model:55s} {ms:6.0f}ms")
        except urllib.error.HTTPError as e:
            res.append({"model":model,"ms":None,"ok":False,"error":f"HTTP {e.code}"})
            print(f"  ❌ {model:55s} HTTP {e.code}")
        except Exception as e:
            res.append({"model":model,"ms":None,"ok":False,"error":str(e)[:60]})
            print(f"  ❌ {model:55s} {str(e)[:40]}")

async def main():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(os.path.join(BASE,"state.txt")) as f: group = f.read().strip()
    print(f"\n{'='*60}\n🕐 [{ts}] Group {group}\n{'='*60}")
    
    with open(os.path.join(BASE,"groups.json")) as f: groups = json.load(f)
    models = groups["groups"].get(group,[])
    if not models: return print("❌ 空组")
    print(f"   共 {len(models)} 个模型")
    
    key = get_key()
    if not key: return print("❌ 无Key")
    
    sem = asyncio.Semaphore(10); results = []
    await asyncio.gather(*[ping(sem,m,key,results) for m in models])
    
    ok = sum(1 for r in results if r["ok"])
    avg = round(sum(r["ms"] for r in results if r["ok"])/ok) if ok else 0
    print(f"\n   ✅ {ok}/{len(results)} 成功, 平均 {avg}ms")
    
    with open(os.path.join(BASE,f"ping_{group}.json"),"w") as f:
        json.dump({"ts":ts,"group":group,"total":len(models),
            "success":ok,"failed":len(results)-ok,"avg_ms":avg,
            "models":{r["model"]:{"ms":r["ms"],"ok":r["ok"],"error":r.get("error")} for r in results}},f)
    
    def top3(cat_ids):
        cand = [(r["model"],r["ms"]) for r in results if r["model"] in cat_ids and r["ok"]]
        cand.sort(key=lambda x:x[1])
        return [{"model":m,"ms":ms} for m,ms in cand[:3]]
    
    rank = {"updated_at":ts,"group":group,"avg_ms_all":avg,
        "categories":groups["categories"],
        "top_by_category":{k:top3(v) for k,v in groups["categories"].items()}}
    with open(os.path.join(BASE,"ranking.json"),"w") as f: json.dump(rank,f)
    
    nxt = "B" if group=="A" else "A"
    with open(os.path.join(BASE,"state.txt"),"w") as f: f.write(nxt)
    
    from datetime import date
    days = (date.fromisoformat(EXPIRE)-date.today()).days
    if 0 < days <= 30: print(f"\n⚠️ Key {days}天后过期")
    print(f"✅ 下一轮: Group {nxt}")

if __name__ == "__main__":
    asyncio.run(main())
