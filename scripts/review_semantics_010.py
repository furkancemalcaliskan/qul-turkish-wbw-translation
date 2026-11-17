"""Second reading: repair draft inflection and finish explicitly identified follow-ups."""
import argparse
from semantic_review import ReviewBatch,validate


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--apply",action="store_true");args=parser.parse_args()
    b=ReviewBatch("semantic-review-010","Second reading of the completed initial queue: correct newly drafted inflections, resolve named adjacent follow-ups and compare a limited lexical family. Earlier draft decisions remain in the chain.")
    if b.exists:validate();return
    def p(a,i,ps,r):b.phrase(a+"-"+i,[(t,f"{a}:{w}" if w else None) for t,w in ps],r)
    def c(a,i,vs,r):b.change(a+"-"+i,{f"{a}:{w}":t for w,t in vs.items()},r)
    def again(k,r):b.decide(k,r,reassessment=True)
    for ay,negative,copula,note in [("4:11",35,36,""),("4:12",7,8,""),("4:12",31,32,""),("4:176",22,23," [kız kardeşinin]")]:
        p(ay,"conditional-harmony-"+str(copula),[("mevcut",copula),(" ",0),("değil",negative),("se"+note,0)],"Second reading found an inflection error in the preceding draft: after değil the shared conditional ending must be -se, not -sa or a disconnected da. Preserve the existence predicate and negation; the condition comes from the preceding if frame, not yakun itself.")
        again(f"{ay}:{copula}","Correct the draft's conditional vowel harmony; keep the recorded functional allocation of existence and negation.")
    c("2:236","conditional-address",{5:"boşarsanız"},"In tallaqtum is a conditional divorce event. Turkish eğer requires the corresponding boşarsanız here, not an independent declarative boşarsınız; no marriage rule is changed.")
    c("4:24","beyond-possessor",{15:"bunların"},"With the recorded Turkish ötesinde olanlar relative, the enumerated items are a genitive possessor bunların. The inherited bunlardan belonged to a different bare ötesi frame and should not be mixed with the new locative relative.")
    p("4:98","coordinated-classes",[("erkekler",4),(", kadınlar",5),(" ve çocuklar",6),("dan",3)],"The shared min scopes over men, women and children. Turkish can place the shared case on the final coordinated noun: erkekler, kadınlar ve çocuklardan. This avoids leaving only the first noun inflected while later categories appear syntactically unrelated.")
    again("4:98:3","Refine the shared-case display over all three coordinated exempted classes, without narrowing any class to another.")
    for ay,relative,before,pronoun in [("5:46",8,9,10),("5:46",19,20,21),("5:48",6,7,8)]:
        p(ay,"preceding-scripture-"+str(relative),[("kendisin",pronoun),("den önce",before),("kini",relative)],"Finish the identified bayna yadayhi follow-up in scripture-confirmation clauses. The full idiom means what preceded it, not literal hands/between; expose the relative object, temporal relation and pronominal anchor while preserving explanatory min and the named scripture.")
    p("9:74","resentment-not-revenge",[("ve ",16),("yalnızca ",18),("hoşnutsuzluk duydular",17)],"Wa-ma naqamu illa expresses the sole ground of resentment. Naqamu does not require an attempted revenge action; replace öç almağa kalktılar with hoşnutsuzluk duydular while retaining the valid positive-only restriction frame.")
    again("9:74:16","Reassess the earlier restriction-only decision after completing its lexical follow-up: restore resentment, not attempted revenge, and expose the conjunction.")
    c("9:74","bounty-spelling",{23:"(lütfu)yla",24:"lütfu(yla)"},"Correct the common-noun possessive form lütfu while preserving the recorded instrumental bounty relation.")
    p("17:36","questioned-predicate",[("sorgulanacak",16),("tır",14)],"Mas'ulan is being asked/questioned. Use the explicit source predicate under the English assured-future reading, not only responsible; kana supplies Turkish assertive predication, with future time licensed by the accountability context.")
    c("17:36","unassigned-pronominal-reference",{15:"onun hakkında"},"Anhu says about it/him. Remove the inherited added action referent [yaptığı] and retain the generic source pronoun, without choosing uniquely between the traditional organ/person antecedent analyses.")
    again("17:36:14","Finish the accountability follow-up conservatively: restore questioning and retain an unexpanded pronoun rather than inventing a specific action antecedent.")
    p("17:69","destructive-wind",[("kırıp geçiren",10),(" ",0),("rüzgar",12)],"Qasifan supplies the destructive/shattering wind quality; al-rih is wind. Restore that adjective at qasif instead of assigning it to min and treating the first word as a separate extra storm noun.")
    c("17:69","wind-kind-min",{11:"(kırıp geçiren rüzgar)"},"Min al-rih identifies the destructive phenomenon as wind. It has no independent spoken suffix in the selected Turkish adjective-noun frame; keep this explicit contextual kind relation rather than invent a physical source.")
    again("17:69:12","Finish the neighboring qasif/min allocation follow-up while retaining the wind noun's actual meaning.")
    p("21:90","good-deed-compound",[("hayır [işleri]",13),("nde",12)],"Second reading found that hayır işleri is a Turkish noun compound: its locative is hayır işlerinde. Restore the possessive compound ending and the correct linking n before the locative, rather than hayır işlerde.")
    again("21:90:12","Correct the draft's compound/locative morphology while preserving good-deed scope.")
    c("24:58","circulating-persons",{37:"girip çıkarlar",38:"sizin [yanınıza]"},"Tawwafuna alaykum describes their circulating around you. Restore third-person plural circulating and the addressed plural complement; the subsequent ba'dukum ala ba'd is a separate mutual relation, not a reason to erase alaykum's you.")
    p("33:19","fainting-simile",[("kendisine ",13),("baygınlık gel",12),("en [kimse] gibi",11)],"Ka-alladhi yughsha alayhi describes the person overcome by faintness. Turkish kendisine baygınlık gelen kimse gibi restores the singular recipient, passive-experience idiom and relative likeness, rather than the inherited plural onların üstüne and detached baygınlığı noun.")
    p("34:21","single-indefinite",[("hiçbir ",5),("zorlayıcı gücü",6)],"Second reading removes the draft's duplicate indefinite bir in hiçbir zorlayıcı bir gücü. The indefinite determiner hiçbir already selects the noun phrase.")
    again("34:21:5","Correct the duplicate determiner while keeping unrestricted negative authority scope.")
    p("42:51","speech-without-extra-reciprocity",[("konuş",5),("ma",4),("sı",5)],"Yukallimahu states speaking to the person in the named communication modes. Remove the inherited supplied [karşılıklı], which unnecessarily asserted reciprocal conversation; retain the nominal speech content and the stated divine subject.")
    # Compare only the seven explicitly identified Throne clauses, not all uses of the root.
    for ay,verb,relation,throne in [("7:54",12,13,14),("10:3",12,13,14),("13:2",9,10,11),("20:5",4,2,3),("25:59",11,12,13),("32:4",12,13,14),("57:4",10,11,12)]:
        c(ay,"throne-istiwa-term",{verb:"istiva etmiştir" if ay=="20:5" else "istiva etti"},"For this explicitly identified istawa ala al-arsh clause, retain the established Turkish technical term istiva already present at 7:54, 13:2 and 32:4. Do not substitute the different verb kuşatmak, assert physical sitting, or put an alternative synonym inside alignment parentheses. This preserves the term without selecting a unique theological account of how it is understood; tree growth, human maturity and istawa ila contexts are not changed.")
        p(ay,"throne-complement",[("Arş",throne),("'a",relation)],"Within the selected Turkish istiva etmek frame, show the complement Arş'a with the dative contribution at ala. This is the phrase's Turkish case realization, not a universal dative definition of ala.")
    again("10:3:13","Reassess the earlier valency-only retention after the lexical comparison: replace kuşattı with the established technical istiva term and align its complement, without a new physical or doctrinal paraphrase.")
    c("60:6","hope-not-bare-desire",{8:"([kavuşmayı] umanlar)",9:"[kavuşmayı] umanlar",10:"Allah'a",11:"ve gününe"},"Finish the kana-yarju lexical comparison with 33:21: yarju is hope/expectation, not merely bare desire for an object. Preserve the inherited meeting-context interpretation explicitly bracketed and give its coordinated Allah/Last-Day complements the same dative case. Kana remains support in the nominal relative, not an extra finite past predicate.")
    again("60:6:8","Refine the earlier nominal-frame decision after the hope/desire comparison, preserving explicit limits on the supplied meeting interpretation.")
    # Every item below was read with its Arabic location; this is not a blind spelling replacement.
    for key,value in {
        "4:2:2":"yetimlere", "4:3:6":"yetimler", "4:6:2":"yetimleri", "4:8:6":"ve yetimler",
        "4:10:5":"yetimlerin", "4:36:11":"ve yetimlere", "4:127:14":"yetim", "4:127:30":"yetimlere karşı",
        "2:215:11":"ve yetimler", "93:9:2":"yetimi",
    }.items():
        b.change(key+"-orphan-term",{key:value},"The Arabic y-t-m orphan term is rendered consistently as yetim, already used elsewhere in the working data, rather than the potentially narrower maternal-orphan öksüz. Preserve the local number/case and conjunction. At 4:3 retain the generic plural: the gender-specific orphan-girl interpretation is not a lexical word in al-yatama and is not imposed as an unmarked suffix note.")
    p("2:220","about-orphans",[("yetimler",6),(" hakkında",5)],"An al-yatama gives the topic of asking, about orphans. Restore the clear Turkish hakkında frame and the same orphan term, rather than a possibly misleading source reading öksüzlerden.")
    b.extra_ayahs += ["93:2"]
    b.references=[{"ayah":"10:3","url":"https://quran.com/yunus/3","use":"Published Arabic istawa ala al-arsh and established-on-the-Throne translation; Turkish technical term preserves the phrase without expanding its theological manner."},
                  {"ayah":"93:2","url":"https://quran.com/ad-duhaa/2","use":"Published when-it-falls-still reading corroborates the retained sakinleştiğinde temporal interpretation from batch 009."}]
    b.follow_up=[{"status":"selected_reading_recorded", "locations":["10:3:12","20:5:4","25:59:11","57:4:10"],
                  "reason":"The technical istiva term is retained without a physical-sitting, encirclement or unique theological expansion. This is a documented conservative terminology choice, not independent expert endorsement."},
                 {"status":"selected_reading_recorded", "locations":["2:177:22","4:135:26","19:34:7","24:40:21","30:3:2","39:74:10","72:7:7","76:8:4"],
                  "reason":"The relevant batches record pronoun, syntax, metaphor, negated-nearness, partitive and lexical alternatives. The retained choices are not claims that every traditional interpretation is identical."}]
    b.finish(args.apply)


if __name__=="__main__":main()
