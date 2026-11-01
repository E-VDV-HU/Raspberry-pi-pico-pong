"""
goal_explosions.py  V3.5.0

Usage (in your main script):
 * import goal_explosions
 * goal_explosions.setup(display)
 * goal_explosions.goal_explosion("wave", axis_ball[0], side_ball)

Animations are drawn for the LEFT goal, "R" flips them automatically.
"random" picks any effect. "text:ANYTHING" scrolls your own text.
Optional: setup(display, screen_text) to use your own scroller for text.

Animations made by Antropics Claude sonnet 5.5 model on medium setting.
"""

#import
from machine import Pin  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
import utime  # pyright: ignore[reportMissingImports, reportMissingModuleSource]
import random
import math

led = Pin("LED", Pin.OUT)

#vars
display = None
screen_text = None
speed = 0.1

# effects picked by "random" and shown in the demo
explosions = [
    "wave", "box", "sweep", "checker", "stripes", "blackhole",
    "explosion", "shockwave", "rain", "heartbeat", "spinner", "fireworks",
    "fallout", "rl_airstrike", "rl_hellfire", "rl_reaper",
    "rl_gravitybomb", "rl_shark", "rl_dragons", "rl_whirlwind",
    "txt_goal", "txt_ez", "txt_siu"
]


def setup(disp, text_function=None):
    global display, screen_text
    display = disp
    screen_text = text_function


def names():
    return explosions


def text_scroll(text):
    # Show text, but faster.
    if screen_text is not None:
        screen_text(text)
    else:
        for i in range(8, -len(text) * 8, -1):
            display.fill(0)
            display.text(text, i, 0, 1)
            display.show()
            utime.sleep(0.03)


def goal_explosion(var, x, side, y=3):
    frames = None
    text = None
    delay = speed

    if var == "random":
        var = random.choice(explosions)

    # Wave (fills from the goal, holds, drains out the far side)
    if var == "wave":
        delay = 0.07
        frames = []
        for step in range(1, 13):
            frames.append([
                [1 if c + abs(r - 3.5) <= step else 0 for c in range(8)]
                for r in range(8)
            ])
        frames += [[[1, 1, 1, 1, 1, 1, 1, 1]] * 8] * 4
        for step in range(1, 13):
            frames.append([
                [0 if c + abs(r - 3.5) <= step else 1 for c in range(8)]
                for r in range(8)
            ])

    # Box (rings, collapse, rings again, then solid squares in and out)
    elif var == "box":
        delay = 0.1
        frames = []
        for s in [0.5, 1.5, 2.5, 3.5, 2.5, 1.5, 0.5, 1.5, 2.5, 3.5]:
            frames.append([
                [
                    1 if abs(max(abs(r - 3.5), abs(c - 3.5)) - s) < 0.1 else 0
                    for c in range(8)
                ]
                for r in range(8)
            ])
        for s in [0.5, 1.5, 2.5, 3.5, 3.5, 2.5, 1.5, 0.5]:
            frames.append([
                [
                    1 if max(abs(r - 3.5), abs(c - 3.5)) <= s else 0
                    for c in range(8)
                ]
                for r in range(8)
            ])
        frames.append([[0, 0, 0, 0, 0, 0, 0, 0]] * 8)

    # Sweep (fills column by column, holds, drains)
    elif var == "sweep":
        delay = 0.08
        frames = []
        for col in range(1, 9):
            frames.append([
                [1 if c < col else 0 for c in range(8)]
                for r in range(8)
            ])
        frames += [[[1, 1, 1, 1, 1, 1, 1, 1]] * 8] * 3
        for col in range(1, 9):
            frames.append([
                [0 if c < col else 1 for c in range(8)]
                for r in range(8)
            ])

    # Checker
    elif var == "checker":
        delay = 0.1
        a = [
            [1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 1]
        ] * 4
        b = [
            [0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0]
        ] * 4
        frames = [a, b] * 8

    # Stripes
    elif var == "stripes":
        delay = 0.1
        a = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ] * 4
        b = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1]
        ] * 4
        frames = [a, b] * 8

    # Black hole (ring collapses, disc with dark core pulses, flare, hole eats the screen)
    elif var == "blackhole":
        delay = 0.1
        d1 = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        d2 = [
            [0, 0, 1, 0, 0, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 0, 0, 1, 0, 0]
        ]
        frames = [
            [
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 1],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]
        ]
        frames += [d1, d2] * 5
        frames.append([[1, 1, 1, 1, 1, 1, 1, 1]] * 8)
        for k in range(1, 8):
            frames.append([
                [
                    0 if ((r - 3.5) ** 2 + (c - 3.5) ** 2) ** 0.5 <= k * 0.75 else 1
                    for c in range(8)
                ]
                for r in range(8)
            ])

    # Explosion (fireball at the goal, then shrapnel flies out)
    elif var == "explosion":
        delay = 0.07
        fire = [1.0, 2.2, 3.0, 2.4, 1.6, 0.8]
        pieces = []
        for i in range(16):
            vx = 0.2 + random.random() * 0.8
            vy = (random.random() * 2 - 1) * 0.8
            life = 8 + int(random.random() * 14)
            pieces.append([vx, vy, life])
        frames = []
        for t in range(24):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            if t < len(fire):
                for r in range(8):
                    for c in range(8):
                        if ((c - 0.5) ** 2 + (r - 3.5) ** 2) ** 0.5 <= fire[t]:
                            m[r][c] = 1
            for p in pieces:
                fx = p[0] * t
                fy = 3.5 + p[1] * t
                if t < p[2] and 0 <= fx <= 7 and 0 <= fy <= 7:
                    m[int(fy + 0.5)][int(fx + 0.5)] = 1
            frames.append(m)

    # Shockwave (two rings expanding from the goal)
    elif var == "shockwave":
        delay = 0.07
        frames = []
        for k in range(20):
            rho = k * 0.6
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            for r in range(8):
                for c in range(8):
                    dist = (c * c + (r - 3.5) ** 2) ** 0.5
                    if abs(dist - rho) < 0.8 or abs(dist - rho + 2.4) < 0.8:
                        m[r][c] = 1
            frames.append(m)

    # Rain (3 drops per column, falls for ~3 seconds)
    elif var == "rain":
        delay = 0.08
        offs = [0, 3, 1, 5, 2, 6, 4, 7]
        gaps = [9, 11, 8, 10, 11, 9, 8, 10]
        frames = []
        for t in range(40):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            for c in range(8):
                for k in range(3):
                    head = t - offs[c] - k * gaps[c]
                    for r in range(8):
                        if 0 <= head - r < 3:
                            m[r][c] = 1
            frames.append(m)

    # Heartbeat
    elif var == "heartbeat":
        delay = 0.12
        small = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        big = [
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        frames = [
            small, big, big, small, small, big, big,
            small, small, big, big, big, small,
            [[0, 0, 0, 0, 0, 0, 0, 0]] * 8
        ]

    # Spinner (rotating line)
    elif var == "spinner":
        delay = 0.08
        v = [[0, 0, 0, 1, 1, 0, 0, 0]] * 8
        h = (
            [[0, 0, 0, 0, 0, 0, 0, 0]] * 3
            + [[1, 1, 1, 1, 1, 1, 1, 1]] * 2
            + [[0, 0, 0, 0, 0, 0, 0, 0]] * 3
        )
        diag1 = [
            [1, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 1]
        ]
        diag2 = [row[::-1] for row in diag1]
        frames = [v, diag1, h, diag2] * 6
        frames.append([[0, 0, 0, 0, 0, 0, 0, 0]] * 8)

    # Fireworks (4 rockets launch one after another and burst)
    elif var == "fireworks":
        delay = 0.1
        shows = [[3, 2, 0], [6, 3, 4], [1, 1, 8], [4, 2, 12]]   # [column, burst row, start frame]
        frames = []
        for t in range(32):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            for fw in shows:
                fc = fw[0]
                br = fw[1]
                s = t - fw[2]
                rise = 7 - br
                if 0 <= s < rise:
                    m[7 - s][fc] = 1
                    if s > 0:
                        m[8 - s][fc] = 1
                elif s >= rise and s - rise <= 8:
                    age = s - rise
                    rad = 0.8 + age * 0.8
                    fall = 0
                    if age >= 3:
                        fall = age - 2
                    for r in range(8):
                        for c in range(8):
                            dist = ((r - br) ** 2 + (c - fc) ** 2) ** 0.5
                            if abs(dist - rad) < 0.7 and (age < 3 or (r + c) % 2 == 0):
                                if r + fall <= 7:
                                    m[r + fall][c] = 1
            frames.append(m)

    # Fallout (custom: white-out, mushroom cloud rises, ash drifts down)
    elif var == "fallout":
        delay = 0.09
        blank = [0, 0, 0, 0, 0, 0, 0, 0]
        base = [
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0]
        ]
        cloud_a = [blank] * 6 + base
        cloud_b = [blank] * 4 + [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0]
        ] + base
        cloud_c = [blank] * 2 + [
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0]
        ] + base
        cloud_d = [
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0]
        ] + base
        cloud_e = [
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 0, 1, 1, 0, 1, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ] + base
        white = [[1, 1, 1, 1, 1, 1, 1, 1]] * 8
        frames = [white, white, cloud_a, cloud_b, cloud_c, cloud_d, cloud_d, cloud_e, cloud_e]
        offs = [0, 2, 5, 1, 6, 3, 7, 4]
        for t in range(24):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            if t < 6:
                keep = 4
            elif t < 10:
                keep = 2
            elif t < 13:
                keep = 1
            else:
                keep = 0
            for r in range(keep):
                for c in range(8):
                    m[r][c] = cloud_e[r][c]
            if t < 10:
                m[7] = [0, 1, 1, 1, 1, 1, 1, 0]
            for c in range(8):
                row = (t - offs[c]) // 2
                if 0 <= row <= 7:
                    m[row][c] = 1
            frames.append(m)

    # RL Airstrike (reticle locks on, bombs rain down, impact flash)
    elif var == "rl_airstrike":
        delay = 0.08
        frames = []
        for s in [3.5, 3.5, 2.5, 2.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5]:
            frames.append([
                [
                    1 if abs(max(abs(r - 3.5), abs(c - 3.5)) - s) < 0.1 else 0
                    for c in range(8)
                ]
                for r in range(8)
            ])
        bombs = [[1, 0], [3, 2], [5, 4], [6, 6], [2, 7]]   # [column, start frame]
        for t in range(18):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            for b in bombs:
                row = t - b[1]
                if 0 <= row <= 6:
                    m[row][b[0]] = 1
                    if row > 0:
                        m[row - 1][b[0]] = 1
                elif 7 <= row <= 8:
                    for dc in (-1, 0, 1):
                        if 0 <= b[0] + dc <= 7:
                            m[7][b[0] + dc] = 1
                    m[6][b[0]] = 1
            frames.append(m)
        frames += [
            [[1, 1, 1, 1, 1, 1, 1, 1]] * 8,
            [[0, 0, 0, 0, 0, 0, 0, 0]] * 8
        ]

    # RL Hellfire (flaming skull rises out of the net)
    elif var == "rl_hellfire":
        delay = 0.09
        blank = [0, 0, 0, 0, 0, 0, 0, 0]
        body = [
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 0, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 0, 0, 1, 0, 0]
        ]
        skull_a = [[1, 0, 1, 0, 0, 1, 0, 1]] + body
        skull_b = [[0, 1, 0, 1, 1, 0, 1, 0]] + body
        frames = []
        for d in range(7, 0, -1):
            frames.append([blank] * d + skull_a[:8 - d])
        frames += [skull_a, skull_b] * 6
        frames += [
            [[1, 1, 1, 1, 1, 1, 1, 1]] * 8,
            [[0, 0, 0, 0, 0, 0, 0, 0]] * 8
        ]

    # RL Reaper (hooded reaper jumps out of the net, hops, retreats)
    elif var == "rl_reaper":
        delay = 0.09
        blank = [0, 0, 0, 0, 0, 0, 0, 0]
        reaper = [
            [0, 0, 1, 1, 1, 0, 1, 1],
            [0, 1, 1, 1, 1, 1, 0, 1],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [0, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 1, 0, 1, 0, 0, 1]
        ]
        hop = reaper[1:] + [blank]
        frames = []
        for k in range(1, 9):
            frames.append([row[8 - k:] + [0] * (8 - k) for row in reaper])
        frames += [reaper] * 2
        frames += [hop, reaper, hop, reaper]
        frames += [reaper] * 3
        for k in range(7, 0, -1):
            frames.append([row[8 - k:] + [0] * (8 - k) for row in reaper])
        frames.append([blank] * 8)

    # RL Gravity Bomb (vortex pulls everything in, collapses, pops)
    elif var == "rl_gravitybomb":
        delay = 0.07
        frames = []
        for t in range(28):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            for i in range(12):
                rad = 2.5 + (i % 4) * 0.9 - t * 0.2
                ang = i * 0.52 + t * 0.5
                if rad > 0.4:
                    fy = 3.5 + rad * math.sin(ang)
                    fx = 3.5 + rad * math.cos(ang)
                    if 0 <= fx <= 7 and 0 <= fy <= 7:
                        m[int(fy + 0.5)][int(fx + 0.5)] = 1
            frames.append(m)
        frames += [
            [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 1, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0, 1, 0, 0],
                [0, 0, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            [[1, 1, 1, 1, 1, 1, 1, 1]] * 8,
            [[0, 0, 0, 0, 0, 0, 0, 0]] * 8
        ]

    # RL Shark Attack (paint drops fall, splash, shark breaches)
    elif var == "rl_shark":
        delay = 0.07
        blank = [0, 0, 0, 0, 0, 0, 0, 0]
        shark = [
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]
        ]
        frames = []
        for t in range(10):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            for col in (0, 1, 2):
                row = t - col * 2
                if 0 <= row <= 7:
                    m[row][col] = 1
            frames.append(m)
        frames += [
            [blank] * 6 + [[1, 1, 1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 0, 0]],
            [blank] * 5 + [
                [0, 1, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 0, 0]
            ]
        ]
        for d in range(7, -1, -1):
            frames.append([blank] * d + shark[:8 - d])
        frames += [shark] * 4
        for d in range(0, 8):
            frames.append([blank] * d + shark[:8 - d])
        frames.append([blank] * 8)

    # RL Dueling Dragons (two serpents coil around each other and slither off)
    elif var == "rl_dragons":
        delay = 0.07
        frames = []
        for t in range(34):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            hi = t * 0.5
            lo = (t - 18) * 0.5
            for sign in (1, -1):
                prev = None
                for c in range(8):
                    yc = int(3.5 + sign * 2.6 * math.sin(c * 0.7 - t * 0.4) + 0.5)
                    if lo < c <= hi:
                        if prev is None:
                            m[yc][c] = 1
                        else:
                            for rr in range(min(prev, yc), max(prev, yc) + 1):
                                m[rr][c] = 1
                        prev = yc
                    else:
                        prev = None
            frames.append(m)

    # RL Chromatic Hollow (whirlwind: spiral arms grow, spin, then collapse)
    elif var == "rl_whirlwind":
        delay = 0.07
        frames = []
        for t in range(34):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            scale = min(1.0, t / 8, (33 - t) / 8)
            if scale > 0:
                for arm in range(3):
                    for k in range(10):
                        rad = (0.4 + k * 0.45) * scale
                        ang = arm * 2.09 + k * 0.55 + t * 0.5
                        fx = 3.5 + rad * math.cos(ang)
                        fy = 3.5 + rad * math.sin(ang)
                        if 0 <= fx <= 7 and 0 <= fy <= 7:
                            m[int(fy + 0.5)][int(fx + 0.5)] = 1
            frames.append(m)

    # Text
    elif var == "txt_goal":
        text = "GOAL"
    elif var == "txt_ez":
        text = "EZZZZ"
    elif var == "txt_siu":
        text = "SIUUUU"
    elif var.startswith("text:"):
        text = var[5:]

    else:
        for i in range(10):
            led.toggle()
            utime.sleep(0.1)
        raise ValueError(f"{var} is not found!")

    # play it
    if text is not None:
        text_scroll(text)
    else:
        for matrix_LIST in frames:
            if side == "R":
                matrix_LIST = [row[::-1] for row in matrix_LIST]
            display.write_matrix(matrix_LIST)
            display.show()
            utime.sleep(delay)

    display.fill(0)
    display.show()