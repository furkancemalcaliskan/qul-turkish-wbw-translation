"""Last multi-entry cases, with explicit provenance and semantic repairs."""
import json
import re
from alignment_common import ROOT, render

def apply_final_cases(en,tr,pair,indexed,add,at,used,groups):
    def direct(key,value,origin,reason):
        add([key],[{"text":value,"role":key}],origin,reason,"explicit_redistribution_or_translation",True,allow_existing=True)

    for key,segments in {
        "7:94:8":[(1,"sık"),(0,"ma"),(2,"dığ"),(1,"ımız")],
        "17:44:12":[(1,"tesbih et"),(0,"meyen")],
    }.items():
        pair(key,segments,"The inherited grammatical negative participates in an exceptive construction. Retain it at the exception source rather than attaching the negative meaning to the positive lexical verb.","exceptive_negative",normalization="grammatical_parentheses")

    # Reassemble existing temporal clause groups from their recorded roles.
    prior={}
    for filename in ["contextual-alignment-changes.json","continued-alignment-changes.json","broad-alignment-changes.json"]:
        for g in json.loads((ROOT/"reports"/filename).read_bytes())["groups"]:
            if all(tr.get(k)==v for k,v in g["after"].items()):
                for k in g["members"]:prior[k]=g
    for first,head in [("12:35:4","12:35:6"),("26:227:10","26:227:12"),("53:26:11","53:26:13"),("4:153:26","4:153:28")]:
        old=prior[head]
        phrase=old["shared_expression"]
        revised=first=="4:153:26"
        if revised:
            assert phrase.endswith("geldikken")
            phrase=phrase[:-3]+"ten"
        match=re.search(r"(?:nden|ndan|den|dan|ten|tan)$",phrase)
        assert match,(first,phrase)
        old_roles=[p["role"] for p in old["parts"] for _ in p["text"]]
        parts=[]
        for i,char in enumerate(phrase):
            role=first if i>=match.start() else old_roles[i]
            if parts and parts[-1]["role"]==role:parts[-1]["text"]+=char
            else:parts.append({"text":char,"role":role})
        post=tr[first].replace("(","[").replace(")","]")
        middle=at(first,1)
        parts += [{"text":" ","role":"context"},{"text":post,"role":middle}]
        add([first,middle]+old["members"],parts,[head,first],
            "Expand the already-recorded nominal clause to include the outer case and temporal postposition. In 4:153 only, correct inherited geldikken to geldikten; the outer ablative was misspelled, not absent in meaning.",
            "expanded_temporal_clause",revised,{head:"grammatical_parentheses",first:"explanatory_notes"})

    indexed("21:105:5",[(2,"Zikir"),(0,"'den"),("context"," [Tevrat'tan] "),(1,"sonra")],["21:105:7","21:105:5"])
    indexed("4:11:49",[(2,"vasiyyet"),(0,"ten"),("context"," [bu hükümler] "),(1,"sonra"),("context","dır")],["4:11:51","4:11:49"])
    indexed("4:12:43",[(2,"vasiyyet"),(0,"ten"),("context"," "),(1,"sonra")],["4:12:45","4:12:43"],
            "Add the missing ablative ending to the inherited will-after expression and expose its three source contributions.","case_completion",True)

    direct("4:24:34","onun üzerinde",["4:24:34"],"The agreement-reference bihi had incorrectly acquired the later temporal postposition. Restore its reference phrase; move sonra to the ba'd source group. Selected QAC 4:24.")
    indexed("4:24:35",[(2,"hakkın kesimi"),(0,"nden"),("context"," "),(1,"sonra")],["4:24:37","4:24:34"])

    # The kinship compound previously held the next temporal word. The two
    # operations are linked by origin key, without copying that word twice.
    add(["9:113:11","9:113:12"],[{"text":"akraba","role":"9:113:12"},{"text":" bile","role":"context"}],
        ["9:113:11"],"Restore the kinship noun to qurbā. The misplaced sonra is reused only in the following temporal group.","kinship_temporal_displacement",allow_existing=True)
    old=prior["9:113:15"]
    assert old["shared_expression"]=="belli olduktan"
    add(["9:113:13","9:113:14","9:113:15","9:113:16"],[
        {"text":"belli ol","role":"9:113:16"},{"text":"duk","role":"9:113:15"},
        {"text":"tan","role":"9:113:13"},{"text":" ","role":"context"},{"text":"sonra","role":"9:113:14"}],
        ["9:113:15","9:113:12"],"Reassemble the temporal clause from its earlier recorded expression and the displaced postposition.","kinship_temporal_displacement",normalization={"9:113:15":"grammatical_parentheses"})

    # Relative and possessive compound expressions.
    indexed("11:108:13",[(2,"Rabbinin"),("context"," "),(1,"dile"),(0,"dikleri")],["11:108:15","11:108:13"])
    indexed("12:83:11",[(2,"onların"),("context"," "),(1,"bana getirir")],["12:83:13","12:83:11"],
            "The reference repeats the whole English phrase at an/verb/bihim positions. Retain the Turkish complementizer as zero, put the verb at the middle key, and restore the pronoun reference to the last key; selected QAC 12:83.")
    indexed("12:76:14",[("context","yoksa "),(2,"al"),(0,"amaz"),("context"," "),(1,"idi")],["12:76:16","12:76:14"])
    indexed("28:23:20",[(1,"biz sulay"),(0,"ama"),(1,"yız")])
    indexed("10:13:11",[(0,"ve "),(2,"iman et"),(0,"me"),(2,"yecekleri"),("context"," için")],
            reason="Keep the negative and the future nominal predicate distinct. The source copula has no independently identified Turkish surface in this nominal paraphrase.")

    indexed("2:71:22",[(1,"az daha"),("context"," "),(2,"yap"),(0,"ma"),(2,"yacaklardı")],["2:71:22","2:71:24"])
    indexed("2:96:6",[(0,"ve "),(2,"ortak koş"),(1,"an kimseler"),(0,"den")],["2:96:6","2:96:8"],
            "Reassemble the participle and generic person noun in Turkish order, restore the source conjunction, and avoid duplicating plural marking on both parts.","comparative_relative",True)
    indexed("8:7:10",[(2,"kuvvet"),(0,"siz"),("context"," "),(1,"olanın"),("context"," hali")],["8:7:12","8:7:10"])
    indexed("22:38:4",[(1,"kimseler"),(0,"den")])
    indexed("28:49:4",[(2,"Allah"),("context"," "),(1,"katı"),(0,"ndan")],["28:49:6","28:49:4"])
    indexed("46:10:5",[(2,"Allah"),("context"," "),(1,"katı"),(0,"ndan")],["46:10:7","46:10:5"])
    indexed("42:3:5",[(2,"sen"),(1,"den"),("context"," "),(2,"önce"),(0,"kilere")])
    indexed("40:27:7",[(2,"kibirlilerin"),("context"," "),(1,"hepsi"),(0,"nden")],["40:27:9","40:27:7"])
    indexed("40:49:2",[(2,"ateş"),("context"," "),(1,"içinde"),(0,"kiler")],["40:49:4","40:49:2"])
    indexed("72:27:8",[(1,"ön"),(2,"ü"),(0,"ne")],reason="The inherited önüne was repeated at two source positions. Use one contextual location/possessive/case expression instead.")

    # Missing lexical predicates and visibly malformed source placeholders.
    direct("30:10:13","alay edenler",[],"Supply the missing mocking predicate. The separate pronoun phrase onlarla is already present and is retained.")
    indexed("7:132:4",[(0,"onunla"),("context"," "),(1,"bir")],["7:132:4"],
            "Move bir to the partitive/indefinite position and restore the absent object-reference phrase for therewith.","reference_phrase_completion",True)
    indexed("63:10:2",[(2,"size ver"),(1,"diğ"),(2,"imiz rızık"),(0,"tan")],["63:10:4"],
            "Remove the inherited literal 0 placeholder and expose the outer case and nominal clause ending already present on the following predicate.","placeholder_repair",True)
    indexed("39:43:2",[(3,"Allah"),(1,"'tan"),("context"," "),(2,"başka"),("context"," "),(0,"mı edindiler"),("context","?")],
            ["39:43:5","39:43:2"],"The preposition and postposition had been absorbed by the noun and question. Restore their source positions, separate the question particle, and correct its vowel harmony.","question_postposition_displacement",True)

    # The existing negative-purpose construction is faithfully paraphrased
    # by a Turkish negative imperative. Reorder its existing words, rather
    # than inventing a second negative that reverses the instruction.
    members=[f"4:135:{i}" for i in range(23,28)]
    parts=[{"text":"öyle ise ","role":members[0]},{"text":"keyfinize","role":members[2]},
           {"text":" ","role":"context"},{"text":"uyarak","role":members[1]},
           {"text":" ","role":"context"},{"text":"adaletten sap","role":members[4]},
           {"text":"ma","role":members[0]},{"text":"yın","role":members[4]}]
    add(members,parts,members[:-1],"Reorder the inherited imperative and its complements into a coherent Turkish instruction. The negative imperative carries the prohibition; lest has no independent surface in this paraphrase. Preserve polarity; compare Diyanet 4:135.","negative_purpose_redistribution",True)

    # The requested reference explicitly uses a kinship gloss. This repair
    # follows that reference without claiming to adjudicate all tafsir views.
    indexed("42:23:16",[(2,"yakınlar"),("context"," "),(1,"arasında"),("context"," "),(0,"sevgi")],
            ["42:23:16","42:23:17"],"Restore the love and relatives vocabulary specified by the English reference. Remove the inherited explanatory Allah'a gloss, which is not present in that reference. Selected comparison: Diyanet 42:23; this does not adjudicate all interpretations.","reference_kinship_gloss_repair",True)

    # Preserve explanatory Kâbe while distinguishing adjective, noun, copula.
    add(["22:33:9","22:33:10","22:33:11"],[{"text":"Eski","role":"22:33:11"},
        {"text":" ","role":"context"},{"text":"Ev","role":"22:33:10"},
        {"text":"'dir","role":"22:33:9"},{"text":" [Kâbe]","role":"context"}],
        ["22:33:9"],"The inherited adjective/noun expression was already displayed twice with contextual parentheses. Consolidate it into three views, retaining the explicit Kâbe explanation.","proper_noun_adjective",normalization="grammatical_parentheses")
    add(["24:31:50","24:31:51","24:31:52"],[{"text":"kadına ihtiyacı","role":"24:31:52"},
        {"text":" ","role":"context"},{"text":"bulun","role":"24:31:51"},{"text":"mayan","role":"24:31:50"}],
        ["24:31:51","24:31:50"],"The negative/non-possessing/desire construction is already expressed as a Turkish existential phrase. Keep its negative and possession markers distinct from the desire noun phrase.","negative_possession_phrase")

    # Complete the remaining group with an existing noun and explanatory note.
    indexed("7:31:5",[(1,"her"),("context"," "),(2,"mescid"),("context","[e gidişiniz]"),(0,"de")],
            ["7:31:5","7:31:7"],"Move the note boundary after the complete mescid stem while retaining every lexical letter, then expose the quantifier and final locative.","annotation_boundary_repair",True)
    indexed("15:19:8",[(1,"her"),("context"," "),(2,"şey"),(0,"den")],["15:19:8","15:19:10"],
            "Explicitly treat the inherited (den) as a grammatical ending, retaining the quantifier and noun.","grammatical_note_reassembly",True)
    indexed("31:17:15",[("context","yapılması gereken "),(1,"işler"),(0,"dendir")],["31:17:15","31:17:17"])
    indexed("3:186:22",[("context","yapmağa değer "),(1,"işler"),(0,"dendir")],["3:186:22","3:186:24"])
    indexed("12:68:7",[(2,"sava"),(0,"maz"),("context"," "),(1,"idi")],["12:68:9","12:68:7"],
            "The negative is on the avail predicate, while the inherited idi expresses the source copula. Keep those surfaces at distinct positions despite the abbreviated English 'it' gloss.")
    indexed("15:93:1",[(2,"yap"),(1,"tık"),(2,"ları"),("context"," "),(0,"şeylerden")],["15:93:3","15:93:1"])
    indexed("28:74:6",[("context","olduklarını "),(2,"san"),(1,"dığınız"),("context"," "),(0,"şeyler")],["28:74:6","28:74:8"],
            "Correct oduklarını to olduklarını and expose the relative head and past nominal predicate in the complete claim expression.","spelling_and_clause_repair",True)
    indexed("43:7:5",[(2,"onunla alay et"),(0,"me"),(1,"dikleri")],["43:7:7","43:7:5"],
            "Restore the omitted mockery noun alay and distinguish the exceptive negative from the past/nominal copula construction.","missing_mockery_predicate",True)

    # Finish the phrase chains whose case/negative was stored further away.
    indexed("5:52:2",[(2,"kalbleri"),(1,"nde"),("context"," "),(3,"hastalık"),
            ("context"," bulun"),(0,"anların")],["5:52:4","5:52:5","5:52:2"])
    indexed("62:6:10",[(2,"insanlar"),(0,"dan"),("context"," "),(1,"başka olarak")],["62:6:12","62:6:10"])
    indexed("12:111:2",[(2,"onların hikayeleri"),(1,"nde"),("context"," "),(0,"vardır")],["12:111:4","12:111:2"])
    indexed("28:43:5",[(3,"helak et"),(2,"tik"),(0,"ten"),("context"," "),(1,"sonra")],["28:43:7","28:43:5"])
    indexed("11:42:16",[(0,"ve "),(1,"ol"),(0,"ma")],["11:42:17"],
            "Negation was already attached to olma at the next key. Expose it at the missing negative/conjunction entry and restore its explicit conjunction.","negative_entry_completion",True)
    indexed("22:5:52",[(2,"bilgi sahibi olduk"),(0,"tan"),("context"," "),(1,"sonra")],["22:5:54","22:5:52"],
            "Replace the mismatched knowledge/while paraphrase with a coherent knowledge-after phrase, retaining the source temporal relation.","knowledge_temporal_repair",True)
    indexed("30:28:8",[(3,"sizin ellerinizde "),(2,"bulun"),(1,"anlar"),(0,"dan"),("context"," [köleler]")],
            ["30:28:11","30:28:9"],"Reassemble the duplicated contextual phrase, correct the possessive agreement sizin ellerinde to sizin ellerinizde, and distinguish possession, relative plural, and case.","possessive_agreement_repair",True)
    indexed("5:41:29",[(2,"yerlerine konulduk"),(0,"tan"),("context"," "),(1,"sonra")],["5:41:29","5:41:31"],
            "Remove unsupported bazısının and restore the min/ba'd/context sequence as a Turkish placement-after clause. This is an interpretive phrase repair following the reference's temporal gloss, and remains explicitly flagged for semantic review; compare Diyanet 5:41 for the contextual-placement sense.","context_placement_repair",True)

    # A right/way phrase had lost its lexical head entirely.
    indexed("4:84:3",[(1,"Allah"),("context","'ın "),(0,"yolu")],["4:84:3"],
            "Restore the missing way head and move Allah to the divine-name source position, completing the inherited 'the way of Allah' phrase.","lost_lexical_head",True)
    indexed("5:32:1",[(2,"işte bu "),(1,"sebep"),(0,"le")],["5:32:3","5:32:1"],
            "The reference's gloss 'time' corresponds here to Arabic ajl, a reason/cause idiom. Retain the existing Turkish reason word and expose min through the causal -le construction rather than inventing a time noun.","causal_source_idiom")
    indexed("10:37:7",[(2,"Allah"),(1,"'tan başkası"),("context"," "),(0,"tarafından")],
            ["10:37:9","10:37:7"],"Restore the complete other-than-Allah/by phrase. Remove the displaced independent copular assertion from Allah'tandır and retain its case in the comparative construction.","agent_comparative_repair",True)
    indexed("2:262:8",[(3,"verdikleri"),("context"," "),(2,"şeyleri"),("context"," "),
            (1,"ardından"),("context"," "),(4,"başa kak"),(0,"ma"),(4,"yan")],
            ["2:262:11","2:262:10","2:262:8","2:262:12"],
            "In the inherited Turkish paraphrase the following relation is adverbial (ardından), while the negative ending occurs on the reminders predicate. Reassemble the phrase so the displaced negative and follow entries share that existing material.","negative_reminder_chain")

    # Repair the contiguous shift at the end of 2:267. These linked operations
    # move each original phrase once; no existing lexical value is silently
    # duplicated into the missing keys.
    direct("2:267:17","ondan",["2:267:23"],"Restore the object-reference phrase minhu from its displaced later source position.")
    direct("2:267:18","sadaka veriyorsunuz",["2:267:17"],"Restore the spend predicate to tunfiquna and supply its finite form instead of leaving the displaced infinitival phrase.")
    add(["2:267:19","2:267:20"],[{"text":"kendinize al","role":"2:267:20"},
        {"text":"ama","role":"2:267:19"},{"text":"yacağınız","role":"2:267:20"}],
        ["2:267:18"],"Move the inherited negative taking expression to the actual negative and take positions.","contiguous_displacement")
    indexed("2:267:21",[(2,"göz yum"),(1,"ma"),(2,"nız"),("context"," "),(0,"dışında")],
            ["2:267:20","2:267:21"],"Rebuild the exception/subordinator/overlooking phrase as göz yummanız dışında, retaining the existing lexical root while correcting its source roles.","contiguous_displacement",True)
    for key,value,origin in [
        ("2:267:24","onda",[]),("2:267:25","ve bilin ki",["2:267:24"]),
        ("2:267:26","şüphesiz",["2:267:25"]),("2:267:27","Allah",["2:267:26"]),
        ("2:267:28","zengindir",["2:267:27"]),("2:267:29","övülmüştür",["2:267:28"]),
    ]:
        direct(key,value,origin,"Correct the contiguous one-position phrase shift at the end of 2:267. The location reference is newly supplied; the following lexical meanings are restored to their reference keys.")

    # Final local orthographic/role corrections discovered while reviewing
    # the explicit specifications. Keep them visible as revisions in the log.
    overrides={
        "15:11:6":([(1,"ol"),(0,"ma"),(1,"dıkları")],"The exception is expressed by the negative -ma; the copular predicate and its nominal ending belong to the following source entry."),
        "26:5:9":([(1,"ol"),(0,"ma"),(1,"dıkları")],"Expose the exceptive negative rather than incorrectly calling -dık the source but/except contribution."),
        "36:46:9":([(1,"ol"),(0,"ma"),(1,"dıkları")],"Expose the exceptive negative separately from the copular/nominal predicate."),
        "2:177:22":([(1,"sevdiği")],"The inherited adjectival love paraphrase has no separately identified in/spite-of marker; do not call its relative ending a preposition."),
        "76:8:4":([(1,"sevdikleri")],"The existing love participle is a paraphrase, with no independent overt in-spite-of surface in this local expression."),
        "2:246:24":([(1,"olur"),("context"," "),(0,"mu"),("context"," ki?")],"Separate the question particle and assign the hypothetical predicate to the appropriate source component."),
        "13:11:17":([(1,"bir millet")],"Correct the inherited spelling milet to millet while restoring the noun phrase."),
        "14:16:6":([("context","bir "),(1,"su")],"Remove the stranded final y from the malformed noun fragment bir suy; retain the complete water noun."),
    }
    for key,(segments,reason) in overrides.items():
        group=next(g for g in groups if key in g["members"])
        first=at(key,-1)
        parts=[{"text":text,"role":first if owner==0 else key if owner==1 else "context"} for owner,text in segments]
        group["parts"]=parts
        group["shared_expression"]="".join(p["text"] for p in parts)
        group["after"]={k:render(parts,k) for k in group["members"]}
        group["zero_surface_keys"]=[k for k in group["members"] if not any(p["role"]==k for p in parts)]
        group["reason"]+=" Final review: "+reason
        group["lexical_revision"]=group["lexical_revision"] or group["shared_expression"]!=tr[first].replace("(","[").replace(")","]")
