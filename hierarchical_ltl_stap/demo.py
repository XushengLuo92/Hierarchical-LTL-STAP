"""Presentation playback of real hierarchical-LTL plans; no planner run required."""
import argparse
import json
import math
from pathlib import Path
import re

import numpy as np

from .demo_monitor import Monitor

BG, PANEL, INK, MUTED = '#0b1220', '#122238', '#e6edf7', '#91a7bf'
GOOD, AMBER = '#50d9c6', '#ffbe69'
PALETTE = ['#5ddcca', '#76b6ff', '#d3a1ff', '#ffc578', '#ff94ac', '#b6da73']
NAMES = {1: 'Bin service', 2: 'Document distribution', 3: 'Office assistance', 4: 'Combined office mission'}


def leaf_description(formula):
    if 'carrybin' in formula:
        return 'Collect & dispose bin', 'D5 → G · carry, dispose, then reset', 'F(D5 ∧ default ∧ X((carrybin U dispose) ∧ F default))'
    if 'emptybin' in formula:
        return 'Empty & return bin', 'G → D5 · reset at the desk', 'F(G ∧ X emptybin ∧ F(D5 ∧ X default))'
    if 'photo' in formula:
        room = re.search(r'<> \((m\d+)', formula).group(1).upper()
        return f'Photo in {room}', 'Camera stays inside meeting rooms', f'F({room} ∧ photo)'
    if 'guide' in formula:
        return 'Guide a visitor', 'D11 → M6 · finish guiding on arrival', 'F(D11 ∧ (guide U (M6 ∧ X ¬guide)))'
    source = re.search(r'<> \((\w+)', formula).group(1).upper()
    target = re.search(r'U \((\w+)', formula).group(1).upper()
    return f'Deliver to {target}', f'{source} → {target} · avoid public while carrying', f'F({source} ∧ (carry U ({target} ∧ X ¬carry)))'


class Presentation:
    def __init__(self, data, fps=30, speed=2):
        import matplotlib.pyplot as plt
        from matplotlib.collections import PatchCollection
        from matplotlib.patches import Rectangle, FancyBboxPatch
        self.data, self.fps, self.speed = data, fps, speed
        self.monitor = Monitor(data)
        self.horizon = self.monitor.horizon
        self.step, self.paused = 0., False
        plt.rcParams.update({'text.usetex': False, 'font.family': 'DejaVu Sans'})
        self.fig = plt.figure(figsize=(16, 9), facecolor=BG)
        self.ax = self.fig.add_axes([.035, .56, .93, .36], facecolor=BG)
        self.ax.set(xlim=(1.5, 31), ylim=(.8, 8), aspect='equal', xticks=[], yticks=[])
        for spine in self.ax.spines.values(): spine.set_visible(False)
        workspace = data['workspace']
        vertices = sorted({tuple(p) for edge in workspace['edges'] for p in edge})
        self.ax.add_collection(PatchCollection([Rectangle(p, 1, 1) for p in vertices],
                                               facecolor='#152438', edgecolor='#24374b', linewidth=.4))
        obstacles = {tuple(p) for points in workspace['obstacles'].values() for p in points}
        self.ax.add_collection(PatchCollection([Rectangle(p, 1, 1) for p in obstacles],
                                               facecolor='#2c3b4d', edgecolor='#3b4c60', linewidth=.5))
        self.region_artists = {}
        for name, points in workspace['regions'].items():
            color = '#8399b4' if name.startswith('d') else '#ac9bff' if name.startswith('m') else GOOD
            if name == 'publicc': color = AMBER
            patch = PatchCollection([Rectangle((x+.04, y+.04), .92, .92) for x, y in points],
                                    facecolors=color, edgecolors=color, alpha=.18, linewidth=1.2)
            self.ax.add_collection(patch)
            self.region_artists[name] = patch
            # Put the region name at its own cell's top; robots sit below it.
            x, y = np.mean(points, axis=0)
            label = 'PUBLIC' if name == 'publicc' else name.upper()
            self.ax.text(x+.5, y+.96, label, color=color, fontsize=8 if name != 'publicc' else 7,
                         ha='center', va='top', weight='bold', zorder=8)
        self.robot_artists, self.robot_status = {}, {}
        for i, robot in enumerate(data['robots']):
            color = PALETTE[i % len(PALETTE)]
            line, = self.ax.plot([], [], color=color, lw=2.4, alpha=.45, solid_capstyle='round')
            dot = self.ax.scatter([], [], s=105, facecolor=color, edgecolor=BG, linewidth=1.5, zorder=10)
            label = self.ax.text(0, 0, str(robot['number']), fontsize=7, color=BG, ha='center', va='center', weight='bold', zorder=11)
            ring = self.ax.scatter([], [], s=175, facecolors='none', edgecolors=color, linewidth=1.2, zorder=9)
            self.robot_artists[robot['id']] = line, dot, label, ring
            x = .042 + i * .148
            self.fig.text(x, .957, f'●  R{robot["number"]}', color=color, fontsize=11, weight='bold')
            self.robot_status[robot['id']] = self.fig.text(x+.043, .957, '', color=MUTED, fontsize=9)
        self.guard = self.fig.text(.045, .525, '', color=AMBER, fontsize=10)
        self.fig.text(.045, .483, f'SCENARIO {data["scenario"]} / {NAMES[data["scenario"]].upper()}',
                      color=INK, fontsize=12, weight='bold')
        self.root = self.fig.text(.96, .483, '', color=GOOD, fontsize=11, ha='right')
        root_formula = self.monitor.formulas['p0'].replace('<>', 'F').replace('&&', '∧')
        self.fig.text(.045, .454, 'p0 = ' + root_formula, color=MUTED, fontsize=10)
        self.clock = self.fig.text(.96, .454, '', color=MUTED, fontsize=10, ha='right')
        self.group_artists, self.rows = [], []
        groups = self.monitor.children['p0']
        gap = .014
        width = (.915-gap*(len(groups)-1)) / len(groups)
        for i, group in enumerate(groups):
            left = .045+i*(width+gap)
            ax = self.fig.add_axes([left, .105, width, .322], facecolor=PANEL)
            ax.set(xlim=(0, 1), ylim=(0, 1), xticks=[], yticks=[])
            for spine in ax.spines.values(): spine.set_visible(False)
            if group in self.monitor.leaves:
                title = leaf_description(self.monitor.formulas[group])[0]
            else:
                titles = {3: {'p100': 'Meeting-room photos'},
                          4: {'p100': 'Bin service', 'p200': 'Printed copies', 'p300': 'Office assistance'}}
                title = titles[data['scenario']][group]
            ax.text(.04, .925, f'{group}  /  {title.upper()}', fontsize=10, color=INK, weight='bold')
            badge = ax.text(.96, .825, '', fontsize=9, color=MUTED, ha='right')
            children = self.monitor.children[group]
            formula = ' ∧ '.join('F '+child for child in children) if children else 'L2 / ACTION TASK'
            ax.text(.04, .825, formula, fontsize=9, color=MUTED)
            self.group_artists.append((group, badge))
            entries = []
            def walk(phi, depth=0):
                if not self.monitor.children[phi]: entries.append((phi, depth))
                else:
                    if depth: entries.append((phi, depth))
                    for child in self.monitor.children[phi]: walk(child, depth+1)
            walk(group)
            branches = sum(bool(self.monitor.children[phi]) for phi, _ in entries)
            leaf_count = len(entries)-branches
            row_height = min(.27, (.72-.075*branches) / leaf_count)
            y = .72
            for phi, depth in entries:
                if self.monitor.children[phi]:
                    ax.text(.052, y-.012, f'{phi} / Meeting-room photos', color=MUTED, fontsize=8, va='top')
                    branch_badge = ax.text(.945, y-.012, '', fontsize=8, color=MUTED, ha='right', va='top')
                    self.group_artists.append((phi, branch_badge))
                    y -= .075
                    continue
                title, hint, formula = leaf_description(self.monitor.formulas[phi])
                compact = leaf_count > 3
                box = FancyBboxPatch((.028, y-row_height+.012), .944, row_height-.016,
                                     boxstyle='round,pad=0.004,rounding_size=0.014', facecolor=BG,
                                     edgecolor='#294057', linewidth=1)
                ax.add_patch(box)
                ax.text(.052, y-(.025 if compact else .038), f'{phi}  {title}', color=INK, fontsize=9, va='top')
                state = ax.text(.945, y-(.025 if compact else .038), '', color=MUTED, fontsize=8, ha='right', va='top')
                detail = ax.text(.052, y-(.075 if compact else .12), '', color=MUTED,
                                 fontsize=8, va='top')
                if not compact:
                    ax.text(.052, y-row_height+.065, 'Goal: '+formula, color=MUTED, fontsize=7, va='top')
                self.rows.append((phi, box, state, detail, hint, compact))
                y -= row_height
        self.timeline = self.fig.add_axes([.048, .035, .91, .04], facecolor=BG)
        self.timeline.set(xlim=(-1, self.horizon+1), ylim=(0, 1))
        self.timeline.axis('off')
        self.timeline.plot([0, self.horizon], [.4, .4], color='#294057', lw=2)
        self.cursor = self.timeline.axvline(0, color=INK, lw=1)
        self.timeline.text(0, 0, '0', color=MUTED, fontsize=8, ha='center')
        self.timeline.text(self.horizon, 0, str(self.horizon), color=MUTED, fontsize=8, ha='center')
        self.milestones = []
        for t in sorted(set(self.monitor.completed[phi] for phi in self.monitor.leaves if phi in self.monitor.completed)):
            dot, = self.timeline.plot(t, .4, 'o', color=MUTED, ms=5)
            self.milestones.append((t, dot))
        self.fig.canvas.mpl_connect('key_press_event', self.key)
        self.fig.canvas.mpl_connect('button_press_event', self.seek)
        self.draw(0)

    def draw(self, step):
        step = self.step = min(self.horizon, max(0, step))
        tick = int(step)
        carrying, cameras = [], []
        for robot in self.data['robots']:
            path = np.asarray(robot['path'], dtype=float)
            next_tick = min(tick+1, self.horizon)
            point = path[tick] * (1-(step-tick)) + path[next_tick] * (step-tick)
            point += [.5, .37]
            line, dot, label, ring = self.robot_artists[robot['id']]
            trail = np.vstack([path[max(0, tick-5):tick+1] + [.5, .37], point])
            line.set_data(trail[:, 0], trail[:, 1])
            dot.set_offsets([point]); label.set_position(point)
            action = robot['actions'][tick]
            active = bool(robot['tasks'][tick])
            moving = not np.array_equal(path[tick], path[next_tick])
            default_state = 'moving' if moving else 'waiting' if active else 'idle'
            ring.set_offsets([point]); ring.set_visible(action != 'default')
            state = {'carrybin': 'bin', 'carry': 'document', 'guide': 'guiding', 'emptybin': 'emptying',
                     'dispose': 'disposing', 'camera': 'camera on', 'photo': 'photo'}.get(action, default_state)
            self.robot_status[robot['id']].set_text(state)
            self.robot_status[robot['id']].set_color(INK if active else MUTED)
            if action in ('carry', 'carrybin'): carrying.append(f'R{robot["number"]}')
            if action in ('camera', 'photo'): cameras.append(f'R{robot["number"]}')
        self.region_artists['publicc'].set_hatch('///' if carrying else None)
        self.region_artists['publicc'].set_alpha(.5 if carrying else .18)
        guard = ('PUBLIC ROUTE RESTRICTED  /  ' + ', '.join(carrying) + ' carrying') if carrying else 'PUBLIC ROUTE  /  no carrying robot'
        if any('photo' in f for f in self.monitor.formulas.values()):
            guard += '      •      CAMERA  /  ' + (', '.join(cameras) + ' in meeting rooms' if cameras else 'off')
        self.guard.set_text(guard)
        self.guard.set_color(AMBER if carrying else MUTED)
        completed = sum(self.monitor.status(phi, step) == 'done' for phi in self.monitor.leaves)
        self.root.set_text(f'{completed} / {len(self.monitor.leaves)} LEAF TASKS' + ('  ·  ROOT COMPLETE' if self.monitor.status('p0', step) == 'done' else ''))
        self.clock.set_text(f'STEP {step:05.1f} / {self.horizon}')
        for phi, badge in self.group_artists:
            status = self.monitor.status(phi, step)
            badge.set_text(status.upper()); badge.set_color(GOOD if status == 'done' else AMBER if status == 'active' else MUTED)
        for phi, box, badge, detail, hint, compact in self.rows:
            status = self.monitor.status(phi, step)
            color = GOOD if status == 'done' else AMBER if status == 'active' else '#294057'
            box.set_edgecolor(color); badge.set_color(color if status != 'pending' else MUTED)
            badge.set_text('✓' if status == 'done' else '●' if status == 'active' else '○')
            robot = self.monitor.witness_robot.get(phi)
            who = f'R{robot.split(":")[1]}' if robot else 'Unassigned'
            if compact:
                detail.set_text(who + ' · ' + (f'completed at {self.monitor.completed[phi]}' if status == 'done' else hint.split(' · ')[0]))
            else:
                detail.set_text(who + ' · ' + hint)
        self.cursor.set_xdata([step, step])
        for t, dot in self.milestones: dot.set_color(GOOD if t <= step else '#506177')

    def key(self, event):
        if event.key == ' ': self.paused = not self.paused
        elif event.key == 'r': self.draw(0)
        elif event.key in ('left', 'right'):
            self.paused = True; self.draw(self.step + (-1 if event.key == 'left' else 1))
        elif event.key in ('n', 'p'):
            self.paused = True
            future = [t for t, _ in self.milestones if t > self.step]
            past = [t for t, _ in self.milestones if t < self.step]
            self.draw(min(future, default=self.horizon) if event.key == 'n' else max(past, default=0))
        self.fig.canvas.draw_idle()

    def seek(self, event):
        if event.inaxes is self.timeline and event.xdata is not None:
            self.paused = True; self.draw(round(event.xdata)); self.fig.canvas.draw_idle()

    def save(self, output, dpi=120):
        from matplotlib.animation import FFMpegWriter
        import matplotlib as mpl
        import imageio_ffmpeg
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.suffix == '.png':
            self.fig.savefig(output, dpi=dpi, facecolor=BG)
            return
        if output.suffix != '.mp4': raise ValueError('Choose .png or .mp4; batch exports add GIF previews.')
        mpl.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()
        writer = FFMpegWriter(fps=self.fps, codec='libx264', bitrate=2800,
                              extra_args=['-pix_fmt', 'yuv420p', '-movflags', '+faststart'])
        frames = math.ceil(self.horizon / self.speed * self.fps)+1
        with writer.saving(self.fig, str(output), dpi):
            for frame in range(frames + self.fps*2):
                self.draw(min(self.horizon, frame*self.speed/self.fps))
                writer.grab_frame(facecolor=BG)

    def show(self):
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        def animate(_):
            if not self.paused:
                self.draw(0 if self.step >= self.horizon else self.step+self.speed/self.fps)
        self.animation = FuncAnimation(self.fig, animate, interval=1000/self.fps, cache_frame_data=False)
        plt.show()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', type=Path, default=Path(__file__).resolve().parents[1]/'demo/generated/scenario_01.json')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--step', type=float, default=0)
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--speed', type=float, default=2)
    parser.add_argument('--dpi', type=int, default=120)
    args = parser.parse_args()
    if args.fps <= 0 or args.speed <= 0 or args.dpi <= 0: parser.error('fps, speed and dpi must be positive')
    import matplotlib
    if args.output: matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data = json.loads(args.replay.read_text())
    view = Presentation(data, args.fps, args.speed)
    try:
        view.draw(args.step)
        if args.output: view.save(args.output, args.dpi)
        else: view.show()
    finally:
        plt.close(view.fig)


if __name__ == '__main__':
    main()
