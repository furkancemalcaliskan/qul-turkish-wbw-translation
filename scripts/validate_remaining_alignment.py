"""Verify the final batch independently against its committed provenance."""
import hashlib
import json
import re
import subprocess

from alignment_common import ROOT,render

def unique(pairs):
    result={}
    for key,value in pairs:
        assert key not in result,f"Duplicate JSON key: {key}"
        result[key]=value
    return result

read=lambda name:json.loads((ROOT/name).read_bytes(),object_pairs_hook=unique)
reference=(ROOT/"english-wbw-translation.json").read_bytes()
assert reference==subprocess.check_output(["git","show","4503cdc:english-wbw-translation.json"],cwd=ROOT)
en=read("english-wbw-translation.json")
baseline=json.loads(subprocess.check_output(["git","show","033d895:turkish-wbw-translation.json"],cwd=ROOT),object_pairs_hook=unique)
for name in ["continued-alignment-changes.json","broad-alignment-changes.json"]:
    for group in read("reports/"+name)["groups"]:
        assert group["before"]=={k:baseline.get(k) for k in group["members"]}
        baseline.update(group["after"])
manifest=read("reports/remaining-alignment-changes.json")
baseline={k:baseline[k] for k in en if k in baseline}
raw_baseline=(json.dumps(baseline,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
assert hashlib.sha256(raw_baseline).hexdigest()==manifest["summary"]["turkish_before_sha256"]
updates={}
for group in manifest["groups"]:
    assert group["before"]=={k:baseline.get(k) for k in group["members"]}
    if not group["lexical_revision"]:
        material=[]
        for key in group["expression_origins"]:
            normalization=group.get("origin_normalization")
            mode=normalization.get(key) if isinstance(normalization,dict) else normalization
            raw=baseline[key]
            material.append(raw.replace("(","").replace(")","") if mode=="grammatical_parentheses" else raw.replace("(","[").replace(")","]"))
        assert " ".join(material)==group["shared_expression"],group["members"]
    for key in group["members"]:
        assert key not in updates
        value=group["after"][key]
        assert value==render(group["parts"],key)
        assert value.replace("(","").replace(")","")==group["shared_expression"]
        updates[key]=value
tr=read("turkish-wbw-translation.json")
assert tr==baseline|updates
assert list(tr)==list(en)
assert all(isinstance(v,str) and v.strip() for v in tr.values())
assert all(tr[k]==v for k,v in baseline.items() if k not in updates)
markers={k:v for k,v in en.items() if re.fullmatch(r"\(\d+\)",v)}
assert len(markers)==6236 and all(tr[k]==v for k,v in markers.items())
assert len(tr)-len(baseline)==manifest["summary"]["added_keys"]==542
assert sum(k in baseline and baseline[k]!=v for k,v in updates.items())==manifest["summary"]["modified_existing_keys"]
assert read("reports/alignment-pending.json")==[]
for key,expected in {
    "2:5:4":"(Rableri)nden","2:5:5":"Rableri(nden)",
    "2:48:4":"yarar sağla(maz)","2:267:27":"Allah","2:267:28":"zengindir","2:267:29":"övülmüştür",
    "16:102:3":"Ruh(u'l-Kudüs)","16:102:4":"(Ruhu'l-)Kudüs", "63:10:2":"(size verdiğimiz rızık)tan",
    "28:23:21":"biz sulay(ama)yız","5:32:2":"(işte bu) sebep(le)",
    "13:11:17":"bir millet","14:16:6":"(bir) su",
}.items():
    assert tr[key]==expected,(key,tr[key],expected)
raw=(ROOT/"turkish-wbw-translation.json").read_bytes()
assert raw==(json.dumps(tr,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
digest=hashlib.sha256(raw).hexdigest()
assert digest==manifest["summary"]["turkish_after_sha256"]
result={"english_unchanged_from_initial":True,"english_entries":len(en),"turkish_entries":len(tr),
        "missing_keys":0,"extra_keys":0,"duplicate_keys":0,"ayah_numbers_unchanged":len(markers),
        "exact_reference_order":True,"untouched_pairs_preserved":True,"manifest_reconstruction":"passed",
        "origin_material_checks":"passed for all preservation-only groups",
        "boundary_and_displacement_regressions":"passed","turkish_sha256":digest,
        "linguistic_review_keys":len(read("reports/linguistic-review.json")),
        "scope":"Structural completion verified; not a certification of all inherited or newly reviewed meanings."}
(ROOT/"reports/remaining-alignment-validation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
