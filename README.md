
# Prompting Flan-T5 & ChatGPT（GPT-4o-mini）

## Prompt 设计

### ChatGPT（GPT-4o-mini）Prompt

> 在 ChatGPT（GPT-4o-mini）中使用较自然的指令式提示，因为该模型擅长理解开放式英文任务描述，并能根据上下文灵活输出结构化结果。

You are a medical information extraction assistant.
Task: Extract all medical entities mentioned in each clinical sentence below.
If no medical entity is found, output: Entity: None
Output them strictly after 'Entity:' separated by semicolons.
Do not add explanations or extra text.

Example 1:
Sentence: Coronary angiography done demonstrated significant lesions in the mid portion of the Left Descending Coronary Artery ( LAD ) and the proximal Circumflex Coronary Artery ( Cx ) .
Entity: lesions in the mid portion of the Left Descending Coronary Artery

Now analyze the following sentence:
Sentence:

### Flan-T5 Prompt

> 相比之下，Flan-T5 属于指令微调的 Seq2Seq 模型，需要更明确的输入输出格式，因此在 Prompt 中采用了“Input–Target”结构来强化格式一致性。

Instruction: Extract all medical entities from the input sentence.
If no medical entity is found, output: Entity: None
Format the output as: Entity: entity1; entity2; ...

Input: Coronary angiography done demonstrated significant lesions in the mid portion of the Left Descending Coronary Artery ( LAD ) and the proximal Circumflex Coronary Artery ( Cx ) .
Target: Entity: lesions in the mid portion of the Left Descending Coronary Artery


---

## 实验结果

| model        | k  | F1        | Precision | Recall  | Inference Time (s) |
|---------------|----|-----------|------------|----------|--------------------|
| flan-t5       | 1  | 0.0348    | 0.0368     | 0.0329   | 135.7 |
| flan-t5       | 5  | 0.0407    | 0.0456     | 0.0368   | 128.1 |
| flan-t5       | 10 | 0.0000    | 0.0000     | 0.0000   | 132.0 |
| flan-t5       | 20 | 0.0000    | 0.0000     | 0.0000   | 199.0 |
| gpt-4o-mini   | 1  | 0.2568    | 0.1566     | 0.7132   | 581.5 |
| gpt-4o-mini   | 5  | 0.2647    | 0.1610     | 0.7442   | 698.4 |
| gpt-4o-mini   | 10 | 0.2972    | 0.1855     | 0.7461   | 641.9 |
| gpt-4o-mini   | 20 | 0.3028    | 0.1906     | 0.7364   | 601.6 |

![Few-shot 效果图](figure/flan-t5:gpt-4o-mini_f1_vs_k.png)

---

1. **Flan-T5 表现极低**  
   - 模型不擅长开放式实体抽取任务。  
   - few-shot 样例过多时输入被截断，导致输出不稳定。  
   - 当 k ≥ 10，模型输出几乎全部为 “Entity: None”。  

2. **GPT-4o-mini 表现稳定且提升明显**  
   - few-shot 学习效果好，F1 随 k 上升。  
   - Recall 高（≈0.7），说明识别覆盖广；Precision 稍低，说明有多余实体输出。  

3. **推理时间差距明显**  
   - Flan-T5 为本地 GPU 推理，速度快但能力有限。  
   - GPT-4o-mini 为远程 API 调用，推理慢但识别能力强。

