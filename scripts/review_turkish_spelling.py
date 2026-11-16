"""Review explicit orthographic candidates against the committed Turkish file."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
# Each replacement is a spelling candidate, never an English-to-Turkish lookup.
CANDIDATES = {
    "herşey": "her şey", "herşeyi": "her şeyi", "herşeyin": "her şeyin", "herşeye": "her şeye",
    "hiçbirşeyi": "hiçbir şeyi", "havyanlar": "hayvanlar", "yada": "ya da",
    "süphesiz": "şüphesiz", "inanmışşızdır": "inanmışızdır",
    "Eçisini": "Elçisini", "aderlerken": "ederlerken",
    "aidolduğu": "ait olduğu", "alakoymak": "alıkoymak", "aldatmakdan": "aldatmaktan",
    "aldattıp": "aldatıp", "alehylerine": "aleyhlerine", "anlanın": "anların",
    "anlattıkarında": "anlattıklarında", "arasıda": "arasında", "artk": "artık",
    "ayerleri": "ayetleri", "açıklıyan": "açıklayan", "aşağılatıcı": "aşağılayıcı",
    "bağışlayadır": "bağışlayandır", "bağışlayındır": "bağışlayandır",
    "bedbahtttır": "bedbahttır", "belkide": "belki de", "berebar": "beraber", "bereber": "beraber",
    "biraraya": "bir araya", "birkısmı": "bir kısmı", "birtek": "bir tek",
    "bozguncuğu": "bozgunculuğu", "bulunaların": "bulunanların", "böyece": "böylece",
    "bıracacak": "bırakacak", "bşüphesiz": "şüphesiz", "dedildikleri": "denildikleri",
    "dedilenden": "denilenden", "dedilmiş": "denilmiş",
    "demekki": "demek ki", "dimseye": "kimseye", "doğrsu": "doğrusu",
    "düzetmeye": "düzeltmeye", "düştünüğünüz": "düştüğünüz", "dışıda": "dışında",
    "elbete": "elbette", "elbett": "elbette", "elbetteki": "elbette ki",
    "emrerdildi": "emredildi", "erişemeycekler": "erişemeyecekler",
    "etttiğinde": "ettiğinde", "getiririrz": "getiririz", "girmdiler": "girmediler",
    "guruplar": "gruplar", "guruptur": "gruptur", "gödün": "gördün",
    "gösterişce": "gösterişçe", "herhangibir": "herhangi bir", "hihayeti": "hidayeti",
    "hikmetsahibidir": "hikmet sahibidir", "hırıstiyanlar": "hıristiyanlar",
    "ilr": "ile", "inananU": "inanan", "inananırlar": "inanırlar", "insanaların": "insanların",
    "işitiğimiz": "işittiğimiz", "işyer": "işler", "karşılığnda": "karşılığında",
    "kendisiden": "kendisinden", "kendisinine": "kendisine",
    "kiimselere": "kimselere", "kimeler": "kimseler", "kimseen": "kimse",
    "kinselerle": "kimselerle", "kokuşmuşdur": "kokuşmuştur", "kulllarına": "kullarına",
    "kuluk": "kulluk", "kütülüktür": "kötülüktür", "kınananrak": "kınanarak",
    "mefaattir": "menfaattir", "mubarek": "mübarek", "muhakkah": "muhakkak",
    "mühtiş": "müthiş", "mükafatladırsın": "mükafatlandırsın", "münezehtir": "münezzehtir",
    "niyyetle": "niyetle", "okimseler": "o kimseler", "olduklarnız": "olduklarınız",
    "olmuyurdu": "olmuyordu", "oludu": "oldu", "onladan": "onlardan", "oun": "onun",
    "oyüzden": "o yüzden", "oğuşturmağa": "ovuşturmaya", "peypambere": "peygambere",
    "rahmetdir": "rahmettir", "rızıkandırdığımız": "rızıklandırdığımız", "sabdederseniz": "sabrederseniz",
    "sarfettikeri": "sarf ettikleri", "sağnak": "sağanak", "saşırtır": "şaşırtır",
    "secede": "secde", "sorumluk": "sorumluluk", "sukün": "sükûn",
    "sürüklenceklerdir": "sürükleneceklerdir", "takdie": "takdir",
    "traş": "tıraş", "umulurki": "umulur ki", "umutlarnı": "umutlarını",
    "uzurumda": "huzurumda", "uçlarnı": "uçlarını", "uğratılcak": "uğratılacak",
    "varmı": "var mı", "vasiyyeti": "vasiyeti", "vasiyyettir": "vasiyettir",
    "verilelerden": "verilenlerden", "verilerlerden": "verilenlerden", "vre": "ve", "vw": "ve",
    "yalanlayacakla": "yalanlayacaklar", "yaparladı": "yaparlardı", "yapasa": "yaparsa",
    "yardımcların": "yardımcıların", "yasasadır": "yasasıdır", "yaslanılar": "yaslanırlar",
    "yazılıdığı": "yazıldığı", "yerlebir": "yerle bir", "yetiğinden": "yettiğinden",
    "yokki": "yok ki", "yükselttiyor": "yükseltiyor",
    "çekiyorsanuz": "çekiyorsanız", "çevirne": "çevirme", "çokca": "çokça",
    "çoçuklarını": "çocuklarını", "çökmüç": "çökmüş", "ödüllendireleceklerdir": "ödüllendirileceklerdir",
    "ölçyü": "ölçüyü", "üyerine": "üzerine", "üzeine": "üzerine", "üzelerine": "üzerlerine",
    "şeayet": "şayet", "şüpheiz": "şüphesiz", "şüphsiz": "şüphesiz",
    "olara": "onlara", "yoks": "yoksa",
    "Allahın": "Allah'ın", "Allahınki": "Allah'ınki", "Allaha": "Allah'a", "Allahtır": "Allah'tır",
    "Alla'ın": "Allah'ın", "Allan'tan": "Allah'tan", "Rabin": "Rabbin", "Rabb'ine": "Rabbine",
    "değiştirmeğ": "değiştirmey", "düzenlemeğ": "düzenlemey", "göstermeğ": "göstermey", "yaratmağ": "yaratmay",
    "öldüremeye": "öldürmeye", "yaşatamaya": "yaşatmaya", "kaldıramaya": "kaldırmaya",
    "mekmi": "mek mi", "nede": "ne de", "fetihden": "fetihten", "hasedcinin": "hasetçinin",
    "azabdan": "azaptan", "azabda": "azapta", "gazabdan": "gazaptan",
    "galibdir": "galiptir", "galibtir": "galiptir", "müteşabihdir": "müteşabihtir",
    "gelmekden": "gelmekten", "inanmakdan": "inanmaktan", "işde": "işte", "kaçdı": "kaçtı",
    "nasibetdiği": "nasip ettiği", "mikdar": "miktar", "mütevazi": "mütevazı",
    "Allahdan": "Allah'tan", "tagutdan": "tağuttan",
    "ZikirKitapdandır": "Zikir Kitaptandır", "alçakdünyanın": "alçak dünyanın",
    "yücemünezzehdir": "yüce münezzehtir", "vaaddir": "vaattir",
    "vukubulacaktır": "vuku bulacaktır", "hesabedeceğini": "hesap edeceğini",
    "talebetmeleri": "talep etmeleri", "takibederse": "takip ederse",
    "feryadederler": "feryat ederler", "feryadediyor": "feryat ediyor",
    "kasdetti": "kastetti", "kasden": "kasten",
    "kableri": "kalpleri", "kablerinde": "kalplerinde", "çağırıyı": "çağrıyı",
    "umud": "umut", "ulud": "ulu", "ayırdelinceye": "ayırt edilinceye", "lutfi": "lütfu",
    "inananUlar": "inananlar", "düzenlemeğe": "düzenlemeye", "değiştirmeğe": "değiştirmeye",
    "göstermeğe": "göstermeye", "yaratmağa": "yaratmaya",
    "çıkaranlanın": "çıkaranların", "şeyndendir": "şeylerdendir", "vereniz": "verenleriz",
    "öldürmekmi": "öldürmek mi",
    "sonre": "sonra", "Allah'dan": "Allah'tan", "zerine": "üzerine",
    "kendilerin": "kendilerinin", "hakında": "hakkında", "bilendi": "bilendir",
    "işitendi": "işitendir", "seden": "senden", "arasıdan": "arasından", "ayırd": "ayırt",
    "Kitapı": "Kitabı", "dünya'da": "dünyada", "O'dan": "O'ndan",
    "kimselerim": "kimselerin", "Kur'ana": "Kur'an'a", "Kur'anı": "Kur'an'ı",
    "Kur'andan": "Kur'an'dan", "Rabbi'imiz": "Rabbimiz", "Rabbi'ndendir": "Rabbindendir",
    "Rabbi'nizden": "Rabbinizden", "Rab'lerinin": "Rablerinin", "soruyarlar": "soruyorlar",
    "misini": "misiniz", "eyetlerimizi": "ayetlerimizi", "azabtan": "azaptan",
    "ni'metdir": "ni'mettir",
    "muhakak": "muhakkak", "mukakkak": "muhakkak", "yoludan": "yolundan",
    "tesbit": "tespit", "geldimi": "geldi mi", "bır": "bir", "ce": "ve", "he": "her",
    "sena": "sana", "O'un": "O'nun", "bi": "bir", "derd": "dert", "azad": "azat", "zıd": "zıt",
    "arab": "Arap", "araplar": "Araplar", "arapça": "Arapça",
}

# Do not match fragments after apostrophes (for example rü'yada or va'dedilmiş).
TOKEN = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*")

if __name__ == "__main__":
    tr = json.loads((ROOT / "turkish-wbw-translation.json").read_text(encoding="utf-8"))
    en = json.loads((ROOT / "english-wbw-translation.json").read_text(encoding="utf-8"))
    for key, value in tr.items():
        # Review complete surfaces: derd(i) is the valid inflection derdi,
        # not an occurrence of the misspelled standalone form derd.
        hits = [word for word in TOKEN.findall(value.replace("(", "").replace(")", "")) if word in CANDIDATES]
        if hits:
            print(key, json.dumps(value, ensure_ascii=False), "|", en[key], "|", ", ".join(hits))
