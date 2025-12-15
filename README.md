# Prompting: Flan-T5 and ChatGPT (GPT-4o)

## Prompt Design

### ChatGPT (GPT-4o) Prompt

> GPT-4o is a large language model with strong instruction-following capability. It can strictly understand structured rules and medical definitions. Therefore, the prompt adopts a few-shot design combining **natural language instructions + strict rules + JSON output format**.

You perform strict span-level extraction of clinical entities.  
All extracted spans must be labeled as type "ety".

"ety" refers ONLY to text spans that explicitly denote a clinical abnormality.  
It includes the following categories:
- diseases or diagnosable conditions
- symptoms or signs
- abnormal masses or structural abnormalities
- pathological exam/imaging/biopsy findings
- laboratory abnormalities
- infections or pathogen-related abnormalities
- clinical events such as bleeding, obstruction, necrosis

"ety" does NOT include:
- normal anatomy
- raw numbers or lab values without interpretation
- appearance descriptions (pale, weak)
- medications, treatments, procedures, or causes
- demographic, temporal, occupational, or contextual information

RULES:
- Extract ONLY spans appearing EXACTLY in the text.
- Do NOT infer, expand, merge, or paraphrase.
- Keep spans minimal but medically complete.
- Output MUST be a JSON array.
- Each entity must be an object: {"text": <span>, "type": "ety"}.
- If no valid entities exist, output [].

Example:

Sentence: Coronary angiography done demonstrated significant lesions in the mid portion of the Left Descending Coronary Artery ( LAD ) and the proximal Circumflex Coronary Artery ( Cx ).  
[{"text": "lesions in the mid portion of the Left Descending Coronary Artery", "type": "ety"}]

Sentence:

---

### Flan-T5 Prompt

> Flan-T5 is an instruction-tuned Seq2Seq model and is not good at generating strict JSON formats. Therefore, the same entity definitions and rules are retained in the prompt, but the output is simplified to a semi-structured text format (`e1; e2; e3`) to reduce formatting constraints.

Extract clinical entities from the sentence.  
Only extract spans that explicitly describe an abnormal medical condition.

Valid entity types (all treated as "ety") include:
- diseases or medical diagnoses
- symptoms or signs of illness
- abnormal masses or structural abnormalities
- pathological exam, imaging, or biopsy findings
- laboratory abnormalities
- infections or pathogen-related abnormalities
- clinical events (bleeding, necrosis, obstruction)

NOT entities:
- normal anatomy
- raw numbers or lab values
- appearance descriptions (e.g., pale, weak)
- medications, procedures, or causes
- time, demographics, or contextual information

RULES:
- Copy spans EXACTLY from the sentence.
- Do NOT add, merge, guess, or paraphrase.
- If no valid entities exist, output: None  
Output format: e1; e2; e3

Example:

Sentence: Coronary angiography done demonstrated significant lesions in the mid portion of the Left Descending Coronary Artery ( LAD ) and the proximal Circumflex Coronary Artery ( Cx ).  
lesions in the mid portion of the Left Descending Coronary Artery

Sentence:

---

## Experimental Results (Based on Latest Data)

| model   | k  | Precision | Recall  | F1        | Inference Time (s) |
|---------|----|-----------|----------|-----------|---------------------|
| flan-t5 | 1  | 0.2500    | 0.0780   | 0.1189    | 461.3 |
| flan-t5 | 5  | 0.2736    | 0.1131   | 0.1600    | 465.1 |
| flan-t5 | 10 | 0.2487    | 0.1832   | 0.2110    | 511.4 |
| flan-t5 | 20 | 0.0000    | 0.0000   | 0.0000    | 660.8 |
| gpt-4o  | 1  | 0.3877    | 0.5146   | 0.4422    | 554.0 |
| gpt-4o  | 5  | 0.4185    | 0.5653   | 0.4809    | 687.9 |
| gpt-4o  | 10 | 0.4797    | 0.5536   | **0.5140** | 852.2 |
| gpt-4o  | 20 | 0.4790    | 0.5556   | **0.5144** | 1256.1 |

![Few-shot Performance Figure 1](figure/flan-t5_gpt-4o_f1_vs_k.png)  

![Few-shot Performance Figure 2](figure/flan-t5_gpt-4o_all_vs_k.png)  

![Few-shot Performance Figure 3](figure/flan-t5_gpt-4o_time_vs_k.png)

---

## Result Analysis (Based on Real Structured Prompts)

### 1. Flan-T5: Unable to stably perform strict structured extraction, and completely collapses at k=20
- When facing complex prompts containing entity definitions, exclusions, and RULES, the Seq2Seq decoding of Flan-T5 struggles to maintain format stability.  
- Although few-shot increases the amount of information, the model lacks LLM-level in-context learning ability, so F1 only improves from 0.12 → 0.21.  
- At k=20, the prompt length exceeds the maximum input window, and **the model directly outputs empty results (all None)**, resulting in F1=0.  
- This indicates that Flan-T5 cannot reliably handle long prompts and has difficulty adhering to strict span-level extraction rules.

---

### 2. GPT-4o: Effectively leverages structured prompts with significant few-shot gains
- GPT-4o accurately understands “definitions + rules + exact spans + JSON output” and can stably perform structured extraction.  
- Few-shot examples help the model quickly establish extraction patterns, with F1 steadily improving from 0.44 → **0.51**.  
- F1 at k=10 and k=20 is both around **0.514**, indicating the model reaches saturation once enough examples are provided.  
- Recall remains above **0.55**, showing that structured prompting effectively reduces false negatives; Precision is slightly lower but stable, reflecting some boundary looseness.

---

### 3. Inference time shows typical prompting behavior: significant growth as k increases
- GPT-4o is affected by remote API inference, with time increasing from 554s → 1256s (k=1→20).  
- Flan-T5 is faster, but performance is insufficient and eventually collapses due to excessive input length.  
- Overall, the trend matches the classic prompting trade-off:  
  **No training required → inference cost grows linearly with prompt length.**

---

## Summary

- **Flan-T5**
  - Not robust to strictly structured prompts  
  - Few-shot provides limited improvement  
  - Long prompts cause input overflow, complete failure at k=20  

- **GPT-4o**
  - Understands and strictly follows structured prompts  
  - Strong few-shot capability, with F1 stabilizing around 0.51 at k=10–20  
  - Demonstrates reliable span-level extraction ability in low-resource clinical NER  

**Conclusion: Structured JSON prompting with GPT-4o is one of the most stable and effective prompting strategies for low-resource clinical entity recognition.**

---

# prototypical_networks

- File Overview
  - `prototypical_networks.ipynb`: Prototypical Networks NER using BioBERT as the encoder. Encoder parameters are fine-tuned. During training, prototypes are constructed within each batch based on labels; during evaluation/prediction, static prototypes are computed from training-set embeddings. Except for the model and loss, the rest of the pipeline is identical to `biobert_baseline.ipynb` (CoNLL loading, subword alignment, class weights, training configuration, metrics, and outputs).
  - `prototypical_networks_baseline.ipynb`: BioBERT encoder is frozen, and only a small projection head (Linear + Tanh + LayerNorm) is trained. Prototype construction logic during training and evaluation is the same as above. This setup learns only the head in few-shot scenarios, reducing overfitting while still using sequence-level F1 as the main metric.

- Core Logic
  - Data & Alignment: Load `train/dev/test` from `conll/fewshot_k{K}_seed42_mention`. Tokenize and align BIO labels; only the first subword of each token is labeled, while remaining subwords are assigned `-100` and ignored in the loss.
  - Class Imbalance: Count label frequencies in the training set, compute inverse-normalized class weights, and slightly down-weight the `O` class. The loss uses `ignore_index=-100` and label smoothing (0.1).
  - Prototype Classification: Use negative Euclidean distance between token representations and class prototypes as logits. During training, prototypes are constructed from batch labels; during evaluation/prediction, “static prototypes” are computed from the full training set before inference.
  - Training Hyperparameters: Aligned with the BioBERT baseline (default `lr=1e-5`, `batch_size=8`, `epochs=50`, `weight_decay=0.01`, wandb disabled).

- Differences Between the Two Versions
  - `prototypical_networks.ipynb`: Trainable encoder (end-to-end fine-tuning), projection is Identity or lightweight mapping; suitable when there is a moderate amount of data and domain adaptation is desired.
  - `prototypical_networks_baseline.ipynb`: Frozen encoder, only a small projection head (Linear + Tanh + LayerNorm) is trained, reducing trainable parameters and improving stability and generalization in few-shot settings.

- Paths & Reproducibility Notes
  - For local runs, modify `BASE` to the project root (e.g., `BASE = Path('.')`) and set `DATA_DIR` to the corresponding few-shot directory (e.g., `fewshot_k1_seed42_mention`, `fewshot_k10_seed42_mention`, etc.). Outputs are written to subdirectories under `results/`, including `metrics.json` and console-printed `classification_report`.

support: 516

Frozen encoder + fine-tuned projection head

| **K-shot** | **Validation F1** | **Precision** | **Recall** | **F1-score (Test)** | **Inference Time (s)** |
| ---------- | ----------------- | ------------- | ---------- | ------------------- | ---------------------- |
| **1**      | 0.6324            | 0.4667        | 0.9089     | 0.6167              | 161.9980               |
| **5**      | 0.6561            | 0.4789        | 0.9031     | 0.6259              | 162.0204               |
| **10**     | 0.6649            | 0.4785        | 0.9050     | 0.6260              | 162.8205               |
| **20**     | 0.6997            | 0.4704        | 0.9070     | 0.6195              | 162.3098               |

Fully frozen

| **K-shot** | **Validation F1** | **Test Precision** | **Test Recall** | **Test F1-score** | **Inference Time (s)** |
| ---------- | ----------------- | ------------------ | --------------- | ----------------- | ---------------------- |
| **1**      | 0.6406            | 0.4800             | 0.9100          | 0.6247            | 143.5993               |
| **5**      | 0.6390            | 0.4800             | 0.9100          | 0.6239            | 143.3418               |
| **10**     | 0.6423            | 0.4800             | 0.9100          | 0.6252            | 142.2335               |
| **20**     | 0.6324            | 0.4700             | 0.9100          | 0.6190            | 142.0920               |

Fine-tuned without freezing: k=10 F1 ≈ 0.49 ?

![Few-shot Performance Figure](figure/prototypical_networks.png)
