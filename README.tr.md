# qul-turkish-wbw-translation

[Türkçe](README.tr.md) · [English](README.md)

Türkçe kelime kelime Kur’an çevirisi

Bu bağımsız çalışma, [Tarteel AI Quranic Universal Library (QUL)](https://qul.tarteel.ai/) üzerindeki [Türkçe kelime kelime çevirinin (#99)](https://qul.tarteel.ai/resources/translation/99/docs) eksik ve hatalı karşılıklarını inceleyip düzeltmeyi amaçlar. Asıl hedef, tamamlanan düzeltmeleri QUL’e katkı olarak sunmak ve geliştiricilerin güncel, incelenmiş verilere ulaşmasına yardımcı olmaktır. Bu repo süreci şeffaf tutar; QUL tarafından onaylanmış veya yayımlanmış bir sürüm değildir.

**İlk şüpheli kayıt listesinin incelemesi tamamlandı.** İlk sürüm: [v1.0.0](https://github.com/furkancemalcaliskan/qul-turkish-wbw-translation/releases/tag/v1.0.0). QUL’e aktarım henüz yapılmadı. Listedeki **831 kaydın tamamı** Arapça kaynak ve İngilizce referansla değerlendirildi; bu listede bekleyen kayıt kalmadı. **487 kayıt**, düzeltme içeren incelemelerle; **344 kayıt**, karşılığı gerekçeyle korunarak kapatıldı. Bunlar hata sayısı değildir: bir karar komşu kelimeleri de kapsayabilir. Bu çalışma, 83.665 karşılığın her biri için bağımsız uzman onayı anlamına gelmez.

## Katkı politikası

Dış katkılar şimdilik kapalıdır; çekme isteği (pull request) veya çeviri önerisi kabul edilmiyor. Bu herkese açık depo, süreci ve sürüm çıktılarını şeffaf biçimde gösterir. QUL’e yapılması planlanan katkı, bu repoya dış katkı kabul edilmesinden ayrı bir süreçtir. [Katkı politikası](CONTRIBUTING.md) · [v1.0.0 değişiklikleri](CHANGELOG.md).

## Kaynaklar ve yapılanlar

`resources/` altındaki orijinal İngilizce/Türkçe JSON ve SQLite dosyaları ile QPC Hafs Arapça kelime kaynağı QUL’den alınmıştır. QUL burada kaynak sağlayıcısıdır; bütün çevirilerin yazarlığı veya telif sahipliği Tarteel AI’ye atfedilmez. Altı orijinal dosya değiştirilmez; [SHA-256 manifesti](reports/resource-integrity.json) ile doğrulanır.

- Türkçe, İngilizce referansın sırası ve biçimiyle hizalandı. Sıralama aşamasında mevcut anahtar/değer çiftleri değiştirilmedi.
- Eksik ayet numarası ve kelime/ifade anahtarları tamamlandı; Türkçe eklerin kaynak kelimelerle ilişkisi görünür kılındı.
- Yazım/gramer turunda **1.162 değer** düzeltildi. Anlam incelemeleri, gösterim temizliği ve ek yazım/gramer kontrollerinden sonra, `661144b` yazım/gramer kaydına göre **1.262 ayette 2.629 farklı değer** değişti. Bunlar bağımsız hata sayıları değildir; aşama toplamları doğrudan birbirine eklenmez.
- Şüpheli anlamlar, Arapça kelime ve ayet bağlamı ile İngilizce karşılık birlikte okunarak değerlendirildi. Birden fazla yorumun mümkün olduğu yerlerde seçilen okuma ve sınırı kaydedildi. Araç/AI desteği kullanıldı; bağımsız uzman onayı iddia edilmiyor.

Son ek turda 622 değerdeki köşeli parantezler kaldırıldı; bu turdaki toplam değişiklik, önceki son duruma göre 940 ayette 1.522 farklı değerdir. Bu toplam gösterim temizliği ve yazım/gramer düzeltmelerini birlikte içerir.

## Gösterim

```json
{
  "2:5:4": "(Rableri)nden",
  "2:5:5": "Rableri(nden)"
}
```

Parantez dışında ilgili kaynak kelimenin Türkçe katkısı, içinde ortak bağlam bulunur. İki görünüm aynı “Rablerinden” ifadesini açıklar; peş peşe birleştirilmez. Güncel Türkçe değerlerde köşeli parantez kullanılmaz. Eski açıklamaların işaretleri kaldırıldı; bozuk birleşim oluşturan yerlerde kelime sınırları ve yinelenen açıklamalar ayrıca incelendi. Yuvarlak parantezler ortak anlamın/bağlamın gösterimi için korunur; ayet numaraları değişmez. Eşleme her zaman bire bir morfem eşliği değildir: Türkçe fiilin istediği hâl veya cümle yapısı esas alınır. Tamamen parantezli bir değer, kendiliğinden doğru sayılmaz; ayrı bir yüzey karşılığı bulunmadığı kabul ediliyorsa gerekçesi inceleme kaydında tutulur.

## Şeffaflık ve çıktı

Raporlar dört dosyada tutulur: [özet](reports/README.md), [inceleme kaydı](reports/review-state.json), [doğrulamalar](reports/validation.json) ve [kaynak SHA-256 değerleri](reports/resource-integrity.json). Son değişikliklerin önce/sonra değerleri, kaynakları, gerekçeleri ve bekleyen kayıtlar korunur. Geçmiş raporlar Git geçmişindedir; [süreç özeti](PROCESS.md) ilgili Git kayıtlarını gösterir.

Kök dizindeki Türkçe SQLite veritabanı, kaynak veritabanının kopyası üzerinden güncellendi ve 83.665 JSON kaydıyla eşleştirildi; QUL şeması korundu. Kök dizindeki Türkçe JSON, inceleme için girintili ve okunabilir biçimde korunur. İngilizce referans doğrudan `resources/english/` altından okunur; kök dizindeki kopyası kaldırıldı. Sıkıştırılmış JSON ve eşdeğer SQLite, `dist/` altında ayrı sürüm dosyaları olarak üretilir. Altı orijinal kaynak değişmez. GitHub sürüm dosyaları indirme içindir; bu yayın QUL tarafından onaylandığı anlamına gelmez. Ayrıntılar: [kaynak ve sürüm politikası](RESOURCE_POLICY.md), [QUL katkı yolu](QUL_CONTRIBUTION.md).

## Lisans bilgisi

[Kaynak #99’un lisans sayfası](https://qul.tarteel.ai/resources/translation/99/licence), telif bilgisinin bulunmadığını belirtiyor. Bu belirsizliği burada da kaydediyoruz. Kaynak belirtmek, dosyaların lisanssız veya kamu malı olduğu anlamına gelmez; orijinal verilere kendi adımıza bir lisans atamıyoruz.

## İndirme ve veri biçimi

Sıkıştırılmış JSON ve SQLite dosyalarını [v1.0.0 sürümünden](https://github.com/furkancemalcaliskan/qul-turkish-wbw-translation/releases/tag/v1.0.0) indirin. Kök dizindeki JSON okunabilir çalışma kopyasıdır; sürüm JSON’u biçimlendirme boşlukları olmadan UTF-8 olarak üretilir. İki dosyanın anahtar/değerleri aynıdır. `resources/turkish/` altındaki eski dosyalar tarihsel kaynaklardır; düzeltilmiş veri olarak kullanılmamalıdır.

SQLite tablo adı: `word_translation`.

| Sütun | Tür |
| --- | --- |
| `surah_number` | `INTEGER` |
| `ayah_number` | `INTEGER` |
| `word_number` | `TEXT` |
| `text` | `TEXT` |

Konumlar `sure:ayet:kelime` biçimindedir ve 1’den başlar. Mevcut kimlikleri yeniden numaralandırmayın. İndirme sonrasında `SHA256SUMS` değerlerini kontrol edin. `release-manifest.json` kaynak/çıktı SHA-256 değerlerini ve üretimin Git kaydını; `RELEASE_NOTES.md` sürüm kapsamını ve sınırlarını açıklar.

## Yerel doğrulama ve sürüm üretimi

Python 3.10+ ve tam Git geçmişi gereklidir. Araçlar yalnızca Python standart kütüphanesini kullanır. Komutları proje kökünde çalıştırın:

```powershell
python scripts/audit_resources.py
python scripts/audit_missing.py
python scripts/semantic_review.py
python scripts/audit_turkish_spelling.py
python -m unittest discover -s tests -v
python scripts/build_release.py --version v1.0.0
```

Çıktılar Git dışında tutulan `dist/` dizinine yazılır. Kök veritabanı eksikse veya JSON’dan farklıysa üretim durur. Yalnızca incelenmiş, bilinçli bir JSON değişikliğinden sonra kök veritabanını yenilemek için `python scripts/build_release.py --update-root-db` kullanılır. Orijinal kaynaklar değiştirilmez. Kontroller veri bütünlüğünü ve kayıtlı değişikliklerin tutarlılığını doğrular; bağımsız dilbilimsel onay değildir.

## Depo yönetimi

[Otomatik kontroller](.github/workflows/release.yml) dal güncellemelerinde ve elle başlatılan çalışmalarda paketi doğrular; gönderilen `v*` etiketleri için taslak sürüm oluşturur. Dosyalar doğrulama sonrasında yayımlanır. Dış katkılar kapalıyken çekme istekleri, sorun bildirimleri, tartışmalar ve viki kapalıdır.

Tüm dallarda yalnızca depo sahibi oluşturma/güncelleme yapabilir. Ayrı geçmiş koruması, istisna tanımadan zorla gönderimi ve dal silmeyi engeller. Yapılandırmalar [.github/rulesets/](.github/rulesets/) altında; katkı politikası [CONTRIBUTING.md](CONTRIBUTING.md) içindedir. Bu depo ayarları, QUL’e yayınlama sürecinden ayrıdır.
