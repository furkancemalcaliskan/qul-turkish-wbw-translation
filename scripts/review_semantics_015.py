"""Modern infinitive inflection at explicitly reviewed verbal locations."""
import argparse
from semantic_review import ReviewBatch, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    b = ReviewBatch("semantic-review-015", "Normalize explicitly selected archaic verbal infinitive inflections to modern Turkish -maya/-meye. Distinguish the verbal noun yemeyi from the food noun yemeği and preserve unrelated mağara, armağan and meğer. No automatic substring-wide ğ replacement.")
    if b.exists:
        validate()
        return
    keys = """5:2:36 5:2:37 40:5:12 34:5:5 4:6:14 4:6:15 35:6:10 57:8:8
2:9:1 62:9:12 72:9:6 61:12:14 9:13:7 46:15:24 46:15:25 46:15:33
41:17:7 56:17:4 14:17:1 23:18:11 81:18:3 89:18:3 89:18:4 25:19:7
32:19:8 39:22:15 79:22:3 7:22:10 39:24:2 42:29:13 68:30:5 38:33:4
46:33:14 46:33:15 55:33:6 55:33:7 5:33:10 54:37:2 6:37:13 6:37:14
22:39:9 75:40:5 75:40:6 22:41:12 34:42:8 40:42:2 40:42:4 26:45:6
43:47:7 30:51:9 18:59:4 18:59:5 40:60:9 40:60:10 12:61:2 9:63:5
22:64:12 6:65:5 6:65:6 6:65:18 19:70:8 5:76:12 12:76:1 18:77:16
18:77:17 40:78:32 6:81:19 17:81:8 17:81:9 28:82:6 9:83:20 23:91:17
9:93:9 9:93:10 3:99:5 18:101:11 4:113:9 4:113:10 6:113:9 20:121:7
4:142:3 3:186:22 3:186:23 2:205:8 7:190:6 2:226:2 2:228:24 26:227:9""".split()
    for key in keys:
        before = b.before[key]
        after = before.replace("mağa", "maya").replace("meğe", "meye").replace("mağ(a)", "may(a)").replace("meğ(e)", "mey(e)").replace("mağ)a", "may)a").replace("meğ)e", "mey)e")
        assert before != after, (key, before)
        b.change(key + "-modern-infinitive", {key: after}, "This explicitly reviewed location contains a verbal infinitive/nominalized action, not the food noun yemek, the effort noun emek, or a word such as mağara/armağan/meğer. Normalize archaic -mağa/-meğe (including split notation) to -maya/-meye; preserve the action, person, polarity and existing source allocation. This is a modern-spelling normalization, not evidence that every older infinitive form is semantically erroneous.")
    b.change("49:12:20-eating-infinitive", {"49:12:20": "(ye)meyi", "49:12:21": "ye(meyi)"}, "The clause is kardeşinin etini yemeyi sever mi: Arabic an ya'kula and English to eat require the nominalized action yemeyi, not the meal noun yemeği. Keep the an-token infinitive contribution outside parentheses and the eating stem foregrounded at the verb token. Actual food-noun forms at 2:61:7 and 33:53:13 remain unchanged.")
    b.finish(args.apply)


if __name__ == "__main__":
    main()
