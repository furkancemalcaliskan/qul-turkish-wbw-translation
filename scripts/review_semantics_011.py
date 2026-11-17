"""Final targeted spelling consistency discovered while rereading semantic contexts."""
import argparse
from semantic_review import ReviewBatch,validate


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--apply",action="store_true");args=parser.parse_args()
    b=ReviewBatch("semantic-review-011","Targeted spelling-only follow-up: the already observed future-negative typo and explicitly identified eating imperatives. No unrestricted substring substitution.")
    if b.exists:validate();return
    for key,value in {"4:3:3":"(adaleti sağlaya)mayacağ(ınızdan)","4:3:4":"adaleti sağlaya(mayacağ)ınızdan"}.items():
        b.change(key+"-future-negative-spelling",{key:value},"Correct mıyacağ to mayacağ in the inherited future-negative expression sağlayamayacağınızdan. Preserve the existing source-role split and contextual inability reading; this does not add a new modal interpretation.")
    keys="4:4:12 5:4:18 34:15:11 67:15:10 52:19:1 7:19:6 69:24:1 2:35:7 22:36:18 77:43:1 23:51:3 20:54:1 2:57:8 2:58:6 2:60:19 8:69:1 20:81:1 5:88:1 16:114:1 6:118:1 6:141:17 6:142:5 7:160:33 7:161:7 2:168:3 2:172:4".split()
    for key in keys:
        assert "eat" in b.en[key].lower(),key
        assert "yeyin" in b.before[key],key
        b.change(key+"-eat-imperative-spelling",{key:b.before[key].replace("yeyin","yiyin")},"The Arabic and English at this explicitly selected location are an eating imperative. Normalize yeyin/yeyiniz to standard yiyin/yiyiniz while preserving local conjunctions, objects and register. Do not replace unrelated strings such as söyleyeyim, hikayeyi or an alignment fragment ending in -yeyim.")
    b.finish(args.apply)


if __name__=="__main__":main()
