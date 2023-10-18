import numpy as np
import matplotlib.pyplot as plt

# Number of groups and bars per group
num_groups = 7
bars_per_group = 3

# Generate random data
data = np.random.rand(num_groups, bars_per_group, 10)  # 10 data points for each bar

mean_values = np.array([
[5.82, 5.77, 5.93],
[11.05, 13.41685, 12.72505 ],
[27.57,  45.4611,  50.0],
[26.8,  22.20,  27.94] ,
[62.265, 78.41,  108.8] ,
[66.2,  79.1, 101.9] ,
[146.98,  161.6, 192.2]])

std_values = np.array([
[4.194,  2.50,  2.52],
[4.80, 5.608, 4.4964],
[9.85, 14.9111, 16.97],
[8.96294, 5.20, 8.73],
[24.398, 23.08, 35.2],
[19.3, 11.7, 8.4 ],
[10.8, 10.8, 18.0 ]])
# Calculate mean and standard deviation
# mean_values = data.mean(axis=2)
# std_values = data.std(axis=2)

# Generate bar positions for each group and bar
group_width = 0.8
bar_width = group_width / bars_per_group

# Adjust this gap value to increase or decrease the gap between groups
inter_group_gap = 1.2
group_positions = np.arange(num_groups)
bar_positions = [inter_group_gap * group_positions + i*bar_width for i in range(bars_per_group)]

# Plot the bars
fig, ax = plt.subplots()
colors = ['#FF9999', '#99FF99', '#9999FF'] 
num = [10, 20, 30]
for i in range(bars_per_group):
    bars = ax.bar(bar_positions[i], mean_values[:, i], width=bar_width, color=colors[i], label=f'{num[i]}', yerr=std_values[:, i], capsize=5)

# Customize the plot
ax.set_xticks(inter_group_gap * group_positions + group_width / 3)
ax.set_xticklabels(['1', '2', '3', r'$1\wedge2$', r'$1\wedge3$', r'$2\wedge3$', r'$1\wedge2\wedge3$'])
ax.set_xlabel('Scenarios')
ax.set_ylabel('Runtimes/s')
ax.legend()

# Display the plot
plt.tight_layout()
plt.savefig('./data/runtimes.png', format='png', dpi=300)

#################################################################################
# num_groups = 7
# bars_per_group = 3

# # Generate random data
# data = np.random.rand(num_groups, bars_per_group, 10)  # 10 data points for each bar

# mean_values = np.array([
# [65.85, 61.75, 59.8],
# [83.8, 78.9, 76.2],
# [92.35, 88.6, 86.2 ],
# [142.4, 135.45, 134.1],
# [160.7, 149.8, 147.6 ],
# [176.0, 164.0, 161.2],
# [235.5, 223.0, 222.55]] )

# std_values = np.array([
# [5.68, 1.96,  1.77],
# [4.42,  3.32, 0.92],
# [4.49, 2.7415, 2.31],
# [4.89898,  2.77, 2.77],
# [7.61,  5.54,  2.48],
# [1.87,   1.65, 0.76],
#  [1.84, 1.63, 1.44]])
# # Calculate mean and standard deviation
# # mean_values = data.mean(axis=2)
# # std_values = data.std(axis=2)

# # Generate bar positions for each group and bar
# group_width = 0.8
# bar_width = group_width / bars_per_group

# # Adjust this gap value to increase or decrease the gap between groups
# inter_group_gap = 1.2
# group_positions = np.arange(num_groups)
# bar_positions = [inter_group_gap * group_positions + i*bar_width for i in range(bars_per_group)]

# # Plot the bars
# fig, ax = plt.subplots()
# colors = ['#FF9999', '#99FF99', '#9999FF'] 
# num = [10, 20, 30]
# for i in range(bars_per_group):
#     bars = ax.bar(bar_positions[i], mean_values[:, i], width=bar_width, color=colors[i], label=f'{num[i]}', yerr=std_values[:, i], capsize=5)

# # Customize the plot
# ax.set_xticks(inter_group_gap * group_positions + group_width / 3)
# ax.set_xticklabels(['1', '2', '3', r'$1\wedge2$', r'$1\wedge3$', r'$2\wedge3$', r'$1\wedge2\wedge3$'])
# ax.set_yticks(np.arange(0, np.max(mean_values + std_values) + 50, 50))  # y-ticks increment by 50
# ax.set_xlabel('Scenarios')
# ax.set_ylabel('Cost')
# ax.legend()

# # Display the plot
# plt.tight_layout()
# plt.savefig('./data/cost.png', format='png', dpi=300)

