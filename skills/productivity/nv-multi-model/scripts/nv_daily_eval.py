#!/usr/bin/env python3
"""每日归档评估 + 蛇形重分组 + 周/月归档"""
import os, json, glob
from datetime import datetime, date, timedelta

BASE = os.path.expanduser("~/.hermes/data/NVping")
TMP = os.path.join(BASE, "tmp")
DAY = os.path.join(BASE, "day")
WEEK = os.path.join(BASE, "week")
MONTH = os.path.join(BASE, "month")

def evaluate(records):
    stats = {}
    for r in records:
        for mid, d in r["models"].items():
            s = stats.setdefault(mid, {"ms":[],"ok":0,"err":0})
            if d.get("ok") and d.get("ms"): s["ms"].append(d["ms"]); s["ok"]+=1
            else: s["err"]+=1
    
    sl = []
    for mid, s in stats.items():
        if not s["ms"]: continue
        a = round(sum(s["ms"])/len(s["ms"]))
        std = round((sum((x-a)**2 for x in s["ms"])/len(s["ms"]))**0.5) if len(s["ms"])>1 else 0
        sr = round(s["ok"]/(s["ok"]+s["err"]),2) if (s["ok"]+s["err"])>0 else 0
        trend = "stable"
        if sr < 0.8: trend = "unstable"
        elif len(s["ms"]) >= 4:
            rcent = sum(s["ms"][:2])/2
            older = sum(s["ms"][-2:])/2 if len(s["ms"])>=4 else a
            if older > 0 and (rcent-older)/older > 0.2: trend = "degrading"
        sl.append({"model":mid,"avg_ms":a,"min_ms":min(s["ms"]),"max_ms":max(s["ms"]),
                   "std_ms":std,"success_rate":sr,"trend":trend})
    sl.sort(key=lambda x:x["avg_ms"])
    for i,s in enumerate(sl): s["rank"]=i+1
    
    stable = [s for s in sl if s["trend"]!="unstable"]
    unstable = [s for s in sl if s["trend"]=="unstable"]
    na, nb = [], []
    for i,s in enumerate(stable):
        if (i//2)%2==0: (na if i%2==0 else nb).append(s["model"])
        else: (nb if i%2==0 else na).append(s["model"])
    for i,s in enumerate(unstable): (na if i%2==0 else nb).append(s["model"])
    
    hl = [{"time":r["ts"],"avg_ms":round(sum(v["ms"] for v in r["models"].values() if v.get("ok") and v.get("ms"))/max(sum(1 for v in r["models"].values() if v.get("ok") and v.get("ms")),1))}
          for r in records if any(v.get("ok") and v.get("ms") for v in r["models"].values())]
    
    return {"model_stats":sl,"new_grouping":{"A":na,"B":nb},
            "traffic_pattern":{"peak_hours":[h["time"] for h in hl if h["avg_ms"]>sum(x["avg_ms"] for x in hl)/len(hl)*1.2] if hl else [],
                               "off_peak_hours":[h["time"] for h in hl if h["avg_ms"]<sum(x["avg_ms"] for x in hl)/len(hl)*0.8] if hl else []}}

def main():
    today = date.today(); ts = today.isoformat()
    print(f"📅 [{ts}]")
    
    records = []
    for f in sorted(glob.glob(os.path.join(TMP,"ping_*.json"))):
        if "group" in os.path.basename(f) or "rank" in os.path.basename(f): continue
        try:
            with open(f) as fh: records.append(json.load(fh))
        except: pass
    
    if not records: return print("  无记录")
    
    with open(os.path.join(TMP,"groups.json")) as f: cg = json.load(f)
    ev = evaluate(records)
    
    with open(os.path.join(DAY,f"{ts}.json"),"w") as f:
        json.dump({"date":ts,"total_pings":len(records),"records":records,"evaluation":ev},f)
    
    cg["groups"] = ev["new_grouping"]
    cg["updated_at"] = ts; cg["effective_from"] = f"{ts} 00:00"
    with open(os.path.join(TMP,"groups.json"),"w") as f: json.dump(cg,f)
    
    cutoff = today - timedelta(days=90)
    for f in glob.glob(os.path.join(DAY,"*.json")):
        try:
            d = date.fromisoformat(os.path.basename(f).replace(".json",""))
            if d < cutoff: os.remove(f); print(f"  🗑️ {d}")
        except: pass
    
    from datetime import date as dt
    days_left = (dt.fromisoformat("2027-05-17")-today).days
    if 0 < days_left <= 30: print(f"  ⚠️ Key {days_left}天后过期")
    
    # 周日 → 周总结
    if today.weekday() == 6:
        wn = today.strftime("%Y-W%W")
        wr = []
        for i in range(7):
            d = (today-timedelta(days=i)).isoformat()
            f = os.path.join(DAY,f"{d}.json")
            if os.path.exists(f):
                with open(f) as fh: wr.append(json.load(fh))
        if wr:
            with open(os.path.join(WEEK,f"{wn}.json"),"w") as f:
                json.dump({"week":wn,"range":f"{(today-timedelta(days=6)).isoformat()}~{ts}",
                    "total_records":sum(w.get("total_pings",0) for w in wr),
                    "weekly_summary":{"total_pings":sum(w.get("total_pings",0) for w in wr),
                        "model_count":len(set(s["model"] for w in wr for s in w.get("evaluation",{}).get("model_stats",[])))}},f)
    
    # 1日 → 月归档
    if today.day == 1:
        pm = (today-timedelta(days=1)).strftime("%Y-%m")
        mw = []
        for f in glob.glob(os.path.join(WEEK,"*.json")):
            with open(f) as fh: mw.append(json.load(fh))
        with open(os.path.join(MONTH,f"{pm}.json"),"w") as f:
            json.dump({"month":pm,"week_count":len(mw),"weeks":mw},f)
    
    print(f"✅ 完成")

if __name__ == "__main__":
    main()
