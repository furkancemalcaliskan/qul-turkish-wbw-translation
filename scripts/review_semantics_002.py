"""Record Arabic-led decisions for flagged constructions in al-Baqarah."""
import argparse
import re

from alignment_common import render
from audit_resources import RESOURCES, read
from report_store import ROOT, STATE, load, save
from semantic_review import digest, encoded, replay, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    state = load(STATE)
    name = "semantic-review-002"
    if name in state["batches"]:
        validate()
        return
    before = replay(state)
    assert (ROOT / "turkish-wbw-translation.json").read_bytes() == encoded(before)
    en = read(RESOURCES / "english/english-wbw-translation.json")
    ar = read(RESOURCES / "arabic/qpc-hafs-word-by-word.json")
    groups, decisions, reviewed = [], [], set()

    def change(ayah, identifier, values, reason):
        values = {f"{ayah}:{word}": value for word, value in values.items() if before[f"{ayah}:{word}"] != value}
        if not values:
            return
        assert not reviewed.intersection(values)
        reviewed.update(values)
        groups.append({"id": ayah + "-" + identifier, "members": list(values),
                       "before": {key: before[key] for key in values}, "after": values,
                       "arabic": {key: ar[key]["text"] for key in values},
                       "english": {key: en[key] for key in values}, "reason": reason,
                       "source_role_note": "Displays were individually assigned after reading the recorded complete Arabic/English ayah. Parentheses retain context; square brackets mark an explanatory supplement. See the group reason for functional rather than literal morpheme mapping."})

    def phrase(ayah, identifier, pieces, reason):
        parts = [{"text": text, "role": f"{ayah}:{word}" if word else "context"} for text, word in pieces]
        members = list(dict.fromkeys(part["role"] for part in parts if part["role"] != "context"))
        values = {key: render(parts, key) for key in members}
        change(ayah, identifier, {int(key.split(":")[-1]): value for key, value in values.items()}, reason)
        if groups and groups[-1]["id"] == ayah + "-" + identifier:
            groups[-1].update(parts=parts, shared_expression="".join(part["text"] for part in parts))

    def decide(ayah, reason, retained=False):
        keys = [entry["key"] for entry in state["queue"] if entry["key"].rsplit(":", 1)[0] == ayah and entry["status"] == "requires_semantic_review"]
        assert keys, ayah
        decisions.append({"ayah": ayah, "status": "retained" if retained else "revised",
                          "resolved_semantic_keys": keys, "reason": reason,
                          "evidence": "Complete original Arabic, supplied English and pre-batch Turkish context stored in original_contexts; assessment applies to the named flags and recorded changes, not every lexical choice in the ayah."})

    phrase("2:23", "revealed-without-extra-addressee", [("indir", 6), ("diğ", 5), ("imiz", 6), ("den", 5)],
           "Nazzalna supplies we revealed; the recipient belongs to ala abdina. Remove the inherited sana, which adds an inconsistent second-person recipient before Our servant.")
    phrase("2:23", "other-than-Allah", [("Allah", 17), ("'tan", 15), (" ", 0), ("başka", 16)],
           "Min duni Allahi is Allah'tan başka. The ablative belongs on Allah, not on başka; başkadan did not express this construction correctly.")
    change("2:23", "conjunction", {1: "ve eğer"}, "Wa-in includes and plus the conditional.")
    decide("2:23", "Retain context-only min before mithlihi: its comparison/partitive relation is naturally included in onun gibi. No artificial ablative is added there. Correct the separate addressee and min duni construction in this ayah.")
    change("2:36", "dwelling-noun", {16: "bir yerleşme yeri"}, "Mustaqarr is a place/state of settlement in a nominal clause, not the bare infinitive kalmak. Here use the dwelling-place reading supported by the English reference.")
    phrase("2:36", "endpoint", [("belirli bir süre", 19), ("ye kadar", 18)], "Ila marks an endpoint: belirli bir süreye kadar. A bare duration omitted the until relation.")
    decide("2:36", "Restore the endpoint contribution of ila and the nominal dwelling expression; both local readings are supported by the Arabic clause and English reference.")
    phrase("2:48", "on-behalf-of", [("bir kimse", 7), (" adına", 6)], "An nafsin is on behalf of another soul, not from someone's sin. Remove the unsupported günahından gloss and represent the vicarious relation as adına.")
    phrase("2:48", "acceptance-negation", [("ve ", 9), ("kabul edil", 10), ("mez", 9)], "Wa-la supplies both conjunction and negation; yuqbalu supplies passive acceptance. Preserve both contributions.")
    phrase("2:48", "help-negation", [("ve ", 17), ("onlar", 18), (" ", 0), ("yardım gör", 19), ("mez", 17), ("ler", 19)], "The final clause negates their being helped. Yardım görmezler expresses passive receipt of help with plural agreement, avoiding the inherited dangling hiçbir yardım.")
    decide("2:48", "Retain yarar sağlamaz for la tajzi, a valid contextual rendering of not availing. Correct the adjacent on-behalf-of relation and final negated help construction.")
    phrase("2:74", "partitive-stones", [("taşlar", 14), ("dan", 13)], "Min al-hijarati selects among stones. Taşlardan explicitly exposes that relation without the inherited context-only öyle taş.")
    decide("2:74", "Expose the partitive min as the Turkish ablative in taşlardan; the following lama clause supplies the existence/relative sense.")
    phrase("2:78", "negative-exception", [("ve ", 8), ("onlar", 9), (" ", 0), ("zannet", 11), ("mek", 0), ("ten başka", 10), (" ", 0), ("bir şey yap", 0), ("maz", 8), ("lar", 11)], "Wa-in hum illa yazunnuna is negative restriction: they do nothing but conjecture. Use zannetmekten başka bir şey yapmazlar, exposing wa-in as conjunction/negation and illa as the exception. Bir şey yap is a Turkish support expression, not an additional Arabic word.")
    decide("2:78", "Replace the context-only negative with an explicit negative-exception construction; retain the inherited conjecture sense of yazunnuna.")
    change("2:85", "demonstrative", {3: "işte bunlarsınız"}, "Haulai is an overt proximal plural demonstrative; a context-only copy of öldürüyorsunuz omitted it. İşte bunlarsınız accommodates its predicative connection with antum.")
    decide("2:85", "Restore the overt demonstrative rather than treating haulai as an invisible relative pronoun.")
    decide("2:88", "In faqalilan ma yuminun, ma can function as reinforcement of the paucity expression rather than a separate object meaning what. Retain the contextual display alongside artık çok az / inanırlar; do not insert a new object or negate the verb. This decision adopts the reinforcing analysis, without asserting all traditional analyses are identical.", True)
    for ayah in ["2:89", "2:91", "2:108"]:
        decide(ayah, "Read min qabl in its full ayah. Turkish daha önce expresses the anterior time relation without a separate pronounced case suffix for min. Retain the complementary context-only display; adding -den to önce would be ungrammatical.", True)
    decide("2:96", "Retain ve ortak koşan kimselerden: min has comparative force under ahrasa, and the relative/plural phrase is assigned to alladhina/ashraku. The omitted repeated comparative predicate is recoverable from ahrasa; do not translate this min as physical origin.", True)
    phrase("2:125", "recipient", [("İbrahim", 14), ("'e", 13)], "Ila marks the recipient of the injunction. Expose the dative rather than retaining it wholly on the name.")
    change("2:125", "dual-injunction", {16: "[şöyle:]", 17: "ikiniz temizleyin", 18: "evimi"}, "An introduces the content of the injunction, followed by the dual imperative tahhira. Render an as an explanatory content introducer and restore a dual command; temizlemesini incorrectly presents a singular nominalized complement. Evimi does not take a proper-name apostrophe.")
    decide("2:125", "Expose ila as a recipient suffix. The neighboring an/tahhira clause is an explanatory introduction plus dual imperative, not a third-person singular cleaning nominal.")
    phrase("2:143", "past-weight", [("ağır", 30), (" ", 0), ("idi", 29)], "Kanat is past copular support for lakabiratan. Restore ağır idi rather than copying the present ağır gelir to the auxiliary key. Existing elbette conveys emphasis in the preceding entry.")
    phrase("2:143", "never-waste", [("ve ", 36), ("zayi edecek", 39), (" ", 0), ("değil", 36), ("di", 37)], "Wa-ma kana ... li-yudia denies that Allah would let faith go to waste. Değildi exposes the past copular contribution; the construction does not describe an ongoing loss. Wa-ma supplies the conjunction as well as negation.")
    change("2:143", "singular-address", {16: "(ol)duğ(un)", 17: "ol(duğ)un"}, "Kunta is second-person singular. Do not turn its relative phrase into second-person plural olduğunuzu; the object governed by jaalna is already al-qiblata.")
    decide("2:143", "Restore the two kana constructions as past copular contributions and repair singular kunta. The second construction denies divine wasting of faith; it is not a stand-alone prediction from English will.")
    phrase("2:145", "surely-among", [("elbette ", 31), ("zalimler", 32), ("den", 31), (" [olursun]", 0)], "La-mina supplies emphasis plus membership. Expose elbette and the ablative on zalimler; the conditional copula remains an explanatory supplement.")
    phrase("2:145", "after-knowledge", [("sana gelen", 26), (" ", 0), ("şey", 25), ("den", 23), (" ", 0), ("sonra", 24)], "Min badi ma jaaka is after what came to you. Put the ablative on the nominalized object şey, not on sonra; the inherited sonraden was malformed and displaced the case marker.")
    decide("2:145", "Expose emphatic membership in la-mina and correct the adjacent after construction. The conditional prediction remains bracketed as supplied context.")
    phrase("2:164", "relative-rainfall", [("ve ", 17), ("indir", 18), ("diğ", 17), ("i", 18)], "Wa-ma anzala is and what He sent down. Restore the conjunction and Turkish nominalizing relative ending instead of an undifferentiated indirip.")
    change("2:164", "sky-earth-locations", {39: "gök", 40: "ve yer"}, "Al-samai means sky and wal-ardi and earth. Their inherited Turkish counterparts were reversed; preserve the source locations even though the order yer ve gök is also natural Turkish.")
    decide("2:164", "Restore the relative contribution in wa-ma anzala. Retain explanatory min before water without a forced ablative: it identifies the substance sent down. Correct the independent reversed sky/earth entries.")
    phrase("2:167", "wish-complement", [("bizim için", 6), (" [mümkün olsaydı]", 5)], "Anna introduces the wished-for state after law. The Turkish supplied predicate mümkün olsaydı carries that complement function; keep it visibly explanatory, with the possession/benefit phrase at lana.")
    decide("2:167", "Identify the complement contribution in the explicit explanatory predicate rather than treating all of lana's phrase as the contribution of anna.")
    phrase("2:177", "despite-love", [("sevme", 22), ("sine rağmen", 21)], "Ala hubbihi is read here as despite love for the wealth, following the supplied English reference. Restore the concessive relation omitted by the inherited bare sevdiği. This records the selected interpretation, not a denial of the attested love-of-God interpretation of the pronoun.")
    change("2:177", "freeing-slaves", {30: "ve (köleleri özgürleştirmek) için", 31: "(ve) köleleri özgürleştirmek (için)"}, "Wa-fi al-riqab concerns freeing people from bondage, not merely giving wealth to slaves. Turkish için expresses the purpose of this spending category; it is a contextual construction, not a universal equivalent of fi.")
    decide("2:177", "Make the selected concessive reading of ala hubbihi explicit and clarify the freeing-from-bondage spending category. The pronoun interpretation is recorded as a choice.")
    phrase("2:185", "guidance-about", [("hidayet", 11), ("e dair", 10)], "Min al-huda after bayyinatin identifies what the proofs concern. Hidayete dair exposes that explanatory relation; no origin or spatial removal is intended.")
    change("2:185", "proofs-and-criterion", {9: "ve açık deliller", 12: "ve doğruyu yanlıştan ayırmaya dair"}, "Bayyinat is plural clear proofs, not a dangling adjective açıklayıcı. Wal-furqan shares the explanatory relation under min; render criterion contextually as distinguishing right from wrong.")
    decide("2:185", "Read min as explanatory in clear proofs concerning guidance and criterion; expose the relation in Turkish rather than inventing an ablative.")
    phrase("2:198", "bounty-source", [("Rabbiniz", 8), ("den", 7)], "Min rabbikum identifies the source of bounty. Use Rabbinizden rather than a genitive-only phrase; adjust the associated bounty noun to avoid two incompatible constructions.")
    change("2:198", "bounty-object", {6: "bir lütuf"}, "Fadlan is indefinite bounty, not an independently possessed lütfunu after the restored source phrase Rabbinizden.")
    decide("2:198", "Restore the source relation explicitly as Rabbinizden bir lütuf; retain the separate earlier-than guidance expression.")
    change("2:210", "exception", {3: "(gelmesinden) başka", 4: "(gel)me(sinden)", 5: "gel(me)sinden"}, "Hal ... illa restricts what is awaited: anything other than the coming. Make illa overt with başka and use the ablative nominal complement required by that Turkish construction.")
    phrase("2:210", "return-to-Allah", [("ve ", 14), ("Allah", 15), ("'a", 14)], "Wa-ila Allahi is and to Allah, not a stand-alone halbuki. Expose the conjunction and dative at their source word.")
    decide("2:210", "Restore the exception restriction and the final dative relation; these changes do not adjudicate the theological manner of the coming described in the ayah.")
    decide("2:217", "Retain ay hakkında: an introduces the subject being asked about, and al-shahr supplies month. It is not a locative or an ablative. The adjective haram remains its separate source entry.", True)
    phrase("2:228", "relative-obligation", [("[erkeklerin] kendileri üzerinde", 33), ("ki", 32)], "Alladhi supplies the nominal relative relation; alayhinna supplies on them. Expose -ki separately instead of a context-only copy of the complete phrase. The explanatory erkeklerin remains bracketed.")
    decide("2:228", "Expose the relative ending -ki without changing the reciprocal-rights interpretation in the surrounding clause.")
    phrase("2:230", "reciprocal-return", [("tekrar birbirlerine dön", 18), ("me", 17), ("lerinde", 18)], "An yatarajaa is a nominalized reciprocal return under no blame, not the separate following conditional in. Expose the nominalizer while preserving dual reference in birbirlerine.")
    decide("2:230", "Do not follow the isolated English if literally: Arabic an introduces a nominal complement; the true condition is the following in zanna.")
    phrase("2:236", "temporal-ma", [("onlara dokun", 9), ("ma", 8), ("dığınız", 9), (" sürece", 7)], "Ma lam tamassuhunna has temporal scope while/as long as you have not touched them; ma is not an object relative whom here. Restore the object them and expose temporal scope as sürece, negation as -ma and the inflected touching predicate at tamassuhunna.")
    phrase("2:236", "wealthy-obligation", [("eli geniş olan", 16), ("a düşer", 15)], "Ala expresses an obligation resting on the wealthy provider. A dative plus düşer makes that role visible in Turkish, instead of omitting it.")
    phrase("2:236", "poor-obligation", [("ve ", 18), ("eli dar olan", 19), ("a düşer", 18)], "Wa-ala similarly expresses the obligation of the person of restricted means, including the conjunction.")
    change("2:236", "plural-command", {14: "ve onları faydalandırın"}, "Wa-mattiuhunna is a second-person plural command; the inherited third-person faydalandırsın changed its addressee.")
    decide("2:236", "Read ma lam temporally, and make both ala obligation clauses visible. Restore the plural imperative in the intervening command. Temporal ma is represented with an explanatory supplement, not falsely labelled as a Turkish object-relative suffix.")
    phrase("2:240", "nominal-action", [("yap", 20), ("tık", 19), ("ların", 20), ("da", 18)], "Fi ma faalna concerns what the women do. Express the nominal-relative and locative roles as yaptıklarında rather than mapping fi to the context-only noun bir şey.")
    decide("2:240", "Expose fi and ma in the nominalized action. This local decision does not settle the jurisprudential relation between maintenance verses.")
    phrase("2:245", "demonstrative-person", [("o", 2), (" ", 0), ("kimse", 3)], "Dha contributes the demonstrative in man dha alladhi. Restore overt o at dha while alladhi carries the following person-relative expression; no invented suffix is needed.")
    decide("2:245", "Restore the demonstrative contribution in the interrogative rather than leaving dha wholly parenthesized.")
    change("2:246", "possibility-address", {24: "sizden beklenir (mi ki?)", 29: "(savaş)ma(manız)", 30: "savaş(ma)manız"}, "Asaytum addresses a plural audience with a possibility/expectation question. Restore that personal scope; alla tuqatilu is a negated nominal complement, not a conditional savaşmazsanız. Hal supplies the question at the preceding key.")
    change("2:246", "question-view", {23: "(sizden beklenir) mi (ki?)"}, "Hal supplies the interrogative particle for the restored plural possibility expression.")
    phrase("2:246", "why-for-us", [("ve ", 32), ("bizim için", 33), (" ", 0), ("ne [engel var]", 32)], "Wa-ma lana is and what is there for us, idiomatically why would we not fight. Retain the question as ne [engel var] with bracketed support, rather than reducing both source entries to bizler.")
    change("2:246", "fight-complement", {34: "(savaş)ma(mıza)", 35: "savaş(ma)mıza"}, "Under the restored ne engel var question, alla nuqatila is naturally expressed by the Turkish dative nominal complement savaşmamıza. Here -ma is nominalization, not an asserted Arabic affirmative replacement: the Arabic rhetorical negation is realized by the question about an obstacle.")
    decide("2:246", "Restore plural reference in asaytum, the nominal scope of alla tuqatilu, and the rhetorical question wa-ma lana. The second negative rhetorical complement is rendered idiomatically as an obstacle question, with that shift explicitly recorded.")
    decide("2:249", "Retain context-only min after kam: kam min fiatin is an exclamatory/quantificational many a company construction, naturally nice topluluk in Turkish. It is not a source or partitive requiring an invented -den.", True)
    change("2:254", "positive-temporal-nominal", {9: "(gel)me(den)", 10: "gel(me)den"}, "An yatiya before qabl is a positive arrival nominal. Turkish gelmeden önce expresses before coming; -me is the nominalizer and -den a temporal ablative, not an extra negation. Remove the ambiguous inherited gelmezden.")
    decide("2:254", "Retain the unpronounced separate min in min qabli; expose an as the Turkish nominalizer in gelmeden önce. Do not interpret the temporal -meden construction as negating the coming.")
    phrase("2:255", "interrogative-demonstrative", [("o", 21), (" [kimse]", 0), (" ki", 22)], "Dha supplies an interrogative demonstrative while alladhi introduces its relative description. Restore o and mark the nominal support kimse as explanatory rather than mapping both to ki.")
    decide("2:255", "Restore the demonstrative contribution; retain the following relative connector. This does not alter the permission limitation on intercession.")
    change("2:256", "pronoun-referent", {21: "onun [kulpun] için"}, "Laha refers to the firm handhold, not to Allah in the following wa-Allahu clause. Restore the feminine pronominal complement as onun, with kulpun bracketed to identify the antecedent.")
    decide("2:256", "Correct the displaced pronoun: laha belongs to the non-breaking handhold clause and must not copy Allah from the next word.")
    decide("2:266", "Retain context-only min in min kulli al-thamarat: the phrase identifies varieties of fruit, naturally her çeşit meyvesi with the inherited possession construction. A physical-origin ablative is not required.", True)
    change("2:267", "spending-circumstance", {18: "infak ederken", 19: "oysa (onu alacak) değilsiniz", 20: "(oysa) onu alacak (değilsiniz)"}, "Tunfiquna is a circumstantial spending predicate in the prohibition, not an independent report of present charity. Wa-lastum bi-akhidhihi denies willingness to take it, not physical inability; remove the inherited ability-negative -ama and retain the object pronoun.")
    change("2:267", "praise", {29: "övgüye layıktır"}, "Hamid is worthy of praise, not a passive past event övülmüştür. The adjective describes a quality.")
    decide("2:267", "Retain minhu as source from that property, the exception illa an tughmidu as göz yummanız dışında, fi-hi as onda, and the explicit knowledge/anna/Allah/Ghani sequence. Correct the circumstantial spending verb, the willingness negation and Hamid. Zengindir is retained here as freedom from need in its divine context; it is not interpreted as financial dependence.")
    phrase("2:282", "absence-copula", [("mevcut", 58), (" ", 0), ("değil", 57), ("se", 0)], "Fa-in lam yakuna combines conditionality, negation and being two men. Turkish mevcut değilse exposes existence separately from negation. The -se is shared conditional context supplied by the preceding fa-in, not falsely assigned as the lexical meaning of yakuna.")
    decide("2:282", "Express the existence/absence construction as mevcut değilse with separate predicate and negative views. The conditional particle is at 2:282:56 and is recorded in the complete context.")
    change("2:282", "scribe-command", {23: "yazsın"}, "Fa-l-yaktub instructs the scribe to write. Distinguish it from the immediately following wa-l-yumlil, which instructs the debtor to dictate. The inherited yazdırsın duplicated the second command.")

    after = dict(before)
    for group in groups:
        after.update(group["after"])
    ayahs = list(dict.fromkeys(decision["ayah"] for decision in decisions))
    contexts = {ayah: [{"location": key, "arabic": value["text"], "english": en.get(key), "turkish_before": before.get(key)}
                       for key, value in ar.items() if key.rsplit(":", 1)[0] == ayah] for ayah in ayahs}
    for records in contexts.values():
        records.sort(key=lambda record: int(record["location"].split(":")[-1]))
    batch = {"baseline": "semantic-review-001", "scope": "Flagged al-Baqarah constructions, with adjacent errors found while reading full ayahs; not a full-ayah certification.",
             "summary": {"changed_values": len(reviewed), "groups": len(groups), "reviewed_ayahs": len(ayahs),
                         "resolved_existing_semantic_flags": sum(len(d["resolved_semantic_keys"]) for d in decisions),
                         "turkish_before_sha256": digest(before), "turkish_after_sha256": digest(after)},
             "groups": groups, "decisions": decisions, "original_contexts": contexts,
             "comparison_sources": [{"ayah": "2:236", "url": "https://quran.com/al-baqarah/236", "use": "Published Arabic and Clear Quran translation confirm pre-consummation scope and means-based compensation."},
                                    {"ayah": "2:246", "url": "https://quran.com/al-baqarah/246", "use": "Published Arabic and Clear Quran translation confirm the possibility question and rhetorical objection."},
                                    {"ayah": "2:177", "url": "https://quran.com/al-baqarah/177", "use": "Published Arabic and Clear Quran translation support cherished wealth and freeing captives."}],
             "reference_limits": "Local immutable QUL Arabic and English were read directly. Attempts to retrieve QAC word-by-word pages returned different verse headings; those responses are not claimed as verification of these decisions. Contextual or disputed analyses are identified in individual reasons."}
    print(batch["summary"])
    if not args.apply:
        return
    state["batches"][name] = batch
    for decision in decisions:
        for entry in state["queue"]:
            if entry["key"] in decision["resolved_semantic_keys"]:
                entry["status"] = "reviewed_retained" if decision["status"] == "retained" else "reviewed_with_changes"
                entry["history"].append({"manifest": name + ".json", "reason": decision["reason"]})
                entry["turkish"] = after[entry["key"]]
                entry["currently_context_only"] = bool(re.fullmatch(r"\([^()]*\)", entry["turkish"]))
    for entry in state["queue"]:
        entry["turkish"] = after[entry["key"]]
    save(STATE, state)
    (ROOT / "turkish-wbw-translation.json").write_bytes(encoded(after))
    validate()


if __name__ == "__main__":
    main()
