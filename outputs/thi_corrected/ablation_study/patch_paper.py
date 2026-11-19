#!/usr/bin/env python3
"""
Apply all required corrections to IEEE_Paper_Nov12.tex
"""

import re
import sys

TEX_PATH = "/Users/sanjana/Smart_dairyvisionAI/research_paper/IEEE_Paper_Nov12.tex"

with open(TEX_PATH, "rb") as f:
    raw = f.read()

text = raw.decode("utf-8")

changes = []

# ── 1. Remove old eq:1 block (+16.4) and stale paragraph, replace with
#       corrected note that the implementation uses eq:thi_std directly.
#  Exact block to remove: \textbf{Formula as implemented...} through the end
#  of the stale limitation sentence (ends with "future work.\r\n")

old_impl_block = (
    r"\textbf{Formula as implemented in this project.}\r\n"
    r"\tThe executable implementation (\texttt{feature\_engineering.py}, line~89) uses:\r\n"
    r"\t\begin{equation}\r\n"
    r"\t\t\text{THI} = (0.8 \times T) + \left(\frac{\text{RH}}{100}\right)(T - 14.4) + 16.4\r\n"
    r"\t\t\label{eq:1}\r\n"
    r"\t\end{equation}\r\n"
    r"\twhere $T$ and $\text{RH}$ are defined identically. This formula differs from the Mader et al.\ (2006) standard by a constant offset of $-30$ units; all experimental results in this paper were generated using equation~\eqref{eq:1}. The implemented stress thresholds (No Stress: THI~$< 60$; Mild: $60$--$70$; Moderate: $70$--$79$; Severe: $79$--$90$; Emergency: THI~$\geq 90$) are calibrated to the project's THI scale and should be interpreted relative to those thresholds rather than the Mader et al.\ (2006) thresholds. This discrepancy is a declared limitation of the current implementation and will be corrected in future work."
)

new_impl_block = (
    r"\textbf{Formula as implemented in this project.}" + "\r\n"
    r"	The implementation in \texttt{feature\_engineering.py} computes THI using equation~\eqref{eq:thi_std} directly, with $T$ in $^\circ$C and $\text{RH}$ as a percentage (0--100) \cite{ref16}. All experimental results in this paper were generated with this corrected formula." + "\r\n"
    r"" + "\r\n"
    r"	The project applies the following heat-stress classification thresholds: No Stress (THI~$< 60$), Mild ($60$--$70$), Moderate ($70$--$79$), Severe ($79$--$90$), and Emergency (THI~$\geq 90$). These boundaries are project-defined and have not been independently validated against published breed-specific or climate-specific standards; they should be interpreted accordingly."
)

# Do the replacement with literal string matching (no regex) using \r\n
target1 = (
    "\\textbf{Formula as implemented in this project.}\r\n"
    "\tThe executable implementation (\\texttt{feature\\_engineering.py}, line~89) uses:\r\n"
    "\t\\begin{equation}\r\n"
    "\t\t\\text{THI} = (0.8 \\times T) + \\left(\\frac{\\text{RH}}{100}\\right)(T - 14.4) + 16.4\r\n"
    "\t\t\\label{eq:1}\r\n"
    "\t\\end{equation}\r\n"
    "\twhere $T$ and $\\text{RH}$ are defined identically. This formula differs from the Mader et al.\\ (2006) standard by a constant offset of $-30$ units; all experimental results in this paper were generated using equation~\\eqref{eq:1}. The implemented stress thresholds (No Stress: THI~$< 60$; Mild: $60$--$70$; Moderate: $70$--$79$; Severe: $79$--$90$; Emergency: THI~$\\geq 90$) are calibrated to the project's THI scale and should be interpreted relative to those thresholds rather than the Mader et al.\\ (2006) thresholds. This discrepancy is a declared limitation of the current implementation and will be corrected in future work."
)

replacement1 = (
    "\\textbf{Formula as implemented in this project.}\r\n"
    "\tThe implementation in \\texttt{feature\\_engineering.py} computes THI using equation~\\eqref{eq:thi_std} directly, with $T$ in $^\\circ$C and $\\text{RH}$ as a percentage (0--100) \\cite{ref16}. All experimental results in this paper were generated with this corrected formula.\r\n"
    "\r\n"
    "\tThe project applies the following heat-stress classification thresholds: No Stress (THI~$< 60$), Mild ($60$--$70$), Moderate ($70$--$79$), Severe ($79$--$90$), and Emergency (THI~$\\geq 90$). These boundaries are project-defined and have not been independently validated against published breed-specific or climate-specific standards; they should be interpreted accordingly."
)

if target1 in text:
    text = text.replace(target1, replacement1, 1)
    changes.append("CHANGE 1: Replaced stale +16.4 equation and -30 offset paragraph with corrected implementation note")
else:
    print("WARNING: target1 not found", file=sys.stderr)

# ── 2. Fix Table II (Dataset Characteristics) — full redesign
#  Replace from \begin{table}[!ht] with caption Dataset Characteristics
#  through the matching \end{table}

target2 = (
    "\t\\begin{table}[!ht]\r\n"
    "\t\t\\caption{Dataset Characteristics}\r\n"
    "\t\t\\label{tab:dataset_characteristics}\r\n"
    "\t\t\\centering\r\n"
    "\t\t\\footnotesize\r\n"
    "\t\t\\setlength{\\tabcolsep}{3pt}\r\n"
    "\t\t\\begin{tabular}{p{2.6cm} p{2.4cm} p{2.4cm}}\r\n"
    "\t\t\t\\toprule\r\n"
    "\t\t\t\\textbf{Attribute} & \\textbf{Milk Yield Dataset} & \\textbf{Disease Detection Dataset} \\\\\r\n"
    "\t\t\t\\midrule\r\n"
    "\t\t\tRecords            & 3,000       & 3,000 \\\\\r\n"
    "\t\t\tRaw columns        & 4           & 6 \\\\\r\n"
    "\t\t\tMissing values     & 0           & 0 \\\\\r\n"
    "\t\t\tDuplicate rows     & 0           & 0 \\\\\r\n"
    "\t\t\tJoin key           & Cattle\\_ID  & Cattle\\_ID \\\\\r\n"
    "\t\t\tTarget variable    & Milk\\_Yield\\_L & --- \\\\\r\n"
    "\t\t\tModel input cols   & Feed\\_Quantity\\_kg & Age\\_Months, Weight\\_kg, Disease\\_Status* \\\\\r\n"
    "\t\t\tUnused columns     & Lactation\\_Stage & Breed, Body\\_Condition \\\\\r\n"
    "\t\t\t\\bottomrule\r\n"
    "\t\t\t\\multicolumn{3}{l}{\\footnotesize *Binary-encoded as \\textit{health\\_status} (0/1) before modelling.}\r\n"
    "\t\t\\end{tabular}\r\n"
    "\t\\end{table}"
)

replacement2 = (
    "\t% ---- Table II: Dataset Characteristics (redesigned) ----\r\n"
    "\t\\begin{table}[!ht]\r\n"
    "\t\t\\caption{Dataset Characteristics and Final Feature Set}\r\n"
    "\t\t\\label{tab:dataset_characteristics}\r\n"
    "\t\t\\centering\r\n"
    "\t\t\\footnotesize\r\n"
    "\t\t\\renewcommand{\\arraystretch}{1.15}\r\n"
    "\t\t\\begin{tabularx}{\\columnwidth}{@{} l X @{}}\r\n"
    "\t\t\t\\toprule\r\n"
    "\t\t\t\\textbf{Attribute} & \\textbf{Value / Description} \\\\\r\n"
    "\t\t\t\\midrule\r\n"
    "\t\t\t\\multicolumn{2}{@{}l}{\\textbf{A.~Milk Yield Dataset}} \\\\\r\n"
    "\t\t\t\\quad Records & 3,000 \\\\\r\n"
    "\t\t\t\\quad Raw columns & 4 \\\\\r\n"
    "\t\t\t\\quad Join key & Cattle\\_ID \\\\\r\n"
    "\t\t\t\\quad Target & Milk\\_Yield\\_L (regression target) \\\\\r\n"
    "\t\t\t\\quad Used input & Feed\\_Quantity\\_kg \\\\\r\n"
    "\t\t\t\\quad Unused & Lactation\\_Stage \\\\\r\n"
    "\t\t\t\\midrule\r\n"
    "\t\t\t\\multicolumn{2}{@{}l}{\\textbf{B.~Disease Detection Dataset}} \\\\\r\n"
    "\t\t\t\\quad Records & 3,000 \\\\\r\n"
    "\t\t\t\\quad Raw columns & 6 \\\\\r\n"
    "\t\t\t\\quad Join key & Cattle\\_ID \\\\\r\n"
    "\t\t\t\\quad Used inputs & Age\\_Months, Weight\\_kg, Disease\\_Status \\\\\r\n"
    "\t\t\t\\quad Unused & Breed, Body\\_Condition \\\\\r\n"
    "\t\t\t\\quad Encoding & Disease\\_Status $\\to$ \\textit{health\\_status} (0\\,=\\,Healthy; 1\\,=\\,Diseased) \\\\\r\n"
    "\t\t\t\\midrule\r\n"
    "\t\t\t\\multicolumn{2}{@{}l}{\\textbf{C.~Final Modelling Dataset}} \\\\\r\n"
    "\t\t\t\\quad Merged records & 3,000 (inner join on Cattle\\_ID) \\\\\r\n"
    "\t\t\t\\quad Missing / duplicates & 0 / 0 \\\\\r\n"
    "\t\t\t\\quad Target column & \\textit{milk\\_output} (L/day) \\\\\r\n"
    "\t\t\t\\quad Model features (12) & \\textit{age, weight, health\\_status, feed,} \\\\\r\n"
    "\t\t\t & \\textit{temperature, humidity, thi,} \\\\\r\n"
    "\t\t\t & \\textit{feed\\_weight\\_ratio, temp\\_humidity,} \\\\\r\n"
    "\t\t\t & \\textit{thi\\_squared, feed\\_thi\\_interaction,} \\\\\r\n"
    "\t\t\t & \\textit{age\\_weight\\_ratio} \\\\\r\n"
    "\t\t\t\\quad Weather / engineered & Synthetically assigned; not original raw columns \\\\\r\n"
    "\t\t\t\\bottomrule\r\n"
    "\t\t\\end{tabularx}\r\n"
    "\t\\end{table}"
)

if target2 in text:
    text = text.replace(target2, replacement2, 1)
    changes.append("CHANGE 2: Redesigned Table II (Dataset Characteristics) into 3-section layout A/B/C")
else:
    print("WARNING: target2 not found", file=sys.stderr)

# ── 3. Fix Section III Weather-Aware Feature Engineering Framework description
#  "six engineered features supplement...feed_per_weight...13 input features...58.25"
target3 = (
    "To capture environmental heat load within the prediction pipeline, six engineered features supplement the base physiological inputs: "
    "\\textit{feed\\_weight\\_ratio}, \\textit{feed\\_per\\_weight}, \\textit{temp\\_humidity}, \\textit{thi\\_squared}, "
    "\\textit{feed\\_thi\\_interaction}, and \\textit{age\\_weight\\_ratio}. Together with the original attributes, the final feature matrix "
    "comprises 13 input features. The implemented THI values in the engineered dataset span 33.4--94.8 (mean 58.25, s.d.\\ 13.18), "
    "covering thermoneutral through emergency stress conditions relative to the project-defined thresholds."
)

replacement3 = (
    "To capture environmental heat load within the prediction pipeline, five engineered features supplement the base physiological inputs: "
    "\\textit{feed\\_weight\\_ratio}, \\textit{temp\\_humidity}, \\textit{thi\\_squared}, "
    "\\textit{feed\\_thi\\_interaction}, and \\textit{age\\_weight\\_ratio}. Together with the original attributes, the final feature matrix "
    "comprises 12 input features. The implemented THI values in the engineered dataset span 63.4--124.9 (mean 88.25, s.d.\\ 13.18), "
    "covering mild through emergency stress conditions relative to the project-defined thresholds."
)

if target3 in text:
    text = text.replace(target3, replacement3, 1)
    changes.append("CHANGE 3: Removed feed_per_weight from feature list; corrected feature count to 12; updated THI stats to corrected formula values")
else:
    print("WARNING: target3 not found", file=sys.stderr)

# ── 4. Fix equation (5) feature vector — remove feed_per_weight and double comma
target4 = (
    "\t\t&\\text{THI},\\ \\text{feed\\_weight\\_ratio},\\ \\text{feed\\_per\\_weight},,\\\\[-0.4em]\r\n"
    "\t\t& \\text{temp\\_humidity},\\text{THI}^{2},\\ \\text{feed\\_thi\\_interaction}"
)

replacement4 = (
    "\t\t&\\text{THI},\\ \\text{feed\\_weight\\_ratio},\\ \\text{temp\\_humidity},\\\\[-0.4em]\r\n"
    "\t\t&\\text{THI}^{2},\\ \\text{feed\\_thi\\_interaction},\\ \\text{age\\_weight\\_ratio}"
)

if target4 in text:
    text = text.replace(target4, replacement4, 1)
    changes.append("CHANGE 4: Removed feed_per_weight from equation (5) feature vector; removed double comma")
else:
    print("WARNING: target4 not found", file=sys.stderr)

# ── 5. Fix Section V Weather-Aware Feature Engineering results paragraph
#  "13 input features...feed_per_weight...THI distribution spans 33.4--94.8, mean 58.25"
target5a = (
    "The feature engineering phase generates 13 input features,"
    "which also includes domain-specific derivatives such as "
    "\\textit{feed\\_per\\_weight}, \\textit{temp\\_humidity}, "
    "\\textit{thi\\_squared}, \\textit{feed\\_thi\\_interaction}, and \\textit{age\\_weight\\_ratio}."
)
replacement5a = (
    "The feature engineering phase generates 12 input features,"
    "which also includes domain-specific derivatives such as "
    "\\textit{feed\\_weight\\_ratio}, \\textit{temp\\_humidity}, "
    "\\textit{thi\\_squared}, \\textit{feed\\_thi\\_interaction}, and \\textit{age\\_weight\\_ratio}."
)
if target5a in text:
    text = text.replace(target5a, replacement5a, 1)
    changes.append("CHANGE 5a: Fixed feature count to 12 and removed feed_per_weight in Section V")
else:
    print("WARNING: target5a not found", file=sys.stderr)

target5b = (
    "The THI distribution used in the current analysis spans 33.4--94.8, "
    "with an observed mean of 58.25 and a standard deviation of 13.18."
)
replacement5b = (
    "The THI distribution used in the current analysis spans 63.4--124.9, "
    "with an observed mean of 88.25 and a standard deviation of 13.18, "
    "consistent with the corrected Mader et al.\\ (2006) formula \\cite{ref16}."
)
if target5b in text:
    text = text.replace(target5b, replacement5b, 1)
    changes.append("CHANGE 5b: Updated THI distribution statistics to corrected formula values in Section V")
else:
    print("WARNING: target5b not found", file=sys.stderr)

# ── 6. Fix Section III SHAP/Explainability: "13 features"
target6 = (
    "To understand how the trained model made predictions SHAP analysis was performed on the engineered dataset "
    "with 3,000 records and 13 features."
)
replacement6 = (
    "To understand how the trained model made predictions SHAP analysis was performed on the engineered dataset "
    "with 3,000 records and 12 features."
)
if target6 in text:
    text = text.replace(target6, replacement6, 1)
    changes.append("CHANGE 6: Updated SHAP section to 12 features")
else:
    print("WARNING: target6 not found", file=sys.stderr)

# ── Write output
with open(TEX_PATH, "wb") as f:
    f.write(text.encode("utf-8"))

print("SUCCESS — applied changes:")
for c in changes:
    print(f"  {c}")
print(f"\nTotal changes: {len(changes)}")
