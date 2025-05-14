import matplotlib
matplotlib.use('TkAgg')  # 如果仅保存图形可改为 'Agg'
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置随机种子以保证可重复性
np.random.seed(42)

# -------------------------------
# 1. 自定义任务及角度（单位：度），保证同一类别任务出现在同一侧
# 为保证任务分组根据要求（例如左侧、右侧），这里给定每个任务的角度
task_angle_deg = {
    'CAR': 108,
    'SSR': 144,
    'CIR': 180,
    'CTR': 216,
    'VTI': 252,
    'MU': 288,
    'TU': 324,
    'ER': 360,
    'CM': 36,
    'IS': 72,
}

# 按角度从小到大排序，获得任务顺序和对应弧度值
# 排序后的顺序为：
#   0: 'Comment Matching' (36°)
#   1: 'Implicit Symbol' (72°)
#   2: 'Causal Reasoning' (108°)
#   3: 'Sequential Structure Reasoning' (144°)
#   4: 'Counterintuitive Reasoning' (180°)
#   5: 'Cross-modal Transfer' (216°)
#   6: 'Video Type and Intent' (252°)
#   7: 'Metaphor Understanding' (288°)
#   8: 'Theme Understanding' (324°)
#   9: 'Emotion Recognition' (360°)
sorted_tasks = sorted(task_angle_deg.items(), key=lambda x: x[1])
tasks_order = [task for task, deg in sorted_tasks]
angles = [np.deg2rad(deg) for task, deg in sorted_tasks]

# 为闭合雷达图，在列表尾部补上第一个任务的角度
angles += angles[:1]

# -------------------------------
# 2. 定义 5 个模型（实际名字已自定义）在各任务上的表现数据（单位：0～70，这里示例数值在 0~70 区间）
# 注意：请按下面规定顺序填写数据（各模型的每一行的顺序应与 tasks_order 对应）：
#   位置 0：Comment Matching
#   位置 1：Implicit Symbol
#   位置 2：Causal Reasoning
#   位置 3：Sequential Structure Reasoning
#   位置 4：Counterintuitive Reasoning
#   位置 5：Cross-modal Transfer
#   位置 6：Video Type and Intent
#   位置 7：Metaphor Understanding
#   位置 8：Theme Understanding
#   位置 9：Emotion Recognition
models = ['gpt-4o', 'claude-3-5-sonnet', 'gemini-2.0-flash', 'gemini-2.0-flash-thinking', 'qwen2.5-vl-7b']
performance_data = np.array([
    [5, 50, 45, 27, 27, 50, 38, 39, 51, 49],   # gpt-4o
    [15, 45, 47, 23, 32, 45, 42, 38, 50, 46],   # claude-3-5-sonnet
    [15, 50, 43, 25, 33, 45, 43, 35, 48, 47],   # gemini-2.0-flash
    [10, 52, 48, 34, 33, 45, 40, 40, 49, 50],   # gemini-2.0-flash-thinking
    [5, 34, 37, 20, 12, 35, 25, 28, 35, 37],     # qwen2.5-vl-7b
])
# 注意：performance_data 的每行必须包含 10 个数，顺序按照上述 10 个任务排列。
# 将数据存入 DataFrame，行对应模型，列对应任务（顺序按照 tasks_order 排列）
df = pd.DataFrame(performance_data, index=models, columns=tasks_order)

# -------------------------------
# 3. 为每个模型指定颜色（参考示例图片的配色）
model_colors = {
    "gpt-4o": "#FFA500",                # 橙色
    "claude-3-5-sonnet": "#90EE90",      # 绿色
    "gemini-2.0-flash": "#87CEEB",       # 蓝色
    "gemini-2.0-flash-thinking": "#9370DB",  # 紫色
    "qwen2.5-vl-7b": "#FF6347",          # 红色
}

# -------------------------------
# 4. 自定义每个任务标签的外移半径（位置），单位与数据一致（此处数据范围 0～70）
default_offset = 57  # 默认外移半径（略大于 70）
label_offsets = {
    # "Causal Reasoning": 53,
    # "Sequential Structure Reasoning": 52,
    # "Counterintuitive Reasoning": 52,
    # "Cross-modal Transfer": 52,
    # "Video Type and Intent": 53,
    # "Metaphor Understanding": 53,
    # "Theme Understanding": 53,
    # "Emotion Recognition": 52,
    # "Comment Matching": 55,
    # "Implicit Symbol": 53,
}

# -------------------------------
# 5. 绘制雷达图
plt.figure(figsize=(10, 8))
ax = plt.subplot(111, polar=True)

# 调整极径范围，使其与数据范围匹配（例如 0～70）
ax.set_ylim(0, 55)

# 循环遍历每个模型，绘制闭合曲线及其阴影（不绘制散点）
for model in models:
    # 获取当前模型在各任务上的准确率，并补充第一个数据以闭合曲线
    values = df.loc[model].tolist()
    values += values[:1]
    color = model_colors.get(model, 'black')
    
    # 绘制闭合曲线
    ax.plot(angles, values, label=model, color=color, linewidth=1)
    # 绘制内部阴影（半透明填充）
    ax.fill(angles, values, color=color, alpha=0.15)

# -------------------------------
# 6. 绘制定制的径向线，只在每个任务标签所在的角度处绘制
# 首先隐藏默认的极坐标角度刻度（默认是每45°一条）
ax.set_xticks([])
# 在每个任务标签角度处画出径向线
for angle in angles[:-1]:
    ax.plot([angle, angle], [0, 55], color='grey', linestyle='--', linewidth=0.5)

# -------------------------------
# 7. 设置任务标签
# 在每个任务标签角度处放置文本，位置根据自定义外移半径设定
for idx, task in enumerate(tasks_order):
    angle = angles[idx]
    offset = label_offsets.get(task, default_offset)
    # 根据角度调整水平对齐方式（确保文字不因位置过近而遮挡）
    if np.pi/2 < angle < 3*np.pi/2:
        ha = "right"
    else:
        ha = "left"
    ax.text(angle, offset, task, size=17, horizontalalignment=ha, verticalalignment="center")

# -------------------------------
# 8. 设置 Y 轴刻度（准确率），可自定义这些刻度
ax.set_yticks([10, 20, 30, 40, 55])
ax.set_yticklabels([str(i) for i in [10, 20, 30, 40, 55]], color="grey", size=10)

# -------------------------------
# 9. 图例、布局及保存
# plt.legend(loc='upper right', bbox_to_anchor=(1.6, 1.2), fontsize=13)
plt.legend(
    loc='upper center',
    bbox_to_anchor=(0.5, 1.25),  # 调整位置：正上方
    ncol=2,                      # 一行放三个
    prop=font_prop,             # 使用指定字体
    frameon=False               # 去掉图例边框（可选）
)
plt.tight_layout()
plt.savefig(
    '/netdisk/zhukejian/implicit_video_anonotations/figs/task_analysis.pdf',
    format='pdf',
    bbox_inches='tight',
    transparent=True
)
# 如需显示图形，请取消下面注释
# plt.show()
