"""
GRAPHS ENGINE - IPL 2026 Analytics Visualizations
===================================================
Batting analysis | Bowling analysis | Momentum dashboard
"""
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from ml_brain import predict_future_score, predict_future_wickets, calculate_win_probability


# ══════════════════════════════════════════════════════════
#  BATTING GRAPH
# ══════════════════════════════════════════════════════════
def draw_batting_graph(player: str, scores: list, ml_result: dict = None):
    if not scores or len(scores) < 3:
        print(f"[Graph] Not enough data for {player}")
        return

    scores  = scores[-14:]
    labels  = [f"M{i+1}" for i in range(len(scores))]
    avg_v   = np.mean(scores)
    colors  = ['#00ff88' if s >= 75 else '#ffd700' if s >= 50
               else '#4fc3f7' if s >= 25 else '#ef5350' for s in scores]

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#161b22')

    bars = ax.bar(labels, scores, color=colors, width=0.6, zorder=3)
    ax.plot(labels, scores, 'white', lw=1.5, marker='o', ms=5, alpha=0.7, zorder=4)
    ax.axhline(avg_v, color='#ff9800', lw=2, ls='--', alpha=0.85, label=f'Avg {avg_v:.1f}')
    ax.axhline(50,  color='#ffd700',  lw=1, ls=':', alpha=0.4)
    ax.axhline(100, color='#00ff88',  lw=1, ls=':', alpha=0.4)

    # ML prediction line
    if ml_result and ml_result.get("predicted") is not None:
        pred  = ml_result["predicted"]
        trend = ml_result.get("trend", "")
        conf  = ml_result.get("confidence", "")
        ax.axhline(pred, color='#e91e63', lw=2.5, ls='-.', alpha=0.9,
                   label=f'ML Prediction: {pred} ({trend}, {conf} confidence)')

    for bar, s in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                str(s), ha='center', va='bottom', fontsize=9,
                color='white', fontweight='bold')

    ax.set_xlabel('Match', color='#8b949e', fontsize=11)
    ax.set_ylabel('Runs',  color='#8b949e', fontsize=11)
    ax.set_title(f'{player} - IPL 2026 Batting Analysis',
                 color='white', fontsize=14, fontweight='bold', pad=15)
    ax.tick_params(colors='#8b949e', labelsize=9)
    for sp in ['top', 'right']:  ax.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']: ax.spines[sp].set_color('#30363d')
    ax.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)
    ax.set_ylim(0, max(scores) + 35)

    legend = [
        mpatches.Patch(color='#00ff88', label='75+ (Excellent)'),
        mpatches.Patch(color='#ffd700', label='50-74 (Half century)'),
        mpatches.Patch(color='#4fc3f7', label='25-49 (Decent)'),
        mpatches.Patch(color='#ef5350', label='0-24 (Poor)'),
        plt.Line2D([0], [0], color='#ff9800', lw=2, ls='--', label=f'Avg {avg_v:.1f}'),
    ]
    if ml_result and ml_result.get("predicted") is not None:
        legend.append(plt.Line2D([0], [0], color='#e91e63', lw=2.5, ls='-.',
                                  label=f'ML Pred {ml_result["predicted"]}'))

    ax.legend(handles=legend, loc='upper right',
              framealpha=0.3, labelcolor='white', fontsize=9)
    plt.tight_layout()

    fname = player.replace(" ", "_") + "_batting.png"
    plt.savefig(fname, dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.show()
    print(f"Saved: {fname}")


# ══════════════════════════════════════════════════════════
#  BOWLING GRAPH
# ══════════════════════════════════════════════════════════
def draw_bowling_graph(player: str, wickets: list, economies: list,
                        ml_result: dict = None):
    if not wickets or len(wickets) < 3:
        print(f"[Graph] Not enough bowling data for {player}")
        return

    wickets  = wickets[-14:]
    n        = len(wickets)
    economies = (economies[-14:] if economies and len(economies) >= n
                 else [8.0] * n)
    labels   = [f"M{i+1}" for i in range(n)]
    avg_wv   = np.mean(wickets)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9),
                                    gridspec_kw={'height_ratios': [3, 2]})
    fig.patch.set_facecolor('#0d1117')

    # Wicket bars
    ax1.set_facecolor('#161b22')
    wc = ['#e91e63' if w == 0 else '#ff9800' if w == 1
          else '#ffd700' if w == 2 else '#00ff88' for w in wickets]
    bars = ax1.bar(labels, wickets, color=wc, width=0.6, zorder=3)
    ax1.plot(labels, wickets, 'white', lw=1.5, marker='D', ms=5, alpha=0.7, zorder=4)
    for bar, w in zip(bars, wickets):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                 str(w), ha='center', va='bottom', fontsize=10,
                 color='white', fontweight='bold')
    ax1.axhline(avg_wv, color='#03a9f4', lw=2, ls='--', alpha=0.8,
                label=f'Avg {avg_wv:.1f} wkts')
    if ml_result and ml_result.get("predicted") is not None:
        ax1.axhline(ml_result["predicted"], color='#e91e63', lw=2.5, ls='-.',
                    alpha=0.9, label=f'ML Pred {ml_result["predicted"]}')
    ax1.set_title(f'{player} - IPL 2026 Bowling Analysis',
                  color='white', fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel('Wickets', color='#8b949e', fontsize=11)
    ax1.set_ylim(0, max(wickets) + 2)
    ax1.tick_params(colors='#8b949e', labelsize=9)
    for sp in ['top', 'right']:  ax1.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']: ax1.spines[sp].set_color('#30363d')
    ax1.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)
    ax1.legend(loc='upper right', framealpha=0.3, labelcolor='white', fontsize=9)

    # Economy line
    ax2.set_facecolor('#161b22')
    ax2.plot(labels, economies, color='#ff6b6b', lw=2.5, marker='o', ms=6, zorder=3)
    ax2.fill_between(range(n), economies, alpha=0.2, color='#ff6b6b')
    ax2.axhline(7.5, color='#ffd700', lw=1.5, ls=':', alpha=0.7, label='Good economy (7.5)')
    eco_avg = np.mean(economies)
    ax2.axhline(eco_avg, color='#03a9f4', lw=2, ls='--', alpha=0.8,
                label=f'Avg economy {eco_avg:.1f}')
    if ml_result and ml_result.get("economy_predicted"):
        ax2.axhline(ml_result["economy_predicted"], color='#e91e63', lw=2, ls='-.',
                    alpha=0.9, label=f'ML Eco Pred {ml_result["economy_predicted"]:.1f}')
    ax2.set_xlabel('Match', color='#8b949e', fontsize=11)
    ax2.set_ylabel('Economy', color='#8b949e', fontsize=11)
    ax2.set_xticks(range(n))
    ax2.set_xticklabels(labels)
    ax2.tick_params(colors='#8b949e', labelsize=9)
    for sp in ['top', 'right']:  ax2.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']: ax2.spines[sp].set_color('#30363d')
    ax2.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)
    ax2.legend(loc='upper right', framealpha=0.3, labelcolor='white', fontsize=9)

    plt.tight_layout()
    fname = player.replace(" ", "_") + "_bowling.png"
    plt.savefig(fname, dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.show()
    print(f"Saved: {fname}")


# ══════════════════════════════════════════════════════════
#  MOMENTUM DASHBOARD
# ══════════════════════════════════════════════════════════
def draw_momentum_dashboard(match_state: dict):
    run_hist  = match_state.get("run_history", [])
    rr_hist   = match_state.get("rr_history", [])
    wkt_overs = match_state.get("wicket_overs", [])
    target    = match_state.get("target", 0)
    t1        = match_state.get("team1", "Team A")
    t2        = match_state.get("team2", "Team B")

    if len(run_hist) < 3:
        np.random.seed(42)
        run_hist  = list(np.cumsum(np.random.randint(4, 12, 20)))
        wkt_overs = [3, 7, 11, 15, 18]

    n = len(run_hist)
    if len(rr_hist) != n:
        rr_hist = [round(run_hist[i] / (i + 1), 2) for i in range(n)]

    overs   = list(range(1, n + 1))
    target  = target or max(run_hist) + 30
    win_probs = []
    for i, r in enumerate(run_hist):
        wkt = sum(1 for wo in wkt_overs if wo <= i + 1)
        wp  = calculate_win_probability(r, wkt, float(i + 1), target)
        win_probs.append(wp.get("win_percent", 50))

    fig = plt.figure(figsize=(16, 11), facecolor='#0d1117')
    gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

    # Plot 1: Cumulative runs
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor('#161b22')
    ax1.plot(overs, run_hist, color='#00ff88', lw=2.5, marker='o', ms=4,
             label='Runs scored', zorder=3)
    if target:
        ax1.axhline(target, color='#ff4444', lw=2, ls='--', label=f'Target {target}')
    for wo in wkt_overs:
        if 1 <= wo <= n:
            ax1.axvline(wo, color='#ff6b6b', lw=1.5, ls=':', alpha=0.7)
    ax1.fill_between(overs, run_hist, alpha=0.15, color='#00ff88')
    ax1.set_title(f'Match Momentum: {t1} vs {t2}',
                  color='white', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Over', color='#8b949e')
    ax1.set_ylabel('Runs', color='#8b949e')
    ax1.tick_params(colors='#8b949e', labelsize=8)
    ax1.legend(framealpha=0.3, labelcolor='white', fontsize=9)
    for sp in ['top', 'right']:  ax1.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']: ax1.spines[sp].set_color('#30363d')
    ax1.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)

    # Plot 2: Run rate per over
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor('#161b22')
    rr_colors = ['#00ff88' if r >= 8 else '#ffd700' if r >= 6 else '#ef5350'
                 for r in rr_hist]
    ax2.bar(overs[:len(rr_hist)], rr_hist, color=rr_colors[:len(rr_hist)], width=0.7, zorder=3)
    avg_rr = np.mean(rr_hist)
    ax2.axhline(avg_rr, color='#ff9800', lw=2, ls='--', alpha=0.8,
                label=f'Avg RR {avg_rr:.1f}')
    ax2.set_title('Run Rate Per Over', color='white', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Over', color='#8b949e')
    ax2.set_ylabel('RR', color='#8b949e')
    ax2.tick_params(colors='#8b949e', labelsize=8)
    ax2.legend(framealpha=0.3, labelcolor='white', fontsize=9)
    for sp in ['top', 'right']:  ax2.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']: ax2.spines[sp].set_color('#30363d')
    ax2.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)

    # Plot 3: Phase analysis
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor('#161b22')
    pp_r  = run_hist[min(5, n-1)]
    mid_r = max(0, (run_hist[min(14, n-1)] - run_hist[min(5, n-1)])) if n > 6 else 0
    dth_r = max(0, (run_hist[-1] - run_hist[min(14, n-1)])) if n > 15 else 0
    bars3 = ax3.bar(['Powerplay\n(1-6)', 'Middle\n(7-15)', 'Death\n(16-20)'],
                    [pp_r, mid_r, dth_r],
                    color=['#4fc3f7', '#ffd700', '#ff6b6b'], width=0.5, zorder=3)
    for bar, val in zip(bars3, [pp_r, mid_r, dth_r]):
        ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 str(val), ha='center', va='bottom',
                 fontsize=10, color='white', fontweight='bold')
    ax3.set_title('Runs by Phase', color='white', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Runs', color='#8b949e')
    ax3.tick_params(colors='#8b949e', labelsize=9)
    for sp in ['top', 'right']:  ax3.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']: ax3.spines[sp].set_color('#30363d')
    ax3.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)

    # Plot 4: Win probability
    ax4 = fig.add_subplot(gs[2, :])
    ax4.set_facecolor('#161b22')
    ax4.plot(overs, win_probs, color='#e91e63', lw=2.5, marker='o', ms=3, zorder=3)
    ax4.fill_between(overs, win_probs, 50,
                     where=[w >= 50 for w in win_probs],
                     alpha=0.2, color='#00ff88', label='Batting ahead')
    ax4.fill_between(overs, win_probs, 50,
                     where=[w < 50 for w in win_probs],
                     alpha=0.2, color='#ef5350', label='Bowling ahead')
    ax4.axhline(50, color='white', lw=1, ls='-', alpha=0.3)
    ax4.set_title('Win Probability Over Time (ML-powered)',
                  color='white', fontsize=11, fontweight='bold')
    ax4.set_xlabel('Over', color='#8b949e')
    ax4.set_ylabel('Win %', color='#8b949e')
    ax4.set_ylim(0, 100)
    ax4.tick_params(colors='#8b949e', labelsize=8)
    ax4.legend(framealpha=0.3, labelcolor='white', fontsize=9)
    for sp in ['top', 'right']:  ax4.spines[sp].set_visible(False)
    for sp in ['bottom', 'left']: ax4.spines[sp].set_color('#30363d')
    ax4.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)

    plt.suptitle('JARVIS IPL 2026 - ML ANALYTICS DASHBOARD',
                 color='#8b949e', fontsize=11, y=0.99)
    plt.savefig('momentum_dashboard.png', dpi=150,
                bbox_inches='tight', facecolor='#0d1117')
    plt.show()
    print("Saved: momentum_dashboard.png")