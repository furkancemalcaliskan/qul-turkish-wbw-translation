# Türkçe kelime kelime Kur’an çevirisi / Turkish Quran word-by-word translation

[Türkçe](#türkçe) · [English](#english)

## Türkçe

Bu bağımsız çalışma, [Tarteel AI Quranic Universal Library (QUL)](https://qul.tarteel.ai/) üzerindeki [Türkçe kelime kelime çevirinin (#99)](https://qul.tarteel.ai/resources/translation/99/docs) eksik ve hatalı karşılıklarını inceleyip düzeltmeyi amaçlar. Asıl hedef, tamamlanan düzeltmeleri QUL’e katkı olarak sunmak ve geliştiricilerin güncel, incelenmiş verilere ulaşmasına yardımcı olmaktır. Bu repo süreci şeffaf tutar; QUL tarafından onaylanmış veya yayımlanmış bir sürüm değildir.

**İlk şüpheli kayıt listesinin incelemesi tamamlandı; release henüz hazırlanmadı.** Listedeki **831 kaydın tamamı** Arapça kaynak ve İngilizce referansla değerlendirildi; bu listede bekleyen kayıt kalmadı. **487 kayıt**, düzeltme içeren incelemelerle; **344 kayıt**, karşılığı gerekçeyle korunarak kapatıldı. Bunlar hata sayısı değildir: bir karar komşu kelimeleri de kapsayabilir. Bu çalışma, 83.665 karşılığın her biri için bağımsız uzman onayı anlamına gelmez.

### Kaynaklar ve yapılanlar

`resources/` altındaki orijinal İngilizce/Türkçe JSON ve SQLite dosyaları ile QPC Hafs Arapça kelime kaynağı QUL’den alınmıştır. QUL burada kaynak sağlayıcısıdır; bütün çevirilerin yazarlığı veya telif sahipliği Tarteel AI’ye atfedilmez. Altı orijinal dosya değiştirilmez; [SHA-256 manifesti](reports/resource-integrity.json) ile doğrulanır.

- Türkçe, İngilizce referansın sırası ve biçimiyle hizalandı. Sıralama aşamasında mevcut key/value çiftleri değiştirilmedi.
- Eksik ayet numarası ve kelime/ifade anahtarları tamamlandı; Türkçe eklerin kaynak kelimelerle ilişkisi görünür kılındı.
- Yazım/gramer turunda **1.162 değer** düzeltildi. Anlam incelemeleri, gösterim temizliği ve ek yazım/gramer kontrollerinden sonra, `661144b` yazım/gramer commit’ine göre **1.262 ayette 2.629 farklı değer** değişti. Bunlar bağımsız hata sayıları değildir; aşama toplamları doğrudan birbirine eklenmez.
- Şüpheli anlamlar, Arapça kelime ve ayet bağlamı ile İngilizce karşılık birlikte okunarak değerlendirildi. Birden fazla yorumun mümkün olduğu yerlerde seçilen okuma ve sınırı kaydedildi. Araç/AI desteği kullanıldı; bağımsız uzman onayı iddia edilmiyor.

Son ek turda 622 değerdeki köşeli parantezler kaldırıldı; bu turdaki toplam değişiklik, önceki son duruma göre 940 ayette 1.522 farklı değerdir. Bu toplam gösterim temizliği ve yazım/gramer düzeltmelerini birlikte içerir.

### Gösterim

```json
{
  "2:5:4": "(Rableri)nden",
  "2:5:5": "Rableri(nden)"
}
```

Parantez dışında ilgili kaynak kelimenin Türkçe katkısı, içinde ortak bağlam bulunur. İki görünüm aynı “Rablerinden” ifadesini açıklar; peş peşe birleştirilmez. Güncel Türkçe değerlerde köşeli parantez kullanılmaz. Eski açıklamaların işaretleri kaldırıldı; bozuk birleşim oluşturan yerlerde kelime sınırları ve yinelenen açıklamalar ayrıca incelendi. Yuvarlak parantezler ortak anlamın/bağlamın gösterimi için korunur; ayet numaraları değişmez. Eşleme her zaman bire bir morfem eşliği değildir: Türkçe fiilin istediği hâl veya cümle yapısı esas alınır. Tamamen parantezli bir değer, kendiliğinden doğru sayılmaz; ayrı bir yüzey karşılığı bulunmadığı kabul ediliyorsa gerekçesi inceleme kaydında tutulur.

### Şeffaflık ve çıktı

Raporlar dört dosyada tutulur: [özet](reports/README.md), [inceleme kaydı](reports/review-state.json), [doğrulamalar](reports/validation.json) ve [kaynak hash’leri](reports/resource-integrity.json). Son değişikliklerin önce/sonra değerleri, kaynakları, gerekçeleri ve bekleyen kayıtlar korunur. Geçmiş raporlar Git geçmişindedir; [süreç özeti](PROCESS.md) ilgili commit’leri gösterir.

İnceleme bitince root Türkçe JSON minify edilecek; kaynak Türkçe DB’nin **root’a kopyası** bu JSON ile eşleştirilecek. QUL şeması korunacak. Root İngilizce dosyası son aşamada kaldırılacak; `resources/` orijinalleri kalacak. Nihai release ve QUL’e yükleme henüz yapılmadı. Ayrıntılar: [kaynak/release politikası](RESOURCE_POLICY.md), [QUL katkı yolu](QUL_CONTRIBUTION.md).

### Lisans bilgisi

[Kaynak #99’un lisans sayfası](https://qul.tarteel.ai/resources/translation/99/licence), telif bilgisinin bulunmadığını belirtiyor. Bu belirsizliği burada da kaydediyoruz. Kaynak belirtmek, dosyaların lisanssız veya kamu malı olduğu anlamına gelmez; orijinal verilere kendi adımıza bir lisans atamıyoruz.

## English

This independent project reviews, completes, and corrects the [Turkish word-by-word translation (#99)](https://qul.tarteel.ai/resources/translation/99/docs) distributed by [Tarteel AI’s Quranic Universal Library (QUL)](https://qul.tarteel.ai/). The intended destination is a contribution to QUL so developers can access reviewed, updated data. This repository provides transparency; it is not an approved or published QUL release.

**The initial flagged-record review is complete; release packaging is pending.** All **831 records** were assessed against Arabic and the English reference; none remains pending in that list. **487 records** were closed through reviews involving changes, and **344** through reasoned retention. These are not error counts: a decision may include adjacent words. This is not independent expert certification of every one of the 83,665 translations.

### Sources and changes

The original English/Turkish JSON and SQLite files and QPC Hafs Arabic word resource under `resources/` were obtained from QUL. This credits QUL as provider without attributing all translation authorship or copyright ownership to Tarteel AI. All six originals remain untouched and are verified against the [SHA-256 manifest](reports/resource-integrity.json).

- Turkish was reordered/formatted against English without changing existing pairs during that stage.
- Missing ayah-number and word/phrase keys were completed, with contextual displays for Turkish suffixes and combined expressions.
- The spelling/grammar stage corrected **1,162 values**. After semantic review, notation cleanup and further spelling/grammar checks, **2,629 distinct values across 1,262 ayahs** differ from spelling/grammar commit `661144b`. These are not independent error counts; stage totals must not simply be added together.
- Uncertain meanings were assessed against original Arabic words and ayah context alongside English. Where multiple readings are possible, the chosen reading and its limits are recorded. Tools/AI assisted the work; no independent expert endorsement is claimed.

The subsequent follow-up removed square delimiters from 622 values. Relative to the previous completed review, this follow-up changes 1,522 distinct values in 940 ayahs, including both notation cleanup and spelling/grammar corrections.

### Notation

In the example above, `(Rableri)nden` highlights the ablative contribution and `Rableri(nden)` the noun context. Both expose the same expression; do not concatenate the views. Outside parentheses is the selected contribution, inside is context. Current Turkish values contain no square brackets. Their old contents were initially preserved, then malformed joins and duplicate lexical explanations were reviewed individually. Round parentheses remain the shared-expression/context notation; ayah-number markers are unchanged. Allocation is functional rather than always morpheme-for-morpheme: Turkish verb valency and clause structure may determine the case or form. A fully parenthesized value is not automatically correct; an accepted zero surface needs its own recorded rationale.

### Transparency and output

Four reports hold the [summary](reports/README.md), [review state](reports/review-state.json), [validation results](reports/validation.json), and [source hashes](reports/resource-integrity.json). Current before/after changes, evidence, reasons, and pending records remain available. Earlier reports are in Git history; [PROCESS.md](PROCESS.md) identifies the relevant commits.

After review, the root Turkish JSON will be minified and a **root copy** of the original Turkish DB updated to match it, preserving QUL's schema. The root English JSON will be removed at the final stage; original resources remain. Final packaging and QUL submission have not occurred. See the [resource/release policy](RESOURCE_POLICY.md) and [QUL contribution route](QUL_CONTRIBUTION.md).

### Licence information

The [resource #99 licence page](https://qul.tarteel.ai/resources/translation/99/licence) states that copyright information is unavailable. We record that uncertainty here. Attribution does not establish that the files are unlicensed or public domain; we do not assign our own licence to the downloaded originals.

## Kontrol / Verification

Python 3.10+ and Git are required; the maintained tools use the Python standard library. Run from the repository root. Git history is needed to reconstruct the review baseline.

```powershell
python scripts/audit_resources.py
python scripts/audit_missing.py
python scripts/semantic_review.py
python scripts/audit_turkish_spelling.py
python scripts/read_arabic_context.py 2:5
```

Kontroller kaynak/veri bütünlüğünü ve kaydedilmiş değişiklikleri doğrular; dilbilimsel doğruluk onayı değildir. / Checks verify integrity and recorded changes, not linguistic correctness.
