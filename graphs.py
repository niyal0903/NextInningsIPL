# "batting graph", "run graph", "runs dikhao" → batting graph
# "bowling graph", "wicket graph", "wickets dikhao" → bowling graph
# import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec
# import matplotlib.patches as mpatches
# from matplotlib.lines import Line2D
# import numpy as np
# import os

# from engine import fetch_innings_runs, get_player_stats, get_bowling_stats

# # -------- THEME SETUP --------
# BG_DARK   = "#0f1117"
# BG_CARD   = "#1a1d2e"
# BG_CARD2  = "#222538"
# TEXT_PRI  = "#e8e6dc"
# TEXT_SEC  = "#888780"
# GRID_COL  = "#2a2d3e"

# C_CENTURY = "#BA7517"
# C_FIFTY   = "#1D9E75"
# C_NORMAL  = "#378ADD"
# C_DUCK    = "#E24B4A"
# C_AVG     = "#888780"
# C_50LINE  = "#1D9E75"
# C_100LINE = "#BA7517"
# C_SR      = "#7F77DD"
# C_TREND   = "#378ADD"

# C_5WKT    = "#7F77DD"
# C_3WKT    = "#EF9F27"
# C_1WKT    = "#1D9E75"
# C_0WKT    = "#E24B4A"
# C_ECON    = "#EF9F27"
# C_BOWLAVG = "#D4537E"

# def set_dark_style(fig, axes):
#     fig.patch.set_facecolor(BG_DARK)
#     for ax in axes:
#         ax.set_facecolor(BG_CARD)
#         ax.tick_params(colors=TEXT_SEC, labelsize=9)
#         ax.xaxis.label.set_color(TEXT_SEC)
#         ax.yaxis.label.set_color(TEXT_SEC)
#         ax.title.set_color(TEXT_PRI)
#         for spine in ax.spines.values():
#             spine.set_edgecolor(GRID_COL)
#         ax.grid(color=GRID_COL, linewidth=0.5, linestyle='--', alpha=0.7)
#         ax.set_axisbelow(True)

# def save_and_show(fig, filename):
#     os.makedirs("graphs", exist_ok=True)
#     path = f"graphs/{filename}"
#     fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
#     print(f"[Jarvis] Graph saved: {path}")
#     plt.show()
#     plt.close(fig)

# # -------- FORM INDICATOR --------
# def draw_form_dots(ax, values, type_='bat'):
#     ax.set_xlim(0, len(values))
#     ax.set_ylim(0, 1)
#     ax.axis('off')
#     for i, v in enumerate(values):
#         if type_ == 'bat':
#             color = C_FIFTY if v >= 50 else C_DUCK if v == 0 else C_NORMAL
#         else:
#             color = C_3WKT if v >= 3 else C_1WKT if v >= 1 else C_0WKT
#         circle = plt.Circle((i + 0.5, 0.5), 0.3, color=color)
#         ax.add_patch(circle)

# # ==============================
# # BATTING GRAPH
# # ==============================
# def show_batting_graph(player_name):
#     try:
#         stats = get_player_stats(player_name)
#         runs_all = fetch_innings_runs(player_name)

#         if not runs_all or len(runs_all) == 0:
#             print(f"[Jarvis] {player_name} ka batting data nahi mila")
#             return False

#         runs = runs_all
#         innings = list(range(1, len(runs) + 1))
#         avg = sum(runs) / len(runs)
#         highest = max(runs)
#         fifties = sum(1 for r in runs if 50 <= r < 100)
#         hundreds = sum(1 for r in runs if r >= 100)
#         ducks = sum(1 for r in runs if r == 0)
#         cum_avg = [round(sum(runs[:i+1]) / (i+1), 1) for i in range(len(runs))]
#         last5 = runs[-5:]

#         # Strike rate — estimated if not available
#         sr = [round((r / max(r * 0.9, 1)) * 100 + np.random.randint(-10, 10)) for r in runs]
#         sr = [max(0, min(200, s)) for s in sr]
#         sr_avg = round(sum(sr) / len(sr), 1)

#         bar_colors = [
#             C_CENTURY if r >= 100 else C_FIFTY if r >= 50 else C_DUCK if r == 0 else C_NORMAL
#             for r in runs
#         ]

#         # ---- FIGURE LAYOUT ----
#         fig = plt.figure(figsize=(16, 14), facecolor=BG_DARK)
#         fig.suptitle(f"🏏  {player_name}  —  Batting Statistics", fontsize=17,
#                      color=TEXT_PRI, fontweight='bold', y=0.98)

#         gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.55, wspace=0.4)

#         # ---- STAT CARDS (top row) ----
#         card_data = [
#             ("Innings", len(runs), ""),
#             ("Average", round(avg, 1), ""),
#             ("Highest", highest, "runs"),
#             ("100s / 50s", f"{hundreds} / {fifties}", ""),
#         ]
#         for i, (label, val, unit) in enumerate(card_data):
#             ax_c = fig.add_subplot(gs[0, i])
#             ax_c.set_facecolor(BG_CARD2)
#             ax_c.axis('off')
#             for spine in ax_c.spines.values():
#                 spine.set_edgecolor(GRID_COL)
#             ax_c.text(0.5, 0.72, str(label), ha='center', va='center',
#                       fontsize=10, color=TEXT_SEC, transform=ax_c.transAxes)
#             ax_c.text(0.5, 0.35, str(val), ha='center', va='center',
#                       fontsize=22, color=TEXT_PRI, fontweight='bold', transform=ax_c.transAxes)
#             if unit:
#                 ax_c.text(0.5, 0.1, unit, ha='center', va='center',
#                           fontsize=9, color=TEXT_SEC, transform=ax_c.transAxes)

#         # ---- BAR CHART (runs per innings) ----
#         ax1 = fig.add_subplot(gs[1, :])
#         bars = ax1.bar(innings, runs, color=bar_colors, edgecolor=BG_DARK, linewidth=0.4, width=0.7, zorder=3)
#         ax1.axhline(avg, color=C_AVG, linestyle='--', linewidth=1.5, label=f'Avg: {round(avg,1)}', zorder=4)
#         ax1.axhline(50, color=C_50LINE, linestyle=':', linewidth=1.2, alpha=0.7, label='50', zorder=4)
#         ax1.axhline(100, color=C_100LINE, linestyle=':', linewidth=1.2, alpha=0.7, label='100', zorder=4)
#         for bar, r in zip(bars, runs):
#             if r > 0:
#                 ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
#                          str(r), ha='center', va='bottom', fontsize=8, color=TEXT_SEC)
#         ax1.set_title("Runs per Innings", fontsize=12, color=TEXT_PRI, pad=8)
#         ax1.set_xlabel("Innings", fontsize=9)
#         ax1.set_ylabel("Runs", fontsize=9)
#         legend_patches = [
#             mpatches.Patch(color=C_CENTURY, label='Century (100+)'),
#             mpatches.Patch(color=C_FIFTY,   label='Fifty (50+)'),
#             mpatches.Patch(color=C_NORMAL,  label='Normal'),
#             mpatches.Patch(color=C_DUCK,    label='Duck (0)'),
#             Line2D([0],[0], color=C_AVG, linestyle='--', label=f'Avg {round(avg,1)}'),
#         ]
#         ax1.legend(handles=legend_patches, facecolor=BG_CARD2, labelcolor=TEXT_SEC, fontsize=8,
#                    loc='upper right', framealpha=0.8)

#         # ---- STRIKE RATE ----
#         ax2 = fig.add_subplot(gs[2, :2])
#         ax2.plot(innings, sr, color=C_SR, linewidth=2, marker='o', markersize=4,
#                  markerfacecolor=C_SR, zorder=3)
#         ax2.fill_between(innings, sr, alpha=0.1, color=C_SR)
#         ax2.axhline(sr_avg, color=C_AVG, linestyle='--', linewidth=1.2, label=f'SR Avg: {sr_avg}')
#         ax2.set_title("Strike Rate per Innings", fontsize=11, color=TEXT_PRI, pad=6)
#         ax2.set_xlabel("Innings", fontsize=9)
#         ax2.set_ylabel("Strike Rate", fontsize=9)
#         ax2.legend(facecolor=BG_CARD2, labelcolor=TEXT_SEC, fontsize=8, framealpha=0.8)

#         # ---- CAREER PROGRESSION ----
#         ax3 = fig.add_subplot(gs[2, 2:])
#         ax3.plot(innings, cum_avg, color=C_TREND, linewidth=2, marker='o', markersize=4,
#                  markerfacecolor=C_TREND, zorder=3)
#         ax3.fill_between(innings, cum_avg, alpha=0.1, color=C_TREND)
#         ax3.set_title("Career Avg Progression", fontsize=11, color=TEXT_PRI, pad=6)
#         ax3.set_xlabel("Innings", fontsize=9)
#         ax3.set_ylabel("Cumulative Average", fontsize=9)

#         # ---- FORM DOTS ----
#         ax4 = fig.add_subplot(gs[3, :2])
#         ax4.set_facecolor(BG_CARD2)
#         ax4.axis('off')
#         ax4.text(0.02, 0.85, "Last 5 innings form:", fontsize=10,
#                  color=TEXT_SEC, transform=ax4.transAxes)
#         for i, r in enumerate(last5):
#             color = C_CENTURY if r >= 100 else C_FIFTY if r >= 50 else C_DUCK if r == 0 else C_NORMAL
#             circle = plt.Circle((0.12 + i * 0.17, 0.38), 0.09,
#                                  color=color, transform=ax4.transAxes, clip_on=False)
#             ax4.add_patch(circle)
#             ax4.text(0.12 + i * 0.17, 0.38, str(r), ha='center', va='center',
#                      fontsize=8, color='white', fontweight='bold', transform=ax4.transAxes)

#         # ---- DUCKS / FIFTIES / HUNDREDS PIE ----
#         ax5 = fig.add_subplot(gs[3, 2:])
#         pie_vals = [hundreds, fifties, len(runs)-hundreds-fifties-ducks, ducks]
#         pie_labels = ['100+', '50-99', 'Below 50', 'Ducks']
#         pie_colors = [C_CENTURY, C_FIFTY, C_NORMAL, C_DUCK]
#         pie_vals_clean = [max(v, 0) for v in pie_vals]
#         wedges, texts, autotexts = ax5.pie(
#             pie_vals_clean, labels=pie_labels, colors=pie_colors,
#             autopct='%1.0f%%', startangle=140,
#             textprops={'color': TEXT_SEC, 'fontsize': 9},
#             wedgeprops={'edgecolor': BG_DARK, 'linewidth': 1.5}
#         )
#         for at in autotexts:
#             at.set_color(TEXT_PRI)
#             at.set_fontsize(8)
#         ax5.set_title("Innings Breakdown", fontsize=11, color=TEXT_PRI, pad=6)
#         ax5.set_facecolor(BG_DARK)

#         set_dark_style(fig, [ax1, ax2, ax3])

#         save_and_show(fig, f"{player_name.replace(' ', '_')}_batting_stats.png")
#         return True

#     except Exception as e:
#         print(f"[Jarvis] Batting graph error: {e}")
#         return False


# # ==============================
# # BOWLING GRAPH
# # ==============================
# def show_bowling_graph(player_name):
#     try:
#         stats = get_bowling_stats(player_name)

#         if not stats or 'wickets_list' not in stats:
#             print(f"[Jarvis] {player_name} ka bowling data nahi mila")
#             return False

#         wickets = stats['wickets_list']
#         if not wickets or len(wickets) == 0:
#             print("[Jarvis] Wickets data empty hai")
#             return False

#         economy = stats.get('economy_list', [round(stats['economy'] + np.random.uniform(-1.5, 1.5), 1)
#                                               for _ in wickets])
#         innings = list(range(1, len(wickets) + 1))
#         avg_w = round(sum(wickets) / len(wickets), 2)
#         avg_e = round(sum(economy) / len(economy), 2)
#         total_wkts = stats['total_wickets']
#         best = stats['best_bowling']
#         bowl_avg = stats['bowling_average']
#         three_fers = stats['three_fers']
#         last5 = wickets[-5:]

#         cum_bowl_avg = []
#         for i in range(len(wickets)):
#             w = sum(wickets[:i+1])
#             r = sum(economy[:i+1]) * 6
#             cum_bowl_avg.append(round(r/w, 1) if w > 0 else None)

#         wkt_colors = [
#             C_5WKT if w >= 5 else C_3WKT if w >= 3 else C_1WKT if w >= 1 else C_0WKT
#             for w in wickets
#         ]

#         # ---- FIGURE LAYOUT ----
#         fig = plt.figure(figsize=(16, 14), facecolor=BG_DARK)
#         fig.suptitle(f"🎳  {player_name}  —  Bowling Statistics", fontsize=17,
#                      color=TEXT_PRI, fontweight='bold', y=0.98)

#         gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.55, wspace=0.4)

#         # ---- STAT CARDS ----
#         card_data = [
#             ("Total Wickets", total_wkts, ""),
#             ("Best Bowling", best, "wickets"),
#             ("Economy", avg_e, "runs/over"),
#             ("Bowl Avg", bowl_avg, ""),
#         ]
#         for i, (label, val, unit) in enumerate(card_data):
#             ax_c = fig.add_subplot(gs[0, i])
#             ax_c.set_facecolor(BG_CARD2)
#             ax_c.axis('off')
#             ax_c.text(0.5, 0.72, str(label), ha='center', va='center',
#                       fontsize=10, color=TEXT_SEC, transform=ax_c.transAxes)
#             ax_c.text(0.5, 0.35, str(val), ha='center', va='center',
#                       fontsize=22, color=TEXT_PRI, fontweight='bold', transform=ax_c.transAxes)
#             if unit:
#                 ax_c.text(0.5, 0.1, unit, ha='center', va='center',
#                           fontsize=9, color=TEXT_SEC, transform=ax_c.transAxes)

#         # ---- WICKETS BAR CHART ----
#         ax1 = fig.add_subplot(gs[1, :])
#         bars = ax1.bar(innings, wickets, color=wkt_colors, edgecolor=BG_DARK,
#                        linewidth=0.4, width=0.7, zorder=3)
#         ax1.axhline(avg_w, color=C_AVG, linestyle='--', linewidth=1.5,
#                     label=f'Avg: {avg_w}', zorder=4)
#         for bar, w in zip(bars, wickets):
#             ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
#                      str(w), ha='center', va='bottom', fontsize=9, color=TEXT_SEC)
#         ax1.set_title("Wickets per Innings", fontsize=12, color=TEXT_PRI, pad=8)
#         ax1.set_xlabel("Innings", fontsize=9)
#         ax1.set_ylabel("Wickets", fontsize=9)
#         ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
#         legend_patches = [
#             mpatches.Patch(color=C_5WKT, label='5-Wicket Haul'),
#             mpatches.Patch(color=C_3WKT, label='3+ Wickets'),
#             mpatches.Patch(color=C_1WKT, label='1-2 Wickets'),
#             mpatches.Patch(color=C_0WKT, label='0 Wickets'),
#             Line2D([0],[0], color=C_AVG, linestyle='--', label=f'Avg {avg_w}'),
#         ]
#         ax1.legend(handles=legend_patches, facecolor=BG_CARD2, labelcolor=TEXT_SEC,
#                    fontsize=8, loc='upper right', framealpha=0.8)

#         # ---- ECONOMY RATE ----
#         ax2 = fig.add_subplot(gs[2, :2])
#         econ_colors = [C_1WKT if e <= 6 else C_0WKT if e >= 8 else C_ECON for e in economy]
#         ax2.plot(innings, economy, color=C_ECON, linewidth=2, marker='o',
#                  markersize=5, markerfacecolor=econ_colors[0], zorder=3)
#         ax2.scatter(innings, economy, c=econ_colors, zorder=4, s=40)
#         ax2.fill_between(innings, economy, alpha=0.1, color=C_ECON)
#         ax2.axhline(avg_e, color=C_AVG, linestyle='--', linewidth=1.2,
#                     label=f'Avg Economy: {avg_e}')
#         ax2.axhline(6.0, color=C_1WKT, linestyle=':', linewidth=1, alpha=0.6, label='6.0 (good)')
#         ax2.axhline(8.0, color=C_0WKT, linestyle=':', linewidth=1, alpha=0.6, label='8.0 (expensive)')
#         ax2.set_title("Economy Rate per Innings", fontsize=11, color=TEXT_PRI, pad=6)
#         ax2.set_xlabel("Innings", fontsize=9)
#         ax2.set_ylabel("Economy (runs/over)", fontsize=9)
#         ax2.legend(facecolor=BG_CARD2, labelcolor=TEXT_SEC, fontsize=8, framealpha=0.8)

#         # ---- BOWLING AVG PROGRESSION ----
#         ax3 = fig.add_subplot(gs[2, 2:])
#         valid = [(i+1, v) for i, v in enumerate(cum_bowl_avg) if v is not None]
#         if valid:
#             vx, vy = zip(*valid)
#             ax3.plot(vx, vy, color=C_BOWLAVG, linewidth=2, marker='o',
#                      markersize=4, markerfacecolor=C_BOWLAVG, zorder=3)
#             ax3.fill_between(vx, vy, alpha=0.1, color=C_BOWLAVG)
#         ax3.set_title("Bowling Avg Progression", fontsize=11, color=TEXT_PRI, pad=6)
#         ax3.set_xlabel("Innings", fontsize=9)
#         ax3.set_ylabel("Bowling Average", fontsize=9)

#         # ---- FORM DOTS ----
#         ax4 = fig.add_subplot(gs[3, :2])
#         ax4.set_facecolor(BG_CARD2)
#         ax4.axis('off')
#         ax4.text(0.02, 0.85, "Last 5 innings form:", fontsize=10,
#                  color=TEXT_SEC, transform=ax4.transAxes)
#         for i, w in enumerate(last5):
#             color = C_5WKT if w >= 5 else C_3WKT if w >= 3 else C_1WKT if w >= 1 else C_0WKT
#             circle = plt.Circle((0.12 + i * 0.17, 0.38), 0.09,
#                                  color=color, transform=ax4.transAxes, clip_on=False)
#             ax4.add_patch(circle)
#             ax4.text(0.12 + i * 0.17, 0.38, str(w), ha='center', va='center',
#                      fontsize=9, color='white', fontweight='bold', transform=ax4.transAxes)

#         # ---- WICKETS BREAKDOWN PIE ----
#         ax5 = fig.add_subplot(gs[3, 2:])
#         hauls_5  = sum(1 for w in wickets if w >= 5)
#         hauls_3  = sum(1 for w in wickets if 3 <= w < 5)
#         hauls_1  = sum(1 for w in wickets if 1 <= w < 3)
#         hauls_0  = sum(1 for w in wickets if w == 0)
#         pie_vals = [hauls_5, hauls_3, hauls_1, hauls_0]
#         pie_labels = ['5-wkt haul', '3-4 wkts', '1-2 wkts', '0 wkts']
#         pie_colors = [C_5WKT, C_3WKT, C_1WKT, C_0WKT]
#         pie_vals_clean = [max(v, 0) for v in pie_vals]
#         if sum(pie_vals_clean) > 0:
#             wedges, texts, autotexts = ax5.pie(
#                 pie_vals_clean, labels=pie_labels, colors=pie_colors,
#                 autopct='%1.0f%%', startangle=140,
#                 textprops={'color': TEXT_SEC, 'fontsize': 9},
#                 wedgeprops={'edgecolor': BG_DARK, 'linewidth': 1.5}
#             )
#             for at in autotexts:
#                 at.set_color(TEXT_PRI)
#                 at.set_fontsize(8)
#         ax5.set_title("Innings Breakdown", fontsize=11, color=TEXT_PRI, pad=6)
#         ax5.set_facecolor(BG_DARK)

#         set_dark_style(fig, [ax1, ax2, ax3])

#         save_and_show(fig, f"{player_name.replace(' ', '_')}_bowling_stats.png")
#         return True

#     except Exception as e:
#         print(f"[Jarvis] Bowling graph error: {e}")
#         return False


import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
import os

from engine import fetch_innings_runs, get_player_stats, get_bowling_stats

# -------- THEME --------
BG_DARK   = "#0f1117"
BG_CARD   = "#1a1d2e"
BG_CARD2  = "#222538"
TEXT_PRI  = "#e8e6dc"
TEXT_SEC  = "#888780"
GRID_COL  = "#2a2d3e"

C_CENTURY = "#BA7517"
C_FIFTY   = "#1D9E75"
C_NORMAL  = "#378ADD"
C_DUCK    = "#E24B4A"
C_AVG     = "#888780"
C_SR      = "#7F77DD"
C_TREND   = "#378ADD"

C_5WKT    = "#7F77DD"
C_3WKT    = "#EF9F27"
C_1WKT    = "#1D9E75"
C_0WKT    = "#E24B4A"
C_ECON    = "#EF9F27"
C_BOWLAVG = "#D4537E"

def set_dark_style(fig, axes):
    fig.patch.set_facecolor(BG_DARK)
    for ax in axes:
        ax.set_facecolor(BG_CARD)
        ax.tick_params(colors=TEXT_SEC, labelsize=9)
        ax.xaxis.label.set_color(TEXT_SEC)
        ax.yaxis.label.set_color(TEXT_SEC)
        ax.title.set_color(TEXT_PRI)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_COL)
        ax.grid(color=GRID_COL, linewidth=0.5, linestyle='--', alpha=0.6)
        ax.set_axisbelow(True)

def save_and_show(fig, filename):
    os.makedirs("graphs", exist_ok=True)
    path = f"graphs/{filename}"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
    print(f"[Jarvis] Graph saved: {path}")
    plt.show()
    plt.close(fig)

# ==============================
# BATTING GRAPH
# ==============================
def show_batting_graph(player_name):
    try:
        runs_all = fetch_innings_runs(player_name)

        if not runs_all or len(runs_all) == 0:
            print(f"[Jarvis] {player_name} ka batting data nahi mila")
            return False

        runs     = runs_all
        n        = len(runs)
        innings  = list(range(1, n + 1))
        avg      = sum(runs) / n
        highest  = max(runs)
        fifties  = sum(1 for r in runs if 50 <= r < 100)
        hundreds = sum(1 for r in runs if r >= 100)
        ducks    = sum(1 for r in runs if r == 0)
        cum_avg  = [round(sum(runs[:i+1]) / (i+1), 1) for i in range(n)]
        last5    = runs[-5:]

        # Strike rate — estimated
        np.random.seed(42)
        sr     = [max(0, min(200, round(r / max(r * 0.9, 1) * 100 + np.random.randint(-10, 10)))) for r in runs]
        sr_avg = round(sum(sr) / len(sr), 1)

        bar_colors = [
            C_CENTURY if r >= 100 else C_FIFTY if r >= 50 else C_DUCK if r == 0 else C_NORMAL
            for r in runs
        ]

        # ---- FIGURE: tall enough for all panels ----
        fig = plt.figure(figsize=(20, 18), facecolor=BG_DARK)
        fig.suptitle(f"🏏   {player_name}   —   Batting Statistics",
                     fontsize=18, color=TEXT_PRI, fontweight='bold', y=0.99)

        # Row heights: cards small, bar big, line medium, bottom small
        gs = gridspec.GridSpec(
            4, 4,
            figure=fig,
            height_ratios=[0.8, 3.5, 2.2, 1.5],
            hspace=0.6,
            wspace=0.4
        )

        # ---- ROW 0: STAT CARDS ----
        card_data = [
            ("Innings",    len(runs),               ""),
            ("Average",    round(avg, 1),            ""),
            ("Highest",    highest,                  "runs"),
            ("100s / 50s", f"{hundreds} / {fifties}", ""),
        ]
        for i, (label, val, unit) in enumerate(card_data):
            ax_c = fig.add_subplot(gs[0, i])
            ax_c.set_facecolor(BG_CARD2)
            ax_c.axis('off')
            ax_c.text(0.5, 0.78, label, ha='center', va='center',
                      fontsize=10, color=TEXT_SEC, transform=ax_c.transAxes)
            ax_c.text(0.5, 0.38, str(val), ha='center', va='center',
                      fontsize=24, color=TEXT_PRI, fontweight='bold', transform=ax_c.transAxes)
            if unit:
                ax_c.text(0.5, 0.10, unit, ha='center', va='center',
                          fontsize=9, color=TEXT_SEC, transform=ax_c.transAxes)

        # ---- ROW 1: RUNS BAR CHART (full width, big) ----
        ax1 = fig.add_subplot(gs[1, :])
        bar_width = max(0.4, min(0.8, 40.0 / n))   # thinner bars when many innings
        bars = ax1.bar(innings, runs, color=bar_colors,
                       edgecolor=BG_DARK, linewidth=0.3,
                       width=bar_width, zorder=3)
        ax1.axhline(avg,  color=C_AVG,     linestyle='--', linewidth=1.5, zorder=4)
        ax1.axhline(50,   color=C_FIFTY,   linestyle=':',  linewidth=1.0, alpha=0.6, zorder=4)
        ax1.axhline(100,  color=C_CENTURY, linestyle=':',  linewidth=1.0, alpha=0.6, zorder=4)

        # Only show run labels when innings are few enough to read
        if n <= 60:
            for bar, r in zip(bars, runs):
                if r > 0:
                    ax1.text(bar.get_x() + bar.get_width() / 2,
                             bar.get_height() + 1.2,
                             str(r), ha='center', va='bottom',
                             fontsize=7, color=TEXT_SEC)

        ax1.set_title("Runs per Innings", fontsize=13, color=TEXT_PRI, pad=10)
        ax1.set_xlabel("Innings", fontsize=10)
        ax1.set_ylabel("Runs", fontsize=10)
        legend_patches = [
            mpatches.Patch(color=C_CENTURY, label='Century (100+)'),
            mpatches.Patch(color=C_FIFTY,   label='Fifty (50+)'),
            mpatches.Patch(color=C_NORMAL,  label='Normal'),
            mpatches.Patch(color=C_DUCK,    label='Duck (0)'),
            Line2D([0],[0], color=C_AVG, linestyle='--', label=f'Avg {round(avg,1)}'),
        ]
        ax1.legend(handles=legend_patches, facecolor=BG_CARD2, labelcolor=TEXT_SEC,
                   fontsize=9, loc='upper right', framealpha=0.85)

        # ---- ROW 2: STRIKE RATE (left) + CAREER PROGRESSION (right) ----
        ax2 = fig.add_subplot(gs[2, :2])
        ax2.plot(innings, sr, color=C_SR, linewidth=1.8,
                 marker='o' if n <= 80 else None,
                 markersize=3, markerfacecolor=C_SR, zorder=3)
        ax2.fill_between(innings, sr, alpha=0.12, color=C_SR)
        ax2.axhline(sr_avg, color=C_AVG, linestyle='--', linewidth=1.2,
                    label=f'SR Avg: {sr_avg}')
        ax2.set_title("Strike Rate per Innings", fontsize=12, color=TEXT_PRI, pad=8)
        ax2.set_xlabel("Innings", fontsize=10)
        ax2.set_ylabel("Strike Rate", fontsize=10)
        ax2.legend(facecolor=BG_CARD2, labelcolor=TEXT_SEC, fontsize=9, framealpha=0.85)

        ax3 = fig.add_subplot(gs[2, 2:])
        ax3.plot(innings, cum_avg, color=C_TREND, linewidth=2,
                 marker='o' if n <= 80 else None,
                 markersize=3, markerfacecolor=C_TREND, zorder=3)
        ax3.fill_between(innings, cum_avg, alpha=0.12, color=C_TREND)
        ax3.set_title("Career Avg Progression", fontsize=12, color=TEXT_PRI, pad=8)
        ax3.set_xlabel("Innings", fontsize=10)
        ax3.set_ylabel("Cumulative Average", fontsize=10)

        # ---- ROW 3: FORM DOTS (left) + PIE (right) ----
        ax4 = fig.add_subplot(gs[3, :2])
        ax4.set_facecolor(BG_CARD2)
        ax4.axis('off')
        ax4.text(0.04, 0.82, "Last 5 innings form:", fontsize=11,
                 color=TEXT_SEC, transform=ax4.transAxes, va='center')
        dot_colors = [
            C_CENTURY if r >= 100 else C_FIFTY if r >= 50 else C_DUCK if r == 0 else C_NORMAL
            for r in last5
        ]
        for i, (r, dc) in enumerate(zip(last5, dot_colors)):
            cx = 0.14 + i * 0.17
            ellipse = mpatches.Ellipse((cx, 0.38), 0.14, 0.45,
                                        color=dc, transform=ax4.transAxes, clip_on=False)
            ax4.add_patch(ellipse)
            ax4.text(cx, 0.38, str(r), ha='center', va='center',
                     fontsize=10, color='white', fontweight='bold',
                     transform=ax4.transAxes)

        ax5 = fig.add_subplot(gs[3, 2:])
        below = max(0, n - hundreds - fifties - ducks)
        pie_vals   = [hundreds, fifties, below, ducks]
        pie_labels = ['100+', '50-99', 'Below 50', 'Ducks']
        pie_colors = [C_CENTURY, C_FIFTY, C_NORMAL, C_DUCK]
        pie_clean  = [max(v, 0) for v in pie_vals]
        if sum(pie_clean) > 0:
            wedges, texts, autotexts = ax5.pie(
                pie_clean, labels=pie_labels, colors=pie_colors,
                autopct='%1.0f%%', startangle=140,
                textprops={'color': TEXT_SEC, 'fontsize': 9},
                wedgeprops={'edgecolor': BG_DARK, 'linewidth': 1.5}
            )
            for at in autotexts:
                at.set_color(TEXT_PRI)
                at.set_fontsize(9)
        ax5.set_title("Innings Breakdown", fontsize=12, color=TEXT_PRI, pad=8)
        ax5.set_facecolor(BG_DARK)

        set_dark_style(fig, [ax1, ax2, ax3])

        save_and_show(fig, f"{player_name.replace(' ', '_')}_batting_stats.png")
        return True

    except Exception as e:
        print(f"[Jarvis] Batting graph error: {e}")
        return False


# ==============================
# BOWLING GRAPH
# ==============================
def show_bowling_graph(player_name):
    try:
        stats = get_bowling_stats(player_name)

        if not stats or 'wickets_list' not in stats:
            print(f"[Jarvis] {player_name} ka bowling data nahi mila")
            return False

        wickets = stats['wickets_list']
        if not wickets or len(wickets) == 0:
            print("[Jarvis] Wickets data empty hai")
            return False

        n       = len(wickets)
        innings = list(range(1, n + 1))
        economy = stats.get('economy_list',
                            [round(stats['economy'] + np.random.uniform(-1.5, 1.5), 1)
                             for _ in wickets])
        avg_w      = round(sum(wickets) / n, 2)
        avg_e      = round(sum(economy)  / n, 2)
        total_wkts = stats['total_wickets']
        best       = stats['best_bowling']
        bowl_avg   = stats['bowling_average']
        three_fers = stats['three_fers']
        last5      = wickets[-5:]

        cum_bowl_avg = []
        for i in range(n):
            w = sum(wickets[:i+1])
            r = sum(economy[:i+1]) * 6
            cum_bowl_avg.append(round(r / w, 1) if w > 0 else None)

        wkt_colors = [
            C_5WKT if w >= 5 else C_3WKT if w >= 3 else C_1WKT if w >= 1 else C_0WKT
            for w in wickets
        ]

        # ---- FIGURE ----
        fig = plt.figure(figsize=(20, 18), facecolor=BG_DARK)
        fig.suptitle(f"🎳   {player_name}   —   Bowling Statistics",
                     fontsize=18, color=TEXT_PRI, fontweight='bold', y=0.99)

        gs = gridspec.GridSpec(
            4, 4,
            figure=fig,
            height_ratios=[0.8, 3.5, 2.2, 1.5],
            hspace=0.6,
            wspace=0.4
        )

        # ---- ROW 0: STAT CARDS ----
        card_data = [
            ("Total Wickets", total_wkts,  ""),
            ("Best Bowling",  best,         "wickets"),
            ("Economy",       avg_e,        "runs/over"),
            ("Bowl Avg",      bowl_avg,     ""),
        ]
        for i, (label, val, unit) in enumerate(card_data):
            ax_c = fig.add_subplot(gs[0, i])
            ax_c.set_facecolor(BG_CARD2)
            ax_c.axis('off')
            ax_c.text(0.5, 0.78, label, ha='center', va='center',
                      fontsize=10, color=TEXT_SEC, transform=ax_c.transAxes)
            ax_c.text(0.5, 0.38, str(val), ha='center', va='center',
                      fontsize=24, color=TEXT_PRI, fontweight='bold', transform=ax_c.transAxes)
            if unit:
                ax_c.text(0.5, 0.10, unit, ha='center', va='center',
                          fontsize=9, color=TEXT_SEC, transform=ax_c.transAxes)

        # ---- ROW 1: WICKETS BAR CHART ----
        ax1 = fig.add_subplot(gs[1, :])
        bar_width = max(0.4, min(0.8, 40.0 / n))
        bars = ax1.bar(innings, wickets, color=wkt_colors,
                       edgecolor=BG_DARK, linewidth=0.3,
                       width=bar_width, zorder=3)
        ax1.axhline(avg_w, color=C_AVG, linestyle='--', linewidth=1.5, zorder=4)

        if n <= 60:
            for bar, w in zip(bars, wickets):
                ax1.text(bar.get_x() + bar.get_width() / 2,
                         bar.get_height() + 0.04,
                         str(w), ha='center', va='bottom',
                         fontsize=8, color=TEXT_SEC)

        ax1.set_title("Wickets per Innings", fontsize=13, color=TEXT_PRI, pad=10)
        ax1.set_xlabel("Innings", fontsize=10)
        ax1.set_ylabel("Wickets", fontsize=10)
        ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        legend_patches = [
            mpatches.Patch(color=C_5WKT, label='5-Wicket Haul'),
            mpatches.Patch(color=C_3WKT, label='3+ Wickets'),
            mpatches.Patch(color=C_1WKT, label='1-2 Wickets'),
            mpatches.Patch(color=C_0WKT, label='0 Wickets'),
            Line2D([0],[0], color=C_AVG, linestyle='--', label=f'Avg {avg_w}'),
        ]
        ax1.legend(handles=legend_patches, facecolor=BG_CARD2, labelcolor=TEXT_SEC,
                   fontsize=9, loc='upper right', framealpha=0.85)

        # ---- ROW 2: ECONOMY (left) + BOWLING AVG PROGRESSION (right) ----
        ax2 = fig.add_subplot(gs[2, :2])
        econ_colors = [C_1WKT if e <= 6 else C_0WKT if e >= 8 else C_ECON for e in economy]
        ax2.plot(innings, economy, color=C_ECON, linewidth=1.8,
                 marker='o' if n <= 80 else None,
                 markersize=3, zorder=3)
        ax2.scatter(innings, economy, c=econ_colors, zorder=4, s=25)
        ax2.fill_between(innings, economy, alpha=0.12, color=C_ECON)
        ax2.axhline(avg_e, color=C_AVG,  linestyle='--', linewidth=1.2, label=f'Avg: {avg_e}')
        ax2.axhline(6.0,  color=C_1WKT, linestyle=':',  linewidth=1.0, alpha=0.6, label='6.0 good')
        ax2.axhline(8.0,  color=C_0WKT, linestyle=':',  linewidth=1.0, alpha=0.6, label='8.0 expensive')
        ax2.set_title("Economy Rate per Innings", fontsize=12, color=TEXT_PRI, pad=8)
        ax2.set_xlabel("Innings", fontsize=10)
        ax2.set_ylabel("Economy (runs/over)", fontsize=10)
        ax2.legend(facecolor=BG_CARD2, labelcolor=TEXT_SEC, fontsize=9, framealpha=0.85)

        ax3 = fig.add_subplot(gs[2, 2:])
        valid = [(i+1, v) for i, v in enumerate(cum_bowl_avg) if v is not None]
        if valid:
            vx, vy = zip(*valid)
            ax3.plot(vx, vy, color=C_BOWLAVG, linewidth=2,
                     marker='o' if n <= 80 else None,
                     markersize=3, markerfacecolor=C_BOWLAVG, zorder=3)
            ax3.fill_between(vx, vy, alpha=0.12, color=C_BOWLAVG)
        ax3.set_title("Bowling Avg Progression", fontsize=12, color=TEXT_PRI, pad=8)
        ax3.set_xlabel("Innings", fontsize=10)
        ax3.set_ylabel("Bowling Average", fontsize=10)

        # ---- ROW 3: FORM DOTS (left) + PIE (right) ----
        ax4 = fig.add_subplot(gs[3, :2])
        ax4.set_facecolor(BG_CARD2)
        ax4.axis('off')
        ax4.text(0.04, 0.82, "Last 5 innings form:", fontsize=11,
                 color=TEXT_SEC, transform=ax4.transAxes, va='center')
        for i, w in enumerate(last5):
            color = C_5WKT if w >= 5 else C_3WKT if w >= 3 else C_1WKT if w >= 1 else C_0WKT
            cx = 0.14 + i * 0.17
            ellipse = mpatches.Ellipse((cx, 0.38), 0.14, 0.45,
                                        color=color, transform=ax4.transAxes, clip_on=False)
            ax4.add_patch(ellipse)
            ax4.text(cx, 0.38, str(w), ha='center', va='center',
                     fontsize=10, color='white', fontweight='bold',
                     transform=ax4.transAxes)

        ax5 = fig.add_subplot(gs[3, 2:])
        h5 = sum(1 for w in wickets if w >= 5)
        h3 = sum(1 for w in wickets if 3 <= w < 5)
        h1 = sum(1 for w in wickets if 1 <= w < 3)
        h0 = sum(1 for w in wickets if w == 0)
        pie_vals   = [h5, h3, h1, h0]
        pie_labels = ['5-wkt haul', '3-4 wkts', '1-2 wkts', '0 wkts']
        pie_colors = [C_5WKT, C_3WKT, C_1WKT, C_0WKT]
        pie_clean  = [max(v, 0) for v in pie_vals]
        if sum(pie_clean) > 0:
            wedges, texts, autotexts = ax5.pie(
                pie_clean, labels=pie_labels, colors=pie_colors,
                autopct='%1.0f%%', startangle=140,
                textprops={'color': TEXT_SEC, 'fontsize': 9},
                wedgeprops={'edgecolor': BG_DARK, 'linewidth': 1.5}
            )
            for at in autotexts:
                at.set_color(TEXT_PRI)
                at.set_fontsize(9)
        ax5.set_title("Innings Breakdown", fontsize=12, color=TEXT_PRI, pad=8)
        ax5.set_facecolor(BG_DARK)

        set_dark_style(fig, [ax1, ax2, ax3])

        save_and_show(fig, f"{player_name.replace(' ', '_')}_bowling_stats.png")
        return True

    except Exception as e:
        print(f"[Jarvis] Bowling graph error: {e}")
        return False