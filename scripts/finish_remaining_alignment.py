"""Review the remaining inventory against the recorded broad-batch baseline.

The explicit specifications below are reviewed expressions, not a dictionary
that blindly fills missing keys. Run without arguments to prepare the log;
--apply writes the verified result and refreshes the pending-key inventory.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter

from alignment_common import ROOT, render

parser=argparse.ArgumentParser()
parser.add_argument("--apply",action="store_true")
args=parser.parse_args()
read=lambda name:json.loads((ROOT/name).read_bytes())
committed=lambda name:subprocess.check_output(["git","show",f"033d895:{name}"],cwd=ROOT)
reference=(ROOT/"english-wbw-translation.json").read_bytes()
assert reference==committed("english-wbw-translation.json")
en=json.loads(reference)
tr=json.loads(committed("turkish-wbw-translation.json"))
for name in ["continued-alignment-changes.json","broad-alignment-changes.json"]:
    for group in read("reports/"+name)["groups"]:
        assert group["before"]=={k:tr.get(k) for k in group["members"]},group["members"]
        tr.update(group["after"])
tr={k:tr[k] for k in en if k in tr}
baseline_bytes=(json.dumps(tr,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
assert hashlib.sha256(baseline_bytes).hexdigest()==read("reports/broad-alignment-changes.json")["summary"]["turkish_after_sha256"]
numeric=lambda k:tuple(map(int,k.split(":")))
groups,used=[],set()

def at(key,offset):
    s,a,w=key.split(":")
    return f"{s}:{a}:{int(w)+offset}"

def add(members,parts,origins,reason,category="explicit_alignment",revised=False,normalization=None,allow_existing=False):
    assert not used.intersection(members),members
    assert allow_existing or any(k not in tr for k in members),members
    assert all(k in en for k in members)
    expression="".join(p["text"] for p in parts)
    assert expression.strip()
    if not revised:
        material=[]
        for k in origins:
            mode=normalization.get(k) if isinstance(normalization,dict) else normalization
            text=tr[k]
            material.append(text.replace("(","").replace(")","") if mode=="grammatical_parentheses" else text.replace("(","[").replace(")","]"))
        original=" ".join(material)
        assert original==expression,(members,original,expression)
    group={"members":members,"english":{k:en[k] for k in members},
           "before":{k:tr.get(k) for k in members},"parts":parts,"expression_origins":origins,
           "shared_expression":expression,"after":{k:render(parts,k) for k in members},
           "zero_surface_keys":[k for k in members if not any(p["role"]==k and p["text"].strip() for p in parts)],
           "lexical_revision":revised,"category":category,"reason":reason,
           "review_status":"local_alignment_review; whole-ayah semantic certification remains separate"}
    if normalization:group["origin_normalization"]=normalization
    groups.append(group)
    used.update(members)

def pair(key,segments,reason="Individually inspected complementary views of the existing Turkish expression.",category="explicit_pair",revised=False,normalization=None):
    prev=at(key,-1)
    if used.intersection([prev,key]):return
    assert prev in tr and key not in tr,key
    parts=[{"text":text,"role":prev if owner==0 else key if owner==1 else "context"} for owner,text in segments]
    add([prev,key],parts,[prev],reason,category,revised,normalization)

# Explicit noun, postposition, predicate, and possessive boundaries.
for key,segments in {
    "2:74:14":[(2,"öyle "),(1,"taş")],
    "2:102:27":[(0,"hiç "),(1,"kimse"),(2,"ye")],
    "2:102:48":[(0,"hiç "),(1,"kimse"),(2,"ye")],
    "2:102:29":[(1,"de"),(0,"medikçe")],
    "2:130:18":[(1,"salihler"),(0,"dendir")],
    "2:194:14":[(1,"saldır"),(0,"dığı")],
    "2:212:8":[(1,"kimseler"),(0,"le")],
    "2:213:38":[(1,"ayrılığa düş"),(0,"tükleri")],
    "2:215:14":[(0,"ve "),(1,"yolda kalmış[lar]")],
    "2:235:41":[(1,"içiniz"),(0,"den geçen")],
    "2:236:16":[(1,"eli geniş olan")],
    "2:236:19":[(1,"eli dar olan"),(2," da")],
    "2:240:19":[(1,"bir şey")],
    "2:240:24":[(1,"uygun olan"),(0,"ı")],
    "2:245:3":[(2,"o "),(1,"kimse")],
    "2:255:22":[(1,"ki")],
    "2:255:30":[(1,"onların önün"),(0,"de")],
    "2:265:10":[(1,"kendilerindeki"),(0,"ni"),(2," [imanı]")],
    "2:275:13":[(1,"dokun"),(0,"up")],
    "2:280:14":[(1,"bilir"),(0,"seniz")],
    "3:4:18":[(1,"öc"),(2," "),(0,"alandır")],
    "3:9:7":[(0,"asla "),(1,"şüphe"),(0," olmayan")],
    "3:25:6":[(0,"hiç "),(1,"şüphe"),(0," olmayan")],
    "3:46:7":[(0,"ve "),(1,"iyiler"),(0,"den olacaktır")],
    "3:78:13":[(1,"Kitap"),(0,"ta")],
    "3:85:13":[(1,"kaybedenler"),(0,"den olacaktır")],
    "3:118:8":[(1,"kendiniz"),(0,"den"),(1," başkasını")],
    "3:125:7":[(2,"onlar "),(1,"ansızın")],
    "3:154:19":[(1,"hak"),(0,"sız")],
    "3:154:55":[(1,"evleriniz"),(0,"de"),(2," dahi")],
    "3:154:62":[(1,"yatacakları yer"),(0,"i")],
    "3:160:11":[(1,"kimse")],
    "3:164:7":[(1,"gönder"),(0,"mekle")],
    "3:164:20":[(1,"bulunuyor"),(0,"larken")],
    "3:193:17":[(1,"kötülüklerimiz"),(2,"i")],
    "4:6:19":[(1,"büyü"),(0,"yüp [geri alacaklar] diye")],
    "4:9:3":[(1,"şayet")],
    "4:11:54":[(1,"ya da")],
    "4:23:29":[(1,"eğer")],
    "4:24:25":[(1,"onlar"),(0,"dan")],
    "4:25:43":[(1,"üzeri"),(0,"ne")],
    "4:29:14":[(1,"rızanız"),(0,"la yaptığınız")],
    "4:30:10":[(0,"ve "),(1,"bu")],
    "4:33:16":[(1,"üzerine")],
    "4:36:15":[(1,"yakın")],
    "4:38:10":[(0,"ve "),(1,"günü"),(2,"ne")],
    "4:42:10":[(1,"yer"),(0," ile")],
    "4:46:2":[(1,"öyleleri"),(0," var ki")],
    "4:47:10":[(1,"yanınızda"),(0,"kini")],
    "4:48:10":[(1,"başkasını")],
    "4:49:4":[(1,"şu")],
    "4:58:14":[(1,"hükmet"),(0,"me"),(1,"niz"),(2,"i")],
    "4:63:14":[(1,"içleri"),(0,"ne işleyecek")],
    "4:65:6":[(1,"seni hakem yap"),(0,"arak")],
    "4:94:37":[(1,"şeyleri")],
    "4:103:17":[(1,"üzerine")],
    "4:117:4":[(1,"O'nu "),(0,"bırakıp da")],
    "4:119:16":[(1,"yerine")],
    "4:128:27":[(1,"şeyleri")],
    "4:129:4":[(2,"[tam] "),(1,"adalet")],
    "4:148:7":[(1,"söz"),(0," söylenmesini")],
    "4:153:33":[(1,"bu"),(0,"ndan"),(2," da")],
    "4:154:15":[(1,"cumartesi[yasakları]"),(0,"nı")],
    "4:172:9":[(0,"ve "),(1,"melekler"),(2," de")],
    "4:173:26":[(0,"ve "),(1,"bir yardımcı")],
    "5:41:10":[(1,"onlar"),(2," "),(0,"ki")],
    "5:46:10":[(1,"elleri"),(0,"nde")],
    "5:46:21":[(1,"elleri"),(0,"nde")],
    "5:48:8":[(1,"elleri"),(0,"nde")],
    "5:48:39":[(0,"ile")],
    "5:59:5":[(1,"hoşlanmıyorsunuz")],
    "5:60:26":[(1,"düz")],
    "5:90:11":[(1,"işi")],
    "5:99:2":[(1,"üzerine"),(2," düşen")],
    "5:106:19":[(1,"siz"),(0,"den"),(1," olmayan")],
    "5:106:43":[(1,"akraba"),(2," da")],
    "5:107:4":[(1,"onlar"),(2,"ın")],
    "5:110:19":[(1,"beşik"),(0,"te iken")],
    "5:113:15":[(2,"bizzat "),(1,"şahit")],
    "6:7:6":[(1,"kağıt"),(0," üzerine"),(2," yazılı")],
    "6:12:18":[(1,"şüphe"),(0," olmayan")],
    "6:35:9":[(1,"ara"),(0," ki")],
    "6:59:11":[(1,"kara"),(0,"da olan")],
    "6:71:22":[(1,"çöl"),(0,"de"),(2," bıraktıkları")],
    "6:79:5":[(1,"yoktan var ed"),(0,"ene")],
    "6:89:17":[(1,"inkar")],
    "6:116:6":[(1,"yeryüzü"),(0,"nde")],
    "6:133:12":[(1,"dile"),(0,"diğini")],
    "6:135:13":[(1,"sonu"),(2,"nun")],
    "6:136:23":[(1,"olan"),(2," [ise]")],
    "6:140:8":[(1,"bilgi"),(0,"sizlik yüzünden")],
    "6:141:16":[(0,"ve "),(1,"benze"),(0,"mez")],
    "6:144:27":[(1,"uydur"),(0,"andan")],
    "6:148:10":[(1,"babalarımız"),(2," da")],
    "6:156:11":[(1,"biz"),(0," ise "),(1,"idik")],
    "6:159:14":[(1,"Allah"),(0,"'a [kalmış]tır")],
    "7:4:3":[(1,"kent[ler]"),(0,"i")],
    "7:20:13":[(1,"sizi men'etti")],
    "7:53:21":[(1,"şefa'atçilerimiz")],
    "7:57:7":[(1,"önü"),(0,"nde")],
    "7:90:12":[(1,"ziyana uğrarsınız")],
    "7:100:10":[(1,"eğer")],
    "7:148:7":[(1,"zinetleri"),(0,"nden"),(2," yapılmış")],
    "7:169:3":[(1,"sonra onların")],
    "7:173:11":[(1,"onlar"),(0,"dan"),(1," sonra"),(2," gelen")],
    "7:205:10":[(1,"bir ses"),(0,"le")],
    "8:3:5":[(0,"ve "),(1,"ver"),(0,"diğ"),(1,"imiz rızık"),(0,"tan")],
    "8:32:10":[(1,"senin yanın"),(0,"dan"),(2," gelmiş")],
    "8:41:3":[(1,"al"),(0,"dığ"),(1,"ınız ganimetler"),(2,"in")],
    "8:41:11":[(0,"ve "),(1,"akrabalar"),(0,"a")],
    "8:41:15":[(0,"ve "),(1,"yolcu[lar]a")],
    "8:60:8":[(0,"ve "),(1,"cihad için bağlanıp beslenen")],
    "8:60:17":[(1,"onların dışı"),(0,"nda")],
    "9:7:16":[(1,"onlar dürüst davran"),(0,"dıkça")],
    "9:27:8":[(1,"kimse"),(0,"nin")],
    "9:49:10":[(2,"onlar zaten "),(1,"fitne"),(0,"ye")],
    "9:93:4":[(1,"kimseler"),(0,"in")],
    "9:99:2":[(1,"bedevi Araplar"),(0,"dan")],
    "9:111:9":[(1,"kendilerinin"),(0," olmak üzere")],
    "9:114:8":[(1,"bir söz"),(0,"den")],
    "9:120:18":[(1,"onun canı"),(0,"ndan önce")],
    "9:127:12":[(1,"birisi")],
    "10:10:11":[(1,"hamdolsun"),(0,"'dur")],
    "10:26:10":[(0,"ve "),(1,"aşağılık")],
    "10:27:14":[(1,"kurtaracak")],
    "10:61:13":[(1,"yapılacaklar"),(2,"dan")],
    "11:20:14":[(1,"dostları")],
    "11:34:7":[(1,"öğüt ver"),(0,"mek")],
    "11:57:8":[(1,"siz"),(2,"e")],
    "11:61:12":[(1,"ilahınız")],
    "11:69:13":[(1,"getirdi")],
    "11:76:14":[(1,"geri çevril"),(0,"meyecek")],
    "11:82:11":[(1,"balçık"),(0,"tan"),(2," pişirilmiş")],
    "11:89:6":[(1,"isabet ed"),(0,"enin")],
    "11:93:4":[(1,"imkanınız"),(0,"ın elverdiğini")],
    "11:106:2":[(1,"kimseler")],
    "11:121:7":[(1,"imkanınız"),(0,"ın elverdiğini")],
    "12:21:5":[(1,"Mısır"),(0,"'lı")],
    "12:23:5":[(1,"onun evi"),(0,"nde iken")],
    "12:28:10":[(1,"sizin hileniz"),(0,"dir")],
    "12:38:17":[(1,"bir lutfu"),(0,"dur")],
    "12:47:14":[(1,"yiye"),(0,"ceğiniz")],
    "12:67:16":[(1,"Allah"),(0,"'tan"),(2," gelecek")],
    "12:82:4":[(1,"bulun"),(0,"duğ"),(1,"umuz")],
    "12:107:3":[(1,"kendilerine gel"),(0,"meyeceğinden")],
    "13:11:17":[(1,"bir milet")],
    "13:11:35":[(1,"koruyucuları")],
    "13:14:27":[(1,"boşa gider")],
    "13:31:24":[(1,"şayet")],
    "13:33:24":[(1,"söz"),(2," mü [söylüyorsunuz]?")],
    "14:16:2":[(1,"ardı"),(0,"ndan"),(2," da")],
    "14:16:6":[(2,"bir "),(1,"su"),(2,"y")],
    "14:22:15":[(1,"benim")],
    "15:54:5":[(1,"bana dokun"),(0,"asına")],
    "15:74:8":[(1,"çamur"),(0,"dan"),(2," pişmiş")],
    "16:27:9":[(1,"et"),(0,"tiğiniz")],
    "16:37:4":[(1,"onların yola gelmeleri"),(0,"ni")],
    "16:46:4":[(1,"dönüp dolaşır"),(0,"larken")],
    "16:53:4":[(2,"her "),(1,"ni'met")],
    "16:92:15":[(1,"olduğu"),(0," için")],
    "16:92:18":[(1,"daha çok")],
    "16:122:9":[(1,"iyiler"),(0,"dendir")],
    "17:24:11":[(1,"beni "),(0,"nasıl "),(1,"yetiştirdiler"),(0,"se")],
    "17:34:7":[(1,"o")],
    "17:36:15":[(1,"o[yaptığı]"),(2,"ndan")],
    "17:53:5":[(1,"o")],
    "17:69:4":[(1,"sizi gönder"),(0,"ip")],
    "17:72:4":[(1,"şu [dünyada]")],
    "17:74:9":[(1,"bir parça")],
    "17:79:5":[(1,"özgü"),(0," olarak")],
    "17:93:15":[(1,"indir"),(0,"medikçe")],
    "17:106:7":[(1,"ağır ağır")],
    "17:110:9":[(1,"çağır"),(0,"sanız")],
    "18:15:15":[(1,"uydur"),(0,"andan")],
    "18:17:9":[(1,"sağ"),(0,"a doğru")],
    "18:17:14":[(1,"sol"),(0,"a doğru")],
    "18:37:8":[(1,"seni yarat"),(0,"anı")],
    "18:49:19":[(2,"her [yaptığımız] şeyi "),(1,"sayıp döküyor")],
    "18:87:3":[(1,"kim")],
    "18:93:11":[(1,"neredeyse")],
    "19:8:5":[(1,"benim")],
    "19:66:5":[(1,"öl"),(0,"düğ"),(1,"üm")],
    "20:108:5":[(0,"hiç "),(1,"pürüzü"),(0," olmayan")],
    "20:128:14":[(1,"bu"),(0,"nda vardır")],
    "21:2:2":[(1,"kendilerine gel"),(2,"en")],
    "21:25:8":[(0,"diye "),(1,"vahyet"),(0,"mediğimiz")],
    "21:52:9":[(1,"siz"),(2,"in")],
    "21:54:4":[(1,"siz")],
    "21:55:7":[(1,"şaka"),(0," mı "),(1,"yapıyorsun"),(2,"?")],
    "21:90:13":[(1,"hayır [işlere]")],
    "22:41:2":[(1,"eğer")],
    "22:60:6":[(1,"yapılan ceza"),(0,"nın")],
    "23:21:8":[(1,"içinde"),(0,"kinden")],
    "23:63:6":[(1,"bu"),(0,"ndan")],
    "24:6:17":[(1,"doğru söyleyenler"),(0,"den olduğuna")],
    "24:8:11":[(1,"yalan söyleyenler"),(0,"den olduğuna")],
    "24:31:61":[(1,"mahrem yerleri"),(0,"ni"),(2,";")],
    "24:33:15":[(1,"sahip ol"),(0,"duklarından")],
    "24:58:23":[(1,"öğle vakti")],
    "24:63:20":[(1,"onun emri"),(0,"ne")],
    "25:18:12":[(1,"veliler")],
    "25:20:5":[(1,"elçiler"),(2,"den")],
    "25:41:9":[(1,"gönder"),(0,"miş")],
    "25:49:7":[(1,"yarat"),(0,"tığımız")],
    "25:57:9":[(1,"iste"),(0,"me"),(1,"niz")],
    "25:74:7":[(1,"eşlerimiz"),(0,"i")],
    "26:20:6":[(1,"dalalette"),(0," idim")],
    "26:42:6":[(1,"yakınlar"),(0,"dan olacaksınız")],
    "26:92:6":[(1,"tap"),(0,"tıklarınız")],
    "26:100:4":[(1,"şefa'atçilerimiz")],
    "26:186:9":[(0,"mutlaka "),(1,"yalancılar"),(0,"dan")],
    "27:20:12":[(1,"kayıplar"),(0,"dan"),(2,"-")],
    "27:36:12":[(1,"size ver"),(0,"diğinden")],
    "27:57:7":[(1,"kalanlar"),(0,"dan olmasını")],
    "27:72:4":[(1,"olmuştur")],
    "27:87:8":[(1,"gökler"),(0,"de bulunan")],
    "27:87:11":[(0,"ve "),(1,"yer"),(0,"de bulunan")],
    "27:89:9":[(1,"korku"),(0,"dan uzaktırlar")],
    "28:25:5":[(1,"utan"),(0,"a "),(1,"utan"),(0,"a")],
    "28:61:17":[(1,"getirilecekler"),(0,"den olan")],
    "28:70:10":[(1,"ilk"),(2," olan")],
    "28:81:17":[(1,"kendini kurtaranlar"),(0,"dan")],
    "29:2:6":[(1,"de"),(0,"mekle")],
    "29:14:16":[(1,"haksızlık edenler"),(2,"i")],
    "30:9:21":[(1,"bunların imar et"),(0,"tiklerinden")],
    "30:28:13":[(1,"ortaklar"),(2,"dan")],
    "30:32:2":[(1,"onlar"),(0," ki")],
    "30:55:9":[(1,"bir sa'at"),(0,"ten başka")],
    "30:56:9":[(1,"yazgısı"),(0,"nca")],
    "31:32:13":[(1,"kara"),(0,"ya"),(2," çıkarıp")],
    "32:17:8":[(1,"aydınlatıcı")],
    "32:18:2":[(2,"hiç "),(1,"olur"),(0," mu"),(2,"?")],
    "33:2:10":[(1,"şeyleri")],
    "33:36:3":[(1,"inanmış bir erkek için")],
    "33:36:16":[(2,"o "),(1,"iş"),(0,"i")],
    "33:38:3":[(1,"üzerine")],
    "33:50:8":[(1,"ver"),(0,"diğ"),(1,"in")],
    "33:50:14":[(1,"ganimet ver"),(0,"diğinden")],
    "33:52:12":[(1,"başka eşler"),(0,"le")],
    "33:55:27":[(1,"üzerine")],
    "34:6:6":[(1,"indiril"),(0,"enin")],
    "34:6:11":[(1,"gerçek"),(0," olduğunu")],
    "34:9:4":[(1,"bulunan"),(0,"ı")],
    "34:14:8":[(1,"onun öl"),(0,"düğ"),(1,"ü"),(2,"nü")],
    "34:14:19":[(1,"eğer")],
    "34:21:6":[(1,"zorlayıcı bir gücü")],
    "34:54:13":[(1,"içinde"),(0,"dirler")],
    "35:13:28":[(1,"bir çekirdek zarı"),(2,"na "),(0,"bile")],
    "35:28:2":[(1,"insanlar"),(0,"dan vardır")],
    "35:29:10":[(1,"ver"),(0,"diğ"),(1,"imiz rızık"),(0,"tan")],
    "35:36:14":[(1,"onun azabı")],
    "36:8:8":[(1,"çeneler"),(0,"e kadar"),(2," dayanır")],
    "36:19:5":[(1,"size öğüt veril"),(0,"diğiiçin mi"),(2,"?")],
    "36:42:4":[(1,"onun gibi")],
    "37:8:4":[(1,"melekler"),(0,"i")],
    "37:54:3":[(1,"siz")],
    "37:83:3":[(1,"onun kolu"),(0,"ndan idi")],
    "37:92:2":[(0,"ne"),(1,"yiniz"),(0," var"),(2,"?")],
    "38:11:6":[(1,"derme çatma")],
    "38:15:10":[(1,"geri dönmesi")],
    "38:58:3":[(1,"ona [azaba] benzer")],
    "38:75:8":[(1,"yarat"),(0,"tığ"),(1,"ım"),(0,"a")],
    "39:3:22":[(1,"ne ki")],
    "39:26:12":[(1,"bil"),(0,"selerdi")],
    "39:28:5":[(1,"pürüzü")],
    "39:29:6":[(1,"ortakları")],
    "39:47:25":[(1,"hesabet"),(0,"medikleri")],
    "40:15:8":[(1,"emri"),(0,"nden olan")],
    "40:66:18":[(1,"teslim ol"),(0,"makla")],
    "40:69:4":[(1,"kimseler"),(0,"i")],
    "40:71:4":[(1,"boyunları"),(0,"nda")],
    "40:80:8":[(1,"gönülleriniz"),(0,"deki")],
    "41:9:5":[(1,"yarat"),(0,"anı")],
    "41:34:8":[(1,"olan"),(0,"la")],
    "41:47:8":[(1,"meyvalar")],
    "41:52:16":[(1,"bir ayrılığa düşen")],
    "42:23:3":[(1,"müjdele"),(0,"diğidir")],
    "42:34:7":[(1,"birçoğu"),(0,"nu"),(2," da")],
    "42:44:18":[(1,"geri dönecek")],
    "42:46:3":[(1,"onların")],
    "43:55:2":[(1,"onlar bizi kızdır"),(0,"ınca")],
    "44:5:3":[(1,"katımız"),(0,"dan olan")],
    "45:11:10":[(1,"çok çetin")],
    "46:10:16":[(1,"bunun benzeri"),(0,"ni")],
    "46:31:10":[(1,"günahlarınız"),(0,"dan bir kısmını")],
    "46:35:24":[(1,"helak"),(0," mı "),(1,"edilecektir"),(2,"?")],
    "48:25:11":[(1,"var"),(0,"ma"),(1,"sı"),(2,"na")],
    "49:9:15":[(1,"saldır"),(0,"an tarafla")],
    "51:17:4":[(1,"geceler"),(0,"i")],
    "51:45:4":[(1,"ayağa kalk"),(0,"ma"),(2,"ya")],
    "52:12:3":[(1,"içinde")],
    "54:37:4":[(1,"onun konukları"),(0,"ndan")],
    "55:11:5":[(1,"salkım"),(0,"lı")],
    "55:12:3":[(1,"sap"),(0,"lı"),(2," ve "),(1,"yaprak"),(0,"lı")],
    "56:18:5":[(1,"kaynağı"),(0,"ndan"),(2," doldurulmuş")],
    "56:61:2":[(1,"diye")],
    "56:86:2":[(1,"eğer")],
    "58:2:5":[(1,"kadınlar"),(0,"a")],
    "58:3:4":[(1,"kadınları"),(0,"na")],
    "59:17:5":[(1,"ateş"),(0,"te kalmaları")],
    "60:7:8":[(1,"düşman ol"),(0,"duklarınız")],
    "61:6:15":[(1,"elim"),(0,"de")],
    "62:9:21":[(1,"bilir"),(0,"seniz")],
    "63:7:12":[(1,"dağılıp git"),(0,"sinler")],
    "65:6:3":[(1,"yer"),(0,"de")],
    "67:22:5":[(1,"yüz"),(0,"üstü")],
    "68:25:3":[(1,"engelle"),(0,"me"),(2,"ye")],
    "71:26:9":[(1,"kafirler"),(2,"den")],
    "74:49:4":[(1,"öğüt"),(0,"ten")],
    "76:8:4":[(1,"sev"),(0,"dikleri")],
    "79:41:2":[(1,"cennet"),(0,"tir")],
    "79:43:4":[(1,"onun söyle"),(0,"yesin")],
    "85:7:3":[(1,"şeyleri")],
    "88:7:6":[(1,"açlığı"),(0,"ndan"),(2," bir şey")],
    "89:7:3":[(1,"sütun"),(0,"lu")],
    "105:2:5":[(1,"boşa")],
    "111:3:4":[(1,"alev"),(0,"li")],
}.items():
    pair(key,segments)

# Additional compound and multi-entry groups are specified below.

# Established min/dun paraphrases. An unpronounced Turkish preposition is
# recorded explicitly, rather than inventing a second ablative for bırakıp.
for key in sorted(en.keys()-tr.keys(),key=numeric):
    prev,nextkey=at(key,-1),at(key,1)
    if key in used or prev in used or prev not in tr:
        continue
    raw=tr[prev]
    if raw in {"O'ndan başka","ondan başka"} and any(word in en[key].lower() for word in ["beside","other than"]):
        base=raw[:raw.index("ndan")]
        pair(key,[(1,base),(0,"ndan"),(1," başka")],"The overt ablative and the pronoun/postposition belong to distinct source positions.","pronoun_postposition")
    elif raw in {"bırakıp","bırakıp da"} and any(word in en[key].lower() for word in ["beside","instead","other than"]):
        pair(key,[(1,raw)],"The combined min/dun relation is paraphrased by the inherited bırakıp expression. No second case ending is pronounced independently.","idiomatic_zero")
    elif raw in {"başka","başkasını","başkalarına","dışında","bırakıp","bırakıp da","karşı"} and nextkey in tr and any(word in en[key].lower() for word in ["beside","instead","other than"]):
        noun=tr[nextkey].replace("(","").replace(")","")
        if not (en[nextkey].lower().find("allah")>=0 or en[nextkey].lower().find("gracious")>=0):continue
        if used.intersection([prev,key,nextkey]):continue
        match=re.search(r"(?:'?[dt][ae]n)$",noun)
        if match:
            parts=[{"text":noun[:match.start()],"role":nextkey},{"text":match.group(),"role":prev},
                   {"text":" ","role":"context"},{"text":raw,"role":key}]
        elif raw in {"bırakıp","bırakıp da"}:
            parts=[{"text":noun,"role":nextkey},{"text":" ","role":"context"},{"text":raw,"role":key}]
        elif raw=="karşı":
            parts=[{"text":noun,"role":nextkey},{"text":" ","role":"context"},{"text":raw,"role":key}]
        elif raw=="dışında":
            parts=[{"text":noun,"role":nextkey},{"text":" ","role":"context"},
                   {"text":"dışı","role":key},{"text":"nda","role":prev}]
        else:continue
        add([prev,key,nextkey],parts,[nextkey,prev],"The case is on the later noun, while the min/dun lexical relation was displaced onto the first source key. Preserve all words and expose the actual three-entry construction.","three_entry_postposition",normalization="grammatical_parentheses")

# The predicates were already translated; the missing pronoun/function key
# must share the negative surface on the following word, not acquire a copy.
for first,pronoun,verb,negative in [
    ("2:123:16","onlara","yardım da edilmez","mez"),
    ("3:108:7","Allah","istemez","mez"),
    ("3:170:17","onların","üzüntüye uğramayacaklarına","ma"),
    ("5:28:6","ben","uzatmam","ma"),
    ("6:111:13","onlar yine de","inanmazlardı","maz"),
    ("7:43:17","biz","(doğruyu) bulamazdık","maz"),
    ("11:20:18","onlar","güç yetiremezlerdi","mez"),
    ("16:28:8","biz","yapmıyorduk","mı"),
    ("21:65:7","bunlar","konuşmazlar","maz"),
    ("40:56:15","onlar","erişemeyecekleri","me"),
]:
    middle,last=at(first,1),at(first,2)
    assert tr[first]==pronoun and tr[last]==verb,first
    surface=verb.replace("(","[").replace(")","]")
    start=surface.index(negative)
    parts=[{"text":pronoun,"role":middle},{"text":" ","role":"context"},
           {"text":surface[:start],"role":last},{"text":negative,"role":first},
           {"text":surface[start+len(negative):],"role":last}]
    add([first,middle,last],parts,[first,last],"Move the overt pronoun to its missing position and expose negation on the following predicate. Turkish passive and nominal clause constructions may realize the source pronoun in an oblique or possessive form.","displaced_negative_pronoun")

# Restrictive not...except constructions with an overt pronoun, including
# nominal copulas that have no independent Turkish surface here.
for key in ["2:78:9","5:110:60","6:7:13","6:25:29","6:29:3","7:184:8","7:188:23",
            "8:31:14","11:50:15","12:31:29","12:104:7","14:10:20","19:93:2","34:46:17"]:
    pair(key,[(1,tr[at(key,-1)].replace("(","[").replace(")","]"))],
         "The noun/pronoun was placed at the negative source key. Restriction is expressed by the separate Turkish exception phrase; no extra negative word is inserted into this view.","restrictive_pronoun")

# Relative/person markers with a case carried by the later passive predicate.
for first in ["2:101:12","3:186:6","5:5:18","9:29:19","5:107:10"]:
    middle,last=at(first,1),at(first,2)
    if used.intersection([first,middle,last]):continue
    pre,word=tr[first],tr[last]
    match=re.search(r"(enler)(den)$",word)
    assert match,(first,word)
    parts=[{"text":pre+" "+word[:match.start()],"role":last},
           {"text":match[1],"role":middle},{"text":match[2],"role":first}]
    add([first,middle,last],parts,[first,last],"The case ending on the passive phrase belongs to the earlier preposition; the relative plural belongs to the intervening person marker.","relative_case_chain")

# Temporal min/ba'd/nominal chains whose English gloss 'that' denotes a
# demonstrative or nominal head here, rather than an absent lexical verb.
for first in ["3:61:4","3:89:4","3:94:6","5:43:10","24:5:4"]:
    middle,last=at(first,1),at(first,2)
    post,noun=tr[first],tr[last]
    assert post in {"sonra","sonra da"}
    ending="ndan" if noun in {"ondan","bundan"} else "den"
    assert noun.endswith(ending)
    parts=[{"text":noun[:-len(ending)],"role":last},{"text":ending,"role":first},
           {"text":" ","role":"context"},{"text":post,"role":middle}]
    add([first,middle,last],parts,[last,first],"Expose the already-present ablative, temporal postposition, and demonstrative/nominal head as three complementary views.","temporal_demonstrative")

# Quantifier words intervene before the noun's grammatical ending.
for first,quantifier,noun,root,ending in [
    ("3:189:6","he","şeye","şey","e"),
    ("5:17:39","he","şeyi","şey","i"),
    ("11:57:18","her","şeyi","şey","i"),
    ("34:21:18","her","şeyi","şey","i"),
    ("35:42:10","herbir","milletten","millet","ten"),
    ("82:8:1","hangi;","surette","suret","te"),
    ("95:4:4","en güzel","biçimde","biçim","de"),
]:
    middle,last=at(first,1),at(first,2)
    assert tr[first]==quantifier and tr[last]==noun,first
    fixed="her" if quantifier=="he" else quantifier
    parts=[{"text":fixed,"role":middle},{"text":" ","role":"context"},
           {"text":root,"role":last},{"text":ending,"role":first}]
    add([first,middle,last],parts,[first,last],"The determiner belongs to the middle source entry; the preposition's written case appears on the later noun. Correct inherited he to her where explicitly recorded.","intervening_quantifier",revised=quantifier=="he")

# Complementizer plus emphatic/negative adverb. The actual negative verb is
# retained at the following source key; an adverb is not mislabeled as that.
for key in ["47:29:8","64:7:5","72:5:4","72:7:6","72:12:4","72:28:3","73:20:22","84:14:4"]:
    pair(key,[(1,tr[at(key,-1)])],"The existing emphatic/negative adverb belongs to this source entry. The complementizer has no separate overt surface in this local expression; the following nominalized predicate carries the clause structure.","complementizer_adverb")

def indexed_group(first,segments,origins=None,reason="Explicit multi-entry phrase decomposition.",category="multi_entry_phrase",revised=False):
    last=max(owner for owner,text in segments if isinstance(owner,int))
    members=[at(first,i) for i in range(last+1)]
    parts=[{"text":text,"role":at(first,owner) if isinstance(owner,int) else "context"} for owner,text in segments]
    add(members,parts,[first] if origins is None else origins,reason,category,revised)

from remaining_special_cases import apply_special_cases
apply_special_cases(en,tr,pair,indexed_group,add,at,used,groups)

updates={k:v for g in groups for k,v in g["after"].items()}
assert len(updates)==sum(len(g["members"]) for g in groups)
for group in groups:
    assert len(group["members"])==len(set(group["members"]))
    assert all(p["role"] in group["members"] or p["role"]=="context" for p in group["parts"])
    for value in group["after"].values():
        assert value.replace("(","").replace(")","")==group["shared_expression"]
        stack=[]
        for char in value:
            if char in "([":stack.append(char)
            elif char in ")]":
                assert stack and stack.pop()==(")"==char and "(" or "["),value
        assert not stack,value
expected=tr|updates
expected={k:expected[k] for k in en if k in expected}
output=(json.dumps(expected,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
summary={"baseline":"033d895 plus continued and broad manifests","baseline_missing_keys":len(en.keys()-tr.keys()),
         "added_keys":len(expected)-len(tr),"modified_existing_keys":sum(k in tr and tr[k]!=v for k,v in updates.items()),
         "remaining_missing_keys":len(en.keys()-expected.keys()),"groups":len(groups),
         "groups_by_category":dict(Counter(g["category"] for g in groups)),
         "zero_surface_views":sum(len(g["zero_surface_keys"]) for g in groups),
         "lexical_revision_groups":sum(g["lexical_revision"] for g in groups),
         "english_sha256":hashlib.sha256(reference).hexdigest(),"turkish_before_sha256":hashlib.sha256(baseline_bytes).hexdigest(),
         "turkish_after_sha256":hashlib.sha256(output).hexdigest()}
(ROOT/"reports/remaining-alignment-changes.json").write_text(json.dumps({"summary":summary,"groups":groups},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
buffer=io.StringIO(newline="")
writer=csv.writer(buffer,lineterminator="\n")
writer.writerow(["key","english","operation","before","after","category","zero_surface","lexical_revision","reason"])
for group in groups:
    for key in group["members"]:
        writer.writerow([key,en[key],"modify" if key in tr else "add",tr.get(key,""),group["after"][key],group["category"],
                         key in group["zero_surface_keys"],group["lexical_revision"],group["reason"]])
(ROOT/"reports/remaining-alignment-changes.csv").write_text(buffer.getvalue(),encoding="utf-8")
if args.apply:
    current=read("turkish-wbw-translation.json")
    assert current==tr or current==expected,"Unexpected working-tree edits."
    assert all(expected[k]==v for k,v in tr.items() if k not in updates)
    assert all(expected[k]==en[k] for k in en if re.fullmatch(r"\(\d+\)",en[k]))
    (ROOT/"turkish-wbw-translation.json").write_bytes(output)
    assert (ROOT/"english-wbw-translation.json").read_bytes()==reference
    missing=sorted(en.keys()-expected.keys(),key=numeric)
    pending=[]
    for key in missing:
        prev=at(key,-1)
        pending.append({"key":key,"english":en[key],"previous_key":prev,"previous_english":en.get(prev),
                        "previous_turkish":expected.get(prev),"status":"requires_individual_review"})
    (ROOT/"reports/alignment-pending.json").write_text(json.dumps(pending,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Preserve historical concerns while showing the current value and
    # current zero-surface status. Structural coverage is not semantic proof.
    review,latest={},{}
    for filename in ["contextual-alignment-changes.json","continued-alignment-changes.json","broad-alignment-changes.json","remaining-alignment-changes.json"]:
        for group in read("reports/"+filename)["groups"]:
            for key in group["members"]:
                latest[key]=key in group.get("zero_surface_keys",[])
                if key in group.get("zero_surface_keys",[]) or group.get("lexical_revision",False):
                    item=review.setdefault(key,{"key":key,"english":en[key],"status":"requires_semantic_review","history":[]})
                    item["history"].append({"manifest":filename,"reason":group["reason"],
                                            "zero_surface":key in group.get("zero_surface_keys",[]),
                                            "lexical_revision":group.get("lexical_revision",False)})
    for key,item in review.items():
        item["turkish"]=expected[key]
        item["currently_context_only"]=latest[key]
    (ROOT/"reports/linguistic-review.json").write_text(json.dumps(sorted(review.values(),key=lambda r:numeric(r["key"])),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary,indent=2))
