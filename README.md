
# <img src="./figs/LOGO_v3.png" alt="MMR-V: *What's Left Unsaid?* A Benchmark for Multimodal Deep Reasoning in Videos" width="5%">  MMR-V: *What's Left Unsaid?* A Benchmark for Multimodal Deep Reasoning in Videos


<p align="center">
  <a href="https://huggingface.co/datasets/JokerJan/MMR-VBench"> 🤗 Benchmark</a></a> |
  <a href="https://arxiv.org/abs/2506.04141"> 📝 Paper</a> |
  <a href="https://mmr-v.github.io/"> 🏠 Homepage</a>
</p>




## 👀 MMR-V Overview
> The sequential structure of videos poses a challenge to the ability of multimodal large language models (MLLMs) to 🕵️locate multi-frame evidence and conduct multimodal reasoning. However, existing video benchmarks mainly focus on understanding tasks, which only require models to match frames mentioned in the question and perceive a few adjacent frames. To address this gap, we propose **MMR-V: A Benchmark for Multimodal Deep Reasoning in Videos**. Models like o3 and o4-mini have achieved impressive results on **"Think with Images"** tasks, which require models to 🕵️mine evidence on image. Similarly, tasks in MMR-V require models to perform in-depth reasoning over visual information from different frames of a video, challenging their ability to 🕵️mine evidence across long-range multi-frame (**"Think with Video"**).

### 🌟 Highlights
* *Long-range, multi-frame reasoning*: Models are required to infer and analyze evidence frames that may be far from the question frame. 

* *Beyond perception*: Questions cannot be answered through direct perception alone but require reasoning over hidden information. 

* *Reliability*: All tasks are **manually annotated**, referencing extensive real-world user understanding to align with common perceptions. 

* *Confusability*: Carefully designed distractor annotation strategies to reduce model shortcuts. 

MMR-V consists of **317** videos and **1,257** tasks. All videos and tasks have been manually reviewed to ensure quality and diversity, aiming to closely reflect real-world scenarios.

## 🎬 MMR-V Task Examples

<p align="center">
    <img src="./figs/data_example_intro_v4_5_16.png" width="100%" height="100%">
</p>

---

## 🚀 Quick Start

1. Load the MMR-V Benchmark

```shell
huggingface-cli download JokerJan/MMR-VBench --repo-type dataset --local-dir MMR-V --local-dir-use-symlinks False
```
2. Extract videos from the `.tar` files:

```shell
cat videos.tar.part.* > videos.tar
tar -xvf videos.tar
```

3. Data Format
   
All data in **MMR-V** are standardized to the following format:
```json
{
    "video": "Level 1 to 100 Magic Tricks Anyone Can Do.mp4",
    "videoType": "TV",
    "question": "How does the man at the beginning of the video pick up and casually control the flame on the lighter?",
    "options": [
      "(A) He used a holographic projector to simulate the flame.",
      "(B) He used a special flame-retardant chemical on his hand to create the illusion.",
      "(C) He possessed an innate immunity to fire.",
      "(D) He practiced yoga meditation to withstand any flame heat.",
      "(E) A quick extinguishing spray was applied that halted the flame.",
      "(F) He surrounded the flame with an invisible film.",
      "(G) He mastered the art of fire manipulation.",
      "(H) The flame was made of non-flammable gas.",
      "(I) He applied a hidden cooling technology under his sleeve.",
      "(J) The flame was actually an LED light.",
      "(K) A hidden lighter in his hand, a sleight of hand trick."
    ],
    "correctAnswer": "(K)",
    "abilityType_L2": "Counterintuitive Reasoning",
    "abilityType_L3": "Magic Deconstruction",
    "question_idx": 20
}
```

4. Evaluation Settings:
   
Please place the unzipped video file under `MMR-V/videos`.

Other model inference details and implementation can be found in `utils
/video_utils.py`.

5. Evaluation with script:

```shell
python evaluation/server_evaluation_on_MMR.py \
      --model_name gemini-2.5-flash-preview-04-17 \
      --api_url https://XXX/v1/chat/completions \
      --api_key sk-XXX \
      --with_cot \
      --frame_count 32
```
Please provide valid API information at the `--api_url` and `--api_key` fields. For open-source models running on a local `vllm` server, set `--api_url` to the local server address and leave `--api_key` empty. If the `--with_cot` flag is specified, the evaluation will use *Chain-of-Thought (CoT) prompting*; otherwise, the model will default to *directly* outputting the final answer.

---
## 📊 Leaderboard <a name="leaderboard"></a>
| Rank | Model | Overall | Implicit | Explicit | Art | Life | TV | Film | Film | Phi. |
|---|---|---|---|---|---|---|---|---|---|---|
| 🥇 |  Human | 86.0 | 80.6 | 91.2 | 57.7 | 92.3 | 90.6 | 92.3 | 90.7 | 70.0 |
| 🥈 | o4-mini | 52.5 | 54.6 | 46.0 | 40.1 | 54.0 | 54.0 | 51.7 | 65.3 | 27.9 |
| 🥉 | Gemini-2.5-Flash | 51.2 | 52.9 |  46.9 |  45.3 | 39.5 | 50.3 | 47.9 | 65.6 | 34.9 |

*Full leaderboard in [our homepage](https://mmr-v.github.io/).*

*📢 The leaderboard is constantly updating as we are welcoming new submissions!*

---



## 🎯 Experiment Results

### Performance across Different Tasks

<p align="center">
    <img src="./figs/task_analysis_final.png" width="35%" height="35%">
</p>

### Impact of Audio Input

<p align="center">
    <img src="./figs/audio.png" width="80%" height="80%">
</p>


### Error Analysis
<p align="center">
    <img src="./figs/error analysis_00.png" width="35%" height="35%">
</p>

---

## 🧠 Model Response Examples

The figure below presents example responses with Multimodal Chain-of-Thought (MCoT) from two reasoning models to a sample task from MMR-V. (Gemini's response omits part of the option analysis.) In the visualization, *yellow tokens represent reasoning and analysis based on textual information (e.g., the question and answer options), while green tokens indicate the model’s analysis of visual content from the video (including the question frame and evidence frames)*. It can be observed that **o4-mini** engages in deeper reasoning and analysis of the **video content**, ultimately arriving at the correct answer. In contrast, Gemini exhibits a more text-dominated reasoning strategy. This example highlights how MMR-V places greater emphasis on a model’s ability to incorporate visual information into the reasoning process and to mine multimodal cues effectively. 
<p align="center">
    <img src="./figs/o4-compare_00.png" width="60%" height="60%">
</p>
The full video corresponding to this example can be found here: https://www.youtube.com/watch?v=g1NuAfkQ-Hw.

## 📜 Citation

We sincerely appreciate it if **MMR-V** provides any inspiration or assistance to your research. Please consider citing the following article and giving us a star⭐.

```bibtex
@misc{zhu2025mmrvwhatsleftunsaid,
      title={MMR-V: What's Left Unsaid? A Benchmark for Multimodal Deep Reasoning in Videos}, 
      author={Kejian Zhu and Zhuoran Jin and Hongbang Yuan and Jiachun Li and Shangqing Tu and Pengfei Cao and Yubo Chen and Kang Liu and Jun Zhao},
      year={2025},
      eprint={2506.04141},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2506.04141}, 
}
```

---
