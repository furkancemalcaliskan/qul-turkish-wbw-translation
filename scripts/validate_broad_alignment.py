"""Independently verify the broad batch against its fixed baseline and log."""
import hashlib
import json
import re
import subprocess

from alignment_common import ROOT, render

def unique(pairs):
    result={}
    for k,v in pairs:
        assert k not in result, f"Duplicate key: {k}"
        result[k]=v
    return result

read=lambda name:json.loads((ROOT/name).read_bytes(),object_pairs_hook=unique)
baseline=json.loads(subprocess.check_output(["git","show","033d895:turkish-wbw-translation.json"],cwd=ROOT),object_pairs_hook=unique)
for group in read("reports/continued-alignment-changes.json")["groups"]:
    baseline.update(group["after"])
reference=(ROOT/"english-wbw-translation.json").read_bytes()
assert reference==subprocess.check_output(["git","show","4503cdc:english-wbw-translation.json"],cwd=ROOT)
en=read("english-wbw-translation.json")
tr=read("turkish-wbw-translation.json")
manifest=read("reports/broad-alignment-changes.json")
updates={}
for group in manifest["groups"]:
    assert group["before"]=={k:baseline.get(k) for k in group["members"]}
    for key in group["members"]:
        assert key not in updates
        assert group["after"][key]==render(group["parts"],key)
        updates[key]=group["after"][key]
        assert updates[key].replace("(","").replace(")","")==group["shared_expression"]
        stack=[]
        for char in updates[key]:
            if char in "([":stack.append(char)
            elif char in ")]":
                assert stack and stack.pop()==(")"==char and "(" or "["),(key,updates[key])
        assert not stack,key
expected=baseline|updates
assert tr==expected
assert list(tr)==[k for k in en if k in tr]
assert not tr.keys()-en.keys()
assert all(isinstance(v,str) and v.strip() for v in tr.values())
assert all(tr[k]==v for k,v in baseline.items() if k not in updates)
assert all(tr[k]==en[k] for k in en if re.fullmatch(r"\(\d+\)",en[k]))
assert len(tr)-len(baseline)==manifest["summary"]["added_keys"]
assert len(en.keys()-tr.keys())==manifest["summary"]["remaining_missing_keys"]
assert {r["key"] for r in read("reports/alignment-pending.json")}==en.keys()-tr.keys()
assert tr["2:5:4"]=="(Rableri)nden" and tr["2:5:5"]=="Rableri(nden)"
assert tr["2:96:5"]=="hayat(a)"  # Never infer haya + ta.
assert tr["4:60:19"]=="tağut(a)"
assert tr["2:203:9"]=="iki gün (içinde)"  # Never infer g + ün.
assert tr["2:60:12"]=="on (iki)"
assert tr["75:12:2"]=="Rabbin(e o gün)"
assert tr["2:217:3"]=="ay (hakkında)"
assert tr["6:143:7"]=="(ve) keçiler(den)"
assert tr["2:143:14"]=="(ve) yap(ma)dık"
assert tr["7:188:14"]=="bil(seydim)"
assert tr["7:73:27"]=="arzı(ndan)"
assert "2:48:4" not in tr  # Unresolved lexical/voice issue remains explicit.
raw=(ROOT/"turkish-wbw-translation.json").read_bytes()
assert raw==(json.dumps(tr,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
result={"english_unchanged_from_initial":True,"exact_manifest_scope":True,
        "untouched_pairs_preserved":True,"ayah_numbers_preserved":True,
        "reference_order_and_format":True,"duplicate_keys":0,
        "regression_examples":"passed","pending_inventory_exact":True,
        "turkish_entries":len(tr),"missing_keys":len(en.keys()-tr.keys()),
        "turkish_sha256":hashlib.sha256(raw).hexdigest()}
assert result["turkish_sha256"]==manifest["summary"]["turkish_after_sha256"]
(ROOT/"reports/broad-alignment-validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
