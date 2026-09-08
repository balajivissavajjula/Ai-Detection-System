import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import ConfusionMatrixDisplay
import json
import os

# -----------------------------
# Metrics (Update these if needed)
# -----------------------------

accuracy = 0.90
precision = 0.9333
recall = 0.90
f1 = 0.9029

# -----------------------------
# Save Metrics JSON
# -----------------------------

metrics = {
    "Accuracy": accuracy,
    "Precision": precision,
    "Recall": recall,
    "F1 Score": f1
}

with open("metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

# -----------------------------
# Metrics Bar Graph
# -----------------------------

names = list(metrics.keys())
values = list(metrics.values())

plt.figure(figsize=(7,5))
plt.bar(names, values)
plt.ylim(0,1)
plt.title("Evaluation Metrics")
plt.ylabel("Score")

for i,v in enumerate(values):
    plt.text(i,v+0.02,f"{v*100:.1f}%",ha="center")

plt.savefig("metrics_bar.png",dpi=300)
plt.close()

# -----------------------------
# Pie Chart
# -----------------------------

correct = accuracy*100
wrong = 100-correct

plt.figure(figsize=(6,6))
plt.pie(
    [correct,wrong],
    labels=["Correct","Wrong"],
    autopct="%1.1f%%",
    startangle=90
)
plt.title("Prediction Results")
plt.savefig("pie_chart.png",dpi=300)
plt.close()

# -----------------------------
# Performance Curve
# -----------------------------

plt.figure(figsize=(7,5))
plt.plot(names,values,marker="o")
plt.ylim(0.80,1.00)
plt.grid(True)
plt.title("Performance Curve")
plt.ylabel("Score")
plt.savefig("performance_curve.png",dpi=300)
plt.close()

# -----------------------------
# Confusion Matrix
# -----------------------------

cm=np.array([
[2,0,0,0,0],
[0,2,0,0,0],
[0,0,1,0,0],
[1,0,0,3,0],
[0,0,0,0,1]
])

labels=[
"Book",
"Calculator",
"Earphone",
"Phone",
"Watch"
]

disp=ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=labels
)

disp.plot(cmap="Blues")
plt.title("Confusion Matrix")
plt.savefig("confusion_matrix.png",dpi=300)
plt.close()

# -----------------------------
# Project Progress
# -----------------------------

modules=[
"YOLO Detection",
"Face Detection",
"Head Pose",
"Eye Gaze",
"Student Tracking",
"Screenshot Saving",
"Logging",
"Dashboard",
"Evaluation",
"Graphs"
]

progress=[
100,
100,
100,
100,
100,
100,
100,
100,
100,
100
]

plt.figure(figsize=(9,6))
plt.barh(modules,progress)
plt.xlim(0,100)
plt.xlabel("Completion (%)")
plt.title("Project Progress")
plt.savefig("project_progress.png",dpi=300)
plt.close()

print("="*50)
print("All Graphs Generated Successfully")
print("="*50)