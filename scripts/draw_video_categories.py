import matplotlib.pyplot as plt 
import numpy as np

# 调亮版配色方案（明度提升5-10%，灰度减少）
palette = {
    'Art':         ['#C3D8F0', '#B1C8E6', '#9FB8DC', '#8DA8D2'],
    'Animation':  ['#FFD8A8', '#FFC894', '#FFB880', '#FFA86C'],
    'Film':        ['#F0D5D5', '#E8C5C5', '#E0B5B5', '#D8A5A5'],
    'Life':        ['#D5ECD6', '#C3DCC4', '#B1CCB2', '#9FBCA0'],
    'Philosophy': ['#DACEEF', '#C8BEDD', '#B6AECB', '#A49EB9'],
    'TV':          ['#F5FFD6', '#FFEFC2', '#FFDFAE', '#FFCF9A']  # 荧光奶油黄
}


# 数据保持不变
hierarchy = {
    'Art': ['Dance', 'Music MV', 'Stage Play', 'Photography'],
    'Animation': ['Social Issues', 'Daily Theme', 'Personification', 'History'],
    'Film': ['Comedy', 'Science Fiction', 'Short Film', 'Classic'],
    'Life': ['Humor', 'Short Video', 'Travel', 'Anti-Cut Editing'],
    'Philosophy': ['Concept Intro', 'Self-Reflection', 'Psychology', 'Philosophy'],
    'TV': ['Commercial', 'Public Service Ad', 'TV Show', 'Magic']
}

main_labels = list(hierarchy.keys())
sub_labels = [item for sublist in hierarchy.values() for item in sublist]

# 创建画布
fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
fig.patch.set_facecolor('#F7F7F7')

# ===== 颜色分配 =====
main_colors = [palette[k][0] for k in hierarchy.keys()]
assert len(set(main_colors)) == len(main_colors), "主类颜色存在重复！"

# 绘制主分类环（保持原宽度）
main_wedges, _ = ax.pie([1/6]*6,
                        radius=0.5,
                        colors=main_colors,
                        startangle=90,
                        wedgeprops=dict(width=0.3, edgecolor='white', linewidth=2))

# 绘制子分类环（加宽外圈）
sub_colors = []
for main_cat in hierarchy.keys():
    sub_colors.extend(palette[main_cat][:len(hierarchy[main_cat])])

sub_wedges, _ = ax.pie([1/24]*24,
                       radius=0.9,  # 增加半径
                       colors=sub_colors,
                       startangle=90,
                       wedgeprops=dict(width=0.4, edgecolor='white', linewidth=1))  # 加宽环状

# ===== 优化标签位置 =====
def place_labels(main_wedges, sub_wedges, main_labels, sub_labels):
    # 主类标签（内圈）
    for w, label in zip(main_wedges, main_labels):
        ang = (w.theta2 + w.theta1) / 2
        x = np.cos(np.deg2rad(ang)) * 0.35
        y = np.sin(np.deg2rad(ang)) * 0.35
        ax.text(x, y, label, ha='center', va='center',
                fontsize=15, rotation=ang-90 if ang > 90 else ang+90,
                rotation_mode='anchor', color='#333333')

    # 子类标签（调整到更外侧）
    for w, label in zip(sub_wedges, sub_labels):
        ang = (w.theta2 + w.theta1) / 2
        radius = 0.69  # 向外侧移动标签
        x = np.cos(np.deg2rad(ang)) * radius
        y = np.sin(np.deg2rad(ang)) * radius

        # 优化文本旋转逻辑
        rotation = ang if ang < 90 or ang > 270 else ang + 180
        vertical = 'center'
        if 70 < ang < 110:
            vertical = 'bottom'
        elif 250 < ang < 290:
            vertical = 'top'

        ax.text(x, y, label, ha='center', va=vertical,
                fontsize=11, rotation=rotation,
                rotation_mode='anchor', color='#333333',
                alpha=0.9)

# 应用新标签布局函数
place_labels(main_wedges, sub_wedges, main_labels, sub_labels)

# 添加中心圆形留白
center_circle = plt.Circle((0, 0), 0.2, color='white')
ax.add_artist(center_circle)

# 中心 LOGO
ax.text(0, 0, "", 
        ha='center', va='center',
        fontsize=24, 
        color='#666666',
        fontstyle='italic')

plt.savefig('/netdisk/zhukejian/implicit_video_anonotations/figs/video_type.pdf', 
           format='pdf', 
           bbox_inches='tight',
           transparent=True)
plt.close()
