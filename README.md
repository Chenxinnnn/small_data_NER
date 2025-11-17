# Prompting：Flan-T5 与 ChatGPT（GPT-4o）

## Prompt 设计

### ChatGPT（GPT-4o）Prompt

> GPT-4o 属于强指令遵循（instruction-following）的 LLM，能够严格理解结构化规则与医学定义。因此 Prompt 采用“自然语言指令 + 严格规则 + JSON 输出格式”的 few-shot 设计。

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

> Flan-T5 是指令微调后的 Seq2Seq 模型，不擅长生成严格 JSON，因此在 Prompt 中沿用相同的实体定义与规则，但将输出简化为半结构化文本格式（`e1; e2; e3`），以降低格式约束难度。

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

## 实验结果（基于最新数据）

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

![Few-shot 效果图1](figure/flan-t5_gpt-4o_f1_vs_k.png)  

![Few-shot 效果图2](figure/flan-t5_gpt-4o_all_vs_k.png)  

![Few-shot 效果图3](figure/flan-t5_gpt-4o_time_vs_k.png)

---

## 结果分析（基于真实 Structured Prompt）

### 1. Flan-T5：无法稳定执行严格结构化抽取，且在 k=20 时完全崩溃
- 面对包含实体定义、排除项、RULES 的复杂 Prompt，Flan-T5 的 Seq2Seq 解码难以保持格式稳定。  
- 尽管 few-shot 提高了信息量，但模型缺乏 LLM 级别的 in-context 学习能力，因此 F1 仅从 0.12 → 0.21。  
- k=20 时 Prompt 长度超过最大输入窗口，**模型直接输出空结果（全部 None）**，F1=0。  
- 说明 Flan-T5 不能可靠处理长 Prompt，也难以遵守严格的 span-level extraction 规则。

---

### 2. GPT-4o：能充分利用结构化 Prompt，few-shot 效果显著
- GPT-4o 对“定义 + 规则 + exact span + JSON 输出”理解准确，能稳定执行结构化抽取。  
- few-shot 示例帮助模型快速建立抽取模式，F1 从 0.44 → **0.51** 持续提升。  
- k=10 与 k=20 的 F1 均约为 **0.514**，说明模型在样本足够后已“学满”，进入饱和状态。  
- Recall 保持在 **0.55+**，显示结构化提示有效减少漏报；Precision 稍低但稳定，反映部分“边界稍宽”。  

---

### 3. 推理时间呈现典型 Prompting 特点：随 k 增加显著上升
- GPT-4o 受 API 远程推理影响，时间从 554s → 1256s（k=1→20）。  
- Flan-T5 虽然更快，但性能不足且最终因输入超长而崩溃。  
- 整体趋势符合 Prompting 的典型 trade-off：  
  **无需训练 → 但推理成本随 Prompt 长度线性增长。**

---

## 总结

- **Flan-T5**  
  - 对严格结构化 Prompt 不够鲁棒  
  - few-shot 无明显提升  
  - 长 prompt 导致输入溢出，k=20 时完全失败  

- **GPT-4o**  
  - 能理解并严格遵守结构化提示  
  - few-shot 能力强，F1 在 k=10–20 稳定于 0.51  
  - 在小样本临床 NER 中表现出可靠的 span-level 抽取能力  

**结论：结构化 JSON Prompt + GPT-4o 是低资源临床实体识别中最稳定、最有效的 prompting 方案之一。**
