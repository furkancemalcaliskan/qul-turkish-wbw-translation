"""Explicitly reviewed compound, displacement, and lexical-repair cases."""

def apply_special_cases(en,tr,pair,indexed_group,add,at,used,groups):
    for key,segments in {
        "2:105:9":[(0,"ve "),(1,"müşrikler"),(2,"den")],
        "2:170:16":[(1,"ol"),(0,"salarda mı?")],
        "2:177:22":[(1,"sev"),(0,"diği")],
        "2:246:24":[(0,"olurmu "),(1,"ki"),(2,"?")],
        "2:253:29":[(1,"onların arkası"),(0,"ndan gelen")],
        "2:256:22":[(1,"Allah")],
        "2:279:15":[(0,"ne "),(1,"haksızlık edersiniz")],
        "2:282:39":[(1,"borç"),(0,"lu olan")],
        "3:50:4":[(1,"benden önce"),(0," gelen")],
        "3:65:8":[(0,"oysa "),(1,"indirilmiştir")],
        "3:172:6":[(1,"sonra"),(2," bile")],
        "3:178:11":[(1,"biz süre veriyoruz")],
        "5:5:29":[(1,"zina"),(0,"dan kaçınan")],
        "5:8:15":[(1,"adalet"),(2,"ten")],
        "5:77:9":[(1,"hak"),(0,"sız"),(2," yere")],
        "6:113:11":[(1,"onlar"),(2,"ın")],
        "6:148:31":[(1,"siz uyuyorsunuz")],
        "7:43:31":[(1,"işte"),(2," size")],
        "7:163:20":[(1,"cumartesi"),(0," dışındaki")],
        "9:117:14":[(1,"O zaman")],
        "11:6:7":[(1,"ait"),(2," "),(0,"olmayan")],
        "11:69:11":[(0,"ve "),(1,"hemen")],
        "11:111:4":[(0,"tastamam "),(1,"verecektir")],
        "14:34:3":[(1,"herşey"),(0,"den")],
        "15:11:6":[(1,"ol"),(0,"madıkları")],
        "16:73:6":[(1,"asla")],
        "16:92:7":[(1,"sonra")],
        "17:33:8":[(1,"hak"),(0,"sız yere")],
        "26:5:9":[(2,"olma"),(0,"dık"),(1,"ları")],
        "27:90:10":[(2,"cezalandırılıyorsunuz")],
        "35:43:14":[(2,"bekliyorlar")],
        "36:46:9":[(2,"olma"),(0,"dık"),(1,"ları")],
        "40:74:2":[(1,"başkaları"),(2,"?")],
        "43:66:3":[(2,"bekliyorlar")],
        "45:24:4":[(1,"başka"),(2," bir şey")],
        "46:21:14":[(1,"ve")],
        "98:4:8":[(2,"[ondan] "),(1,"sonra")],
    }.items():
        pair(key,segments,"Explicit review of a paraphrase/grammatical cluster. Context-only contributions remain flagged for semantic review; a preserved expression is not certified merely by adding its missing key.","reviewed_paraphrase")

    for first,prefix,tail in [("2:97:13","kendinden ","kileri"),("3:3:6","kendinden ","kini"),("35:31:9","kendinden ","kini")]:
        middle,last=at(first,1),at(first,2)
        assert tr[first]==prefix+"önce"+tail
        parts=[{"text":prefix,"role":last},{"text":"önce","role":middle},{"text":tail,"role":first}]
        add([first,middle,last],parts,[first],"Arabic between/hands is paraphrased as Turkish temporal priority. Expose the relative ending, temporal element, and reference separately; consolidate repeated inherited full phrases into complementary views.","before_hands_idiom")
    for first,pronoun,ending in [("2:286:28","biz","kilerin"),("6:148:17","onlar","")]:
        middle,last=at(first,1),at(first,2)
        parts=[{"text":pronoun,"role":last},{"text":"den" if pronoun=="biz" else "dan","role":middle},
               {"text":" ","role":"context"},{"text":"önce","role":last}]
        if ending:parts.append({"text":ending,"role":first})
        add([first,middle,last],parts,[first],"Separate the reference pronoun, ablative, temporal phrase, and overt relative ending. A relative with no identified surface remains context-only.","temporal_relative_chain")

    for first,possessive in [("7:17:3","leri"),("13:11:3","ü"),("41:14:4","leri"),("41:42:4","ü")]:
        middle,last=at(first,1),at(first,2)
        parts=[{"text":"ön","role":middle},{"text":possessive,"role":last},{"text":"nden","role":first}]
        add([first,middle,last],parts,[first],"Separate the location noun, possessive reference, and ablative instead of repeating the fused front/before expression.","spatial_possessive_chain")

    for first,segments,origins in [
        ("2:109:13",[(1,"iç"),(2,"leri"),(0,"ndeki")],None),
        ("2:210:3",[(2,"gel"),(1,"me"),(2,"si"),("context","ni")],None),
        ("4:25:10",[(2,"sahip ol"),(1,"duğ"),(2,"unuz")],None),
        ("16:71:13",[(2,"altında bulun"),(1,"anlar"),(0,"a")],None),
        ("19:63:7",[(2,"korun"),(0,"anlar"),("context","a")],None),
        ("20:99:6",[(2,"geç"),(1,"miş"),(0,"lerin")],None),
        ("4:86:11",[(2,"her"),("context"," "),(3,"şey"),(1,"i")],None),
        ("28:19:12",[(2,"beni öldür"),(1,"mek"),(0,"mi istiyorsun"),("context","?")],None),
        ("2:151:15",[(2,"bil"),(0,"mi"),(2,"yor"),("context"," "),(1,"olduğunuz")],["2:151:17","2:151:15"]),
        ("21:103:9",[(1,"size"),("context"," "),(2,"va'dedil"),(0,"en")],["21:103:9","21:103:11"]),
        ("17:1:9",[(1,"Mescid-i"),("context"," "),(2,"Aksa"),(0,"'ya")],["17:1:9","17:1:11"]),
    ]:
        indexed_group(first,segments,origins,"Explicit multi-entry decomposition keeps the actual clause, nominal, and case contributions at distinct source positions.")

    pair("2:48:4",[(1,"yarar sağla"),(0,"maz")],
         "Replace inherited cezalandırılmaz ('is not punished') with yarar sağlamaz for 'does not avail'. This repairs lexical meaning and voice, not just alignment. Selected source: QAC 2:48.","lexical_meaning_repair",revised=True)
    pair("6:48:2",[(1,"biz gönder"),(0,"me"),(1,"yiz")],
         "Repair malformed gönderimeyi to the finite negative predicate göndermeyiz. The following exception supplies the restrictive construction.","malformed_predicate_repair",revised=True)
    pair("5:63:6",[(1,"onların sözleri"),(0,"ni")],
         "Correct inherited onlarıv to onların while restoring the displaced lexical phrase to 'their saying'.","spelling_and_alignment",revised=True)

    for first,segments,origins,reason in [
        ("16:102:3",[(0,"Ruh"),("context","u'l-"),(1,"Kudüs")],["16:102:4"],"Restore the corrupted Holy Spirit compound as Ruhu'l-Kudüs. Arabic ruh and al-qudus occupy separate source positions; no interpretation identifying a particular being is added."),
        ("18:94:2",[(0,"ey Zül"),(1,"karneyn")],["18:94:3"],"Complete the vocative compound name Zülkarneyn and contextualize its two source components."),
        ("30:54:14",[(2,"kuvvet"),(0,"ten"),("context"," "),(1,"sonra")],["30:54:14"],"Supply the absent strength noun and attach the already-indicated -ten instead of leaving it isolated."),
        ("10:3:21",[(2,"O'nun izni"),(0,"nden"),("context"," "),(1,"sonra")],["10:3:21"],"Complete the permission-after construction; the baseline stored only O'nun izni at the earlier temporal key."),
        ("27:54:5",[("context","o "),(1,"aşırı kötülüğü"),(0," mü yapıyorsunuz"),("context","?")],["27:54:5"],"Restore the immorality noun and separate the question particle from it; otherwise preserve the wording."),
        ("34:8:6",[(0,"kendisinde "),(1,"delilik"),(0," mi var"),("context","?")],["34:8:6"],"Supply the absent madness noun in the existential question and remove the placeholder hyphen."),
        ("42:10:4",[("context","herhangi bir "),(1,"şey")],["42:10:4"],"Supply the absent şey in the existing indefinite phrase; the source relation has no separate overt surface here."),
    ]:
        indexed_group(first,segments,origins,reason,"lexical_or_compound_repair",revised=True)

    from remaining_final_cases import apply_final_cases
    apply_final_cases(en,tr,pair,indexed_group,add,at,used,groups)
