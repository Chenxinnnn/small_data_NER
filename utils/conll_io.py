# Basic CoNLL I/O helper
def read_conll(path):
    sents, sent = [], []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                if sent: sents.append(sent); sent=[]
            else:
                tok, lab = line.split()[:2]
                sent.append((tok, lab))
    if sent: sents.append(sent)
    return sents

def write_conll(sents, path):
    with open(path, 'w', encoding='utf-8') as f:
        for s in sents:
            for tok, lab in s:
                f.write(f"{tok}\t{lab}\n")
            f.write("\n")
