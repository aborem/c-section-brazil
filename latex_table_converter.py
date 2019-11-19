import json

f1 = open("findings/ratios.txt", "r")
f2 = open("findings/summaries.txt", "r")

# Process summaries
summaries = f2.readlines()
f2.close()
escmaes = [line[49:55] for line in summaries if line[:6] == "ESCMAE"]
racacors = [line[49:55] for line in summaries if line[:7] == "RACACOR"]

ratio_data = json.load(f1)
f1.close()

i = 0

beginning = """
\\begin{table}[h!]
\caption{Birth demographics and statistics for the state of Acre after January 2017.}
\label{tab:acre}
\\begin{tabular}{lllllllll}
\hline
\multicolumn{2}{l}{\\textbf{Characteristics}} & \multicolumn{4}{l}{\\textbf{C-Section}} & \multicolumn{2}{l}{\\textbf{Total}} & \\textit{\\textbf{p}} \\ \cline{3-6}
 &  & \multicolumn{2}{l}{Yes} & \multicolumn{2}{l}{No} &  &  &  \\ \cline{3-9} 
 &  & n & \% & n & \% & n & \% &  \\\\ \hline
"""

end = """
\end{tabular}
\end{table}
"""

for state, data in ratio_data.items():
    race_data = data["Race"]
    lines = []
    for race, specific_race_data in race_data.items():
        y, yp, n, np, t, tp = specific_race_data["y"], specific_race_data["y%"], specific_race_data["n"], \
                              specific_race_data["n%"], specific_race_data["t"], specific_race_data["t%"]
        single_line = f"& {race} & {y} & {yp} & {n} & {np} & {t} & {tp} & \\\\"
        lines.append(single_line)
    lines[0] = "\multirow{5}{*}{Race} " + lines[0][:-2] + "\multirow{5}{*}{" + racacors[i] + "} \\\\"
    educ_data = data["Education"]
    educ_lines = []
    for educ, specific_educ_data in educ_data.items():
        y, yp, n, np, t, tp = specific_educ_data["y"], specific_educ_data["y%"], specific_educ_data["n"], \
                              specific_educ_data["n%"], specific_educ_data["t"], specific_educ_data["t%"]
        single_line = f"& {educ} & {y} & {yp} & {n} & {np} & {t} & {tp} & \\\\"
        educ_lines.append(single_line)
    educ_lines[0] = "\multirow{3}{*}{Education} " + educ_lines[0][:-2] + "\multirow{3}{*}{" + escmaes[i] + "} \\\\"
    educ_lines[-1] += " \hline"

    all_lines = lines + educ_lines
    table_all = '\n'.join(all_lines)
    print(beginning + table_all + end)
    print(f'\n\n')
    i += 1
