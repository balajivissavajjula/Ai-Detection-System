from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# -------------------------------------
# Ground Truth
# -------------------------------------

y_true = [
    "phone",
    "phone",
    "book",
    "calculator",
    "phone",
    "watch",
    "book",
    "earphone",
    "phone",
    "calculator"
]

# -------------------------------------
# Model Prediction
# -------------------------------------

y_pred = [
    "phone",
    "phone",
    "book",
    "calculator",
    "book",
    "watch",
    "book",
    "earphone",
    "phone",
    "calculator"
]

# -------------------------------------
# Metrics
# -------------------------------------

print("="*50)

print("Accuracy :",
      accuracy_score(y_true, y_pred))

print("Precision :",
      precision_score(
          y_true,
          y_pred,
          average="weighted"
      ))

print("Recall :",
      recall_score(
          y_true,
          y_pred,
          average="weighted"
      ))

print("F1 Score :",
      f1_score(
          y_true,
          y_pred,
          average="weighted"
      ))

print("="*50)

print(classification_report(y_true, y_pred))

print("="*50)

print("Confusion Matrix")

print(confusion_matrix(y_true, y_pred))