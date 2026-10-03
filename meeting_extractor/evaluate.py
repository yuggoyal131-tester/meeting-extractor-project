"""Step 6a: evaluate extraction accuracy against hand-labelled ground truth.
Usage: python evaluate.py [--llm]"""
import glob, json, sys
from datetime import date
from extractor.pipeline import run
from extractor.validate import _tokens


def similar(a, b):
    ta, tb = _tokens(a), _tokens(b)
    return len(ta & tb) / min(len(ta), len(tb)) if ta and tb else 0.0


def evaluate(pred, truth, threshold=0.5):
    used, tp, own_ok, dl_ok = set(), 0, 0, 0
    for p in pred:
        scores = [(similar(p.task, t["task"]), j) for j, t in enumerate(truth) if j not in used]
        if not scores:
            break
        s, j = max(scores)
        if s >= threshold:
            used.add(j); tp += 1
            t = truth[j]
            own_ok += (p.owner or "").lower() == (t["owner"] or "").lower()
            dl_ok += p.deadline == t["deadline"]
    prec = tp / len(pred) if pred else 0
    rec = tp / len(truth) if truth else 0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
    return dict(tp=tp, pred=len(pred), truth=len(truth), precision=prec, recall=rec, f1=f1,
                owner_acc=own_ok / tp if tp else 0, deadline_acc=dl_ok / tp if tp else 0)


if __name__ == "__main__":
    mode = "llm" if "--llm" in sys.argv else "rule"
    tot = dict(tp=0, pred=0, truth=0, own=0, dl=0)
    for f in sorted(glob.glob("data/meeting_*.txt")):
        gt = json.load(open(f.replace(".txt", ".json")))
        pred = run(open(f).read(), date.fromisoformat(gt["meeting_date"]), mode)
        r = evaluate(pred, gt["action_items"])
        print(f"{f}: P={r['precision']:.2f} R={r['recall']:.2f} F1={r['f1']:.2f} "
              f"owner_acc={r['owner_acc']:.2f} deadline_acc={r['deadline_acc']:.2f}  "
              f"({r['tp']} correct / {r['pred']} predicted / {r['truth']} true)")
        tot["tp"] += r["tp"]; tot["pred"] += r["pred"]; tot["truth"] += r["truth"]
        tot["own"] += r["owner_acc"] * r["tp"]; tot["dl"] += r["deadline_acc"] * r["tp"]
    P = tot["tp"] / tot["pred"]; R = tot["tp"] / tot["truth"]
    print(f"\nOVERALL ({mode}): precision={P:.2f} recall={R:.2f} F1={2*P*R/(P+R):.2f} "
          f"owner_acc={tot['own']/tot['tp']:.2f} deadline_acc={tot['dl']/tot['tp']:.2f}")
