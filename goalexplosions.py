"""
goal_explosions.py  V3.4.0

Usage (in your main script):
 * import goal_explosions
 * goal_explosions.setup(display)
 * goal_explosions.goal_explosion("wave", axis_ball[0], side_ball)

Animations are drawn for the LEFT goal, "R" flips them automatically.
"random" picks any effect. "text:ANYTHING" scrolls your own text.
Optional: setup(display, screen_text) to use your own scroller for text.
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
    "wave", "box", "sweep", "flash", "checker", "stripes", "blackhole",
    "explosion", "shockwave", "rain", "heartbeat", "spinner", "fireworks",
    "rl_airstrike", "rl_hellfire", "rl_batman", "rl_beachparty",
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

    # Wave (fills from the goal, flashes, drains out the far side)
    if var == "wave":
        delay = 0.07
        frames = []
        for step in range(1, 13):
            frames.append([
                [1 if c + abs(r - 3.5) <= step else 0 for c in range(8)]
                for r in range(8)
            ])
        frames += [
            [[0, 0, 0, 0, 0, 0, 0, 0]] * 8,
            [[1, 1, 1, 1, 1, 1, 1, 1]] * 8
        ] * 2
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

    # Flash
    elif var == "flash":
        delay = 0.09
        frames = [
            [[1, 1, 1, 1, 1, 1, 1, 1]] * 8,
            [[0, 0, 0, 0, 0, 0, 0, 0]] * 8
        ] * 8

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

    # Rain
    elif var == "rain":
        delay = 0.08
        offs = [0, 3, 1, 5, 2, 6, 4, 7]
        frames = []
        for t in range(18):
            frames.append([
                [
                    1 if 0 <= (t - offs[c]) - r < 3 else 0
                    for c in range(8)
                ]
                for r in range(8)
            ])

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

    # Fireworks (rocket goes up, bursts, sparks fall)
    elif var == "fireworks":
        delay = 0.12
        frames = []
        for r in range(7, 1, -1):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            m[r][3] = 1
            if r < 7:
                m[r + 1][3] = 1
            frames.append(m)

        frames += [
            [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 1, 0, 1, 0, 0, 0],
                [0, 1, 0, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 1, 0, 1, 0, 0, 0],
                [0, 1, 0, 0, 0, 1, 0, 0],
                [1, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 1, 0, 0, 0, 1, 0, 0],
                [1, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 0]
            ],
            [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 1, 0, 0],
                [1, 0, 0, 0, 0, 0, 1, 0]
            ],
            [[0, 0, 0, 0, 0, 0, 0, 0]] * 8
        ]

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

    # RL The Batman (bat symbol flickers on, holds, burns out)
    elif var == "rl_batman":
        delay = 0.1
        blank = [0, 0, 0, 0, 0, 0, 0, 0]
        bat = [
            blank,
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 0, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 0, 1, 1, 0, 1, 0],
            blank
        ]
        frames = [bat, [blank] * 8] * 3
        frames += [bat] * 6
        for d in range(1, 8):
            frames.append(bat[:8 - d] + [blank] * d)

    # RL Beach Party (beach balls bounce around the board)
    elif var == "rl_beachparty":
        delay = 0.08
        balls = [
            [0.0, 3.0, 0.45, -0.5],
            [0.0, 4.0, 0.6, 0.45],
            [0.0, 2.0, 0.35, 0.3],
            [0.0, 5.0, 0.5, -0.35],
            [0.0, 3.0, 0.3, 0.6],
            [0.0, 4.0, 0.7, -0.2]
        ]
        frames = []
        for t in range(30):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            for b in balls:
                b[0] += b[2]
                b[1] += b[3]
                if b[0] < 0:
                    b[0] = -b[0]
                    b[2] = -b[2]
                elif b[0] > 7:
                    b[0] = 14 - b[0]
                    b[2] = -b[2]
                if b[1] < 0:
                    b[1] = -b[1]
                    b[3] = -b[3]
                elif b[1] > 7:
                    b[1] = 14 - b[1]
                    b[3] = -b[3]
                m[int(b[1] + 0.5)][int(b[0] + 0.5)] = 1
            frames.append(m)
        frames.append([[0, 0, 0, 0, 0, 0, 0, 0]] * 8)

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

    # RL Dueling Dragons (two serpents weave past each other)
    elif var == "rl_dragons":
        delay = 0.07
        frames = []
        for t in range(32):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            hx = t * 0.4 - 1
            for c in range(8):
                if hx - 4 <= c <= hx:
                    ya = 3.5 + 3 * math.sin(c * 0.9 + t * 0.3)
                    yb = 3.5 + 3 * math.sin(c * 0.9 + t * 0.3 + 3.14)
                    m[int(ya + 0.5)][c] = 1
                    m[int(yb + 0.5)][c] = 1
            frames.append(m)
        frames.append([[0, 0, 0, 0, 0, 0, 0, 0]] * 8)

    # RL Chromatic Hollow (whirlwind: a spinning tornado)
    elif var == "rl_whirlwind":
        delay = 0.07
        frames = []
        for t in range(30):
            m = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]
            for r in range(8):
                amp = 0.6 + (7 - r) * 0.4
                ang = t * 0.6 + r * 0.9
                for f in (3.5 + amp * math.sin(ang), 3.5 + amp * math.sin(ang + 3.14)):
                    if 0 <= f <= 7:
                        m[r][int(f + 0.5)] = 1
            frames.append(m)
        frames.append([[0, 0, 0, 0, 0, 0, 0, 0]] * 8)

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