"""
THE BACKROOMS — Level 0
A 3D first-person liminal horror game built with the Ursina engine (Panda3D).
Runs on macOS and Windows.

    Goal: find 8 bottles of Almond Water scattered through the endless
    yellow rooms, then no-clip back out of reality. Something else is
    wandering the halls. Don't let it find you.

    You see everything through the camcorder you're holding: CRT scanlines,
    tape grain, a blinking REC light. In some sectors the fluorescent
    lights are dead or dying — the camera compensates with gain, badly.

Controls:
    WASD / Arrows  - move          Mouse       - look around
    Left Shift     - sprint        Esc         - quit
"""

import random
import math
import os
import sys

# ----------------------------------------------------------------------------
# Procedurally generate the textures (wallpaper / carpet / ceiling) with PIL
# so the game ships as a single .py file with no asset downloads.
# ----------------------------------------------------------------------------
from PIL import Image, ImageDraw

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets_generated")
os.makedirs(ASSET_DIR, exist_ok=True)


def _noise_px(base, amount, rng):
    return tuple(
        max(0, min(255, c + rng.randint(-amount, amount))) for c in base
    )


def make_wallpaper(path):
    if os.path.exists(path):
        return
    rng = random.Random(7)
    w, h = 256, 256
    img = Image.new("RGB", (w, h))
    px = img.load()
    base = (196, 178, 100)                      # mustard wallpaper
    for y in range(h):
        for x in range(w):
            c = _noise_px(base, 6, rng)
            # faint vertical stripe pattern
            if x % 32 < 2:
                c = tuple(max(0, v - 10) for v in c)
            px[x, y] = c
    d = ImageDraw.Draw(img)
    # water stains near the bottom
    for _ in range(5):
        sx, sy = rng.randint(0, w), rng.randint(h - 70, h)
        r = rng.randint(12, 34)
        d.ellipse((sx - r, sy - r // 2, sx + r, sy + r // 2),
                  fill=(172, 152, 82))
    # dark strip at the very bottom (baseboard grime)
    d.rectangle((0, h - 8, w, h), fill=(150, 132, 70))
    img.save(path)


def make_carpet(path):
    if os.path.exists(path):
        return
    rng = random.Random(13)
    w, h = 256, 256
    img = Image.new("RGB", (w, h))
    px = img.load()
    base = (150, 132, 66)                       # damp mono-yellow carpet
    for y in range(h):
        for x in range(w):
            px[x, y] = _noise_px(base, 14, rng)
    d = ImageDraw.Draw(img)
    for _ in range(220):                        # carpet fiber speckle
        x, y = rng.randint(0, w - 1), rng.randint(0, h - 1)
        d.point((x, y), fill=(128, 112, 52))
    img.save(path)


def make_ceiling(path):
    if os.path.exists(path):
        return
    rng = random.Random(21)
    w, h = 256, 256
    img = Image.new("RGB", (w, h), (214, 208, 184))   # off-white tile
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = _noise_px((214, 208, 184), 5, rng)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w - 1, h - 1), outline=(150, 146, 128), width=3)
    img.save(path)


def make_lightpanel(path):
    if os.path.exists(path):
        return
    w, h = 128, 128
    img = Image.new("RGB", (w, h), (255, 252, 224))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w - 1, h - 1), outline=(180, 176, 150), width=4)
    for i in range(1, 4):                       # fluorescent tube lines
        d.line((10, i * h // 4, w - 10, i * h // 4), fill=(255, 255, 245), width=6)
    img.save(path)


def make_hum(path):
    """Generate a looping fluorescent-light hum as a WAV file."""
    if os.path.exists(path):
        return
    try:
        import wave, struct
        rate = 22050
        secs = 4
        n = rate * secs
        rng = random.Random(3)
        frames = bytearray()
        for i in range(n):
            t = i / rate
            v = (0.20 * math.sin(2 * math.pi * 120 * t)
                 + 0.10 * math.sin(2 * math.pi * 240 * t)
                 + 0.05 * math.sin(2 * math.pi * 60 * t)
                 + 0.03 * (rng.random() * 2 - 1))
            # fade the loop seam
            edge = min(i, n - i) / (rate * 0.05)
            v *= min(1.0, edge)
            frames += struct.pack("<h", int(max(-1, min(1, v)) * 12000))
        with wave.open(path, "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(rate)
            f.writeframes(bytes(frames))
    except Exception:
        pass


def make_step(path):
    """Generate a soft, muffled carpet-footstep thump as a WAV file."""
    if os.path.exists(path):
        return
    try:
        import wave, struct
        rate = 22050
        n = int(rate * 0.16)
        rng = random.Random(9)
        frames = bytearray()
        low = 0.0
        for i in range(n):
            t = i / rate
            noise = rng.random() * 2 - 1
            low += (noise - low) * 0.08                 # cheap lowpass
            v = low * math.exp(-t * 34) * 1.8
            v += 0.4 * math.sin(2 * math.pi * 70 * t) * math.exp(-t * 40)
            frames += struct.pack("<h", int(max(-1, min(1, v)) * 9000))
        with wave.open(path, "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(rate)
            f.writeframes(bytes(frames))
    except Exception:
        pass


make_wallpaper(os.path.join(ASSET_DIR, "wallpaper.png"))
make_carpet(os.path.join(ASSET_DIR, "carpet.png"))
make_ceiling(os.path.join(ASSET_DIR, "ceiling.png"))
make_lightpanel(os.path.join(ASSET_DIR, "lightpanel.png"))
make_hum(os.path.join(ASSET_DIR, "hum.wav"))
make_step(os.path.join(ASSET_DIR, "step.wav"))

# ----------------------------------------------------------------------------
# Game
# ----------------------------------------------------------------------------
import platform

from ursina import (Ursina, Entity, Text, Audio, camera, color, window, scene,
                    held_keys, time, application, destroy, raycast, Vec3,
                    mouse, lerp, invoke, Texture, Shader)
from ursina.prefabs.first_person_controller import FirstPersonController

if platform.system() == "Darwin":
    # macOS's default OpenGL context only accepts GLSL <= 120, but Ursina's
    # built-in shaders are written for GLSL 130/140 -> nothing renders (blank
    # fog-colored window). Requesting a modern "core profile" context doesn't
    # help either: core rejects anything below GLSL 150 AND disables the
    # fixed-function fallbacks Panda3D relies on.
    #
    # Solution: stay on the legacy context and swap in functionally identical
    # shaders written in GLSL 120, which every Mac accepts. They declare the
    # same uniforms as Ursina's originals, so fog and texture scaling keep
    # working through Ursina's normal code paths.
    from ursina.shader import Shader as _Shader
    from ursina.vec2 import Vec2 as _Vec2
    import ursina.text as _utext

    _mac_unlit_fog_120 = _Shader(
        name="mac_unlit_fog_120", language=_Shader.GLSL,
        vertex="""#version 120
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;
attribute vec4 p3d_Color;
varying vec2 uvs;
varying vec4 vertex_color;
varying vec3 vertex_world_position;
uniform vec2 texture_scale;
uniform vec2 texture_offset;
void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uvs = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
    vertex_color = p3d_Color;
    vertex_world_position = (p3d_ModelMatrix * p3d_Vertex).xyz;
}
""",
        fragment="""#version 120
uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
varying vec2 uvs;
varying vec4 vertex_color;
varying vec3 vertex_world_position;
uniform vec3 camera_world_position;
uniform vec4 fog_color;
uniform float fog_start;
uniform float fog_end;
void main() {
    vec4 col = texture2D(p3d_Texture0, uvs) * p3d_ColorScale * vertex_color;
    float dist = length(vertex_world_position - camera_world_position);
    float t = clamp(dist / (fog_end - fog_start), 0.0, 1.0);
    col.rgb = mix(col.rgb, fog_color.rgb, t * fog_color.a);
    gl_FragColor = col;
}
""",
        default_input={
            "texture_scale": _Vec2(1, 1),
            "texture_offset": _Vec2(0.0, 0.0),
            "fog_color": color.clear,
            "fog_start": 10,
            "fog_end": 100,
            "camera_world_position": Vec3(0, 0, 0),
        },
    )
    _mac_unlit_fog_120.continuous_input["camera_world_position"] = (
        lambda: camera.world_position)
    Entity.default_shader = _mac_unlit_fog_120

    _mac_text_120 = _Shader(
        name="mac_text_120", language=_Shader.GLSL,
        vertex="""#version 120
uniform mat4 p3d_ModelViewProjectionMatrix;
attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;
attribute vec4 p3d_Color;
varying vec2 uvs;
varying vec4 vertex_color;
void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uvs = p3d_MultiTexCoord0;
    vertex_color = p3d_Color;
}
""",
        fragment="""#version 120
uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
varying vec2 uvs;
varying vec4 vertex_color;
void main() {
    float dist = texture2D(p3d_Texture0, uvs).a;
    float w = fwidth(dist);
    float alpha = smoothstep(0.5 - w, 0.5 + w, dist);
    vec4 col = vertex_color * p3d_ColorScale;
    gl_FragColor = vec4(col.rgb, col.a * alpha);
}
""",
        default_input={},
    )
    _utext.text_shader = _mac_text_120

# NOTE: do not pass fullscreen=False here — in ursina 8.3 an explicit
# fullscreen kwarg silently breaks all camera.ui rendering (windowed is
# already the default).
app = Ursina(title="The Backrooms — Level 0", borderless=False,
             vsync=True, development_mode=False)
window.color = color.rgb32(8, 8, 4)
window.fps_counter.enabled = False
window.exit_button.visible = False

# ---------------------------- CRT / camcorder post-process ------------------
# The whole scene renders into a texture, then this shader replays it like
# footage off a worn-out camcorder: barrel distortion, chromatic fringing,
# scanlines, tape grain (which gets worse in the dark, like real sensor gain),
# and a slow luminance roll. GLSL 120 so it runs on macOS's legacy GL context.
_crt_shader = Shader(
    name="crt_cam", language=Shader.GLSL,
    vertex="""#version 120
uniform mat4 p3d_ModelViewProjectionMatrix;
attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;
varying vec2 uv;
void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uv = p3d_MultiTexCoord0;
}
""",
    fragment="""#version 120
uniform sampler2D tex;
uniform float osg_FrameTime;
uniform float darkness;
varying vec2 uv;

float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    float t = osg_FrameTime;
    vec2 cuv = uv - 0.5;
    float r2 = dot(cuv, cuv);
    vec2 duv = cuv * (1.0 + 0.11 * r2) + 0.5;          // barrel distortion
    if (duv.x < 0.0 || duv.x > 1.0 || duv.y < 0.0 || duv.y > 1.0) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    // interlace jitter: scanline rows shiver sideways a little
    duv.x += (rand(vec2(floor(duv.y * 240.0), floor(t * 15.0))) - 0.5) * 0.0014;
    // chromatic aberration, stronger toward the edges
    vec2 ca = cuv * 0.0038;
    vec3 col = vec3(texture2D(tex, duv + ca).r,
                    texture2D(tex, duv).g,
                    texture2D(tex, duv - ca).b);
    // broken-light zones: the camera loses exposure and gains noise
    col *= 1.0 - darkness * 0.62;
    // camcorder color: slightly washed out, lifted blacks
    float lum = dot(col, vec3(0.299, 0.587, 0.114));
    col = mix(col, vec3(lum), 0.18);
    col = col * 0.94 + 0.025;
    // scanlines + slow vertical luminance roll
    col *= 0.86 + 0.14 * sin(duv.y * 780.0);
    col *= 1.0 + 0.035 * sin(duv.y * 3.0 - t * 1.4);
    // tape grain — much heavier where it's dark
    float g = rand(duv * 371.0 + fract(t) * 91.0) - 0.5;
    col += g * (0.045 + darkness * 0.26);
    // vignette + tiny global flicker
    col *= 1.0 - r2 * 0.85;
    col *= 0.985 + 0.015 * rand(vec2(floor(t * 24.0), 0.5));
    gl_FragColor = vec4(col, 1.0);
}
""",
    default_input={"darkness": 0.0},
)

crt_ok = False
if not os.environ.get("BR_NO_CRT"):
    try:
        camera.shader = _crt_shader
        camera.set_shader_input("darkness", 0.0)
        crt_ok = True
    except Exception:
        crt_ok = False

# point Ursina's asset loader at our generated assets; built-in models and
# fonts still resolve through Ursina's internal fallback folders
from pathlib import Path
application.asset_folder = Path(ASSET_DIR)

def TEX(name):
    return name.rsplit('.', 1)[0]   # reference generated textures by name

CELL = 4          # world units per maze cell
GRID = 32         # maze is GRID x GRID cells
WALL_H = 3.4      # wall height
BOTTLES_TO_WIN = 8

random.seed()

# ---------------------------- map generation --------------------------------
def generate_map():
    """1 = wall, 0 = open. Sparse rectangular wall chunks -> backrooms rooms."""
    g = [[0] * GRID for _ in range(GRID)]
    for i in range(GRID):                          # outer border
        g[0][i] = g[GRID - 1][i] = g[i][0] = g[i][GRID - 1] = 1
    rng = random.Random()
    # scatter wall segments (horizontal & vertical runs) and pillars
    for _ in range(int(GRID * GRID * 0.055)):
        x, z = rng.randint(2, GRID - 3), rng.randint(2, GRID - 3)
        length = rng.randint(2, 6)
        if rng.random() < 0.5:
            for dx in range(length):
                if x + dx < GRID - 1:
                    g[z][x + dx] = 1
        else:
            for dz in range(length):
                if z + dz < GRID - 1:
                    g[z + dz][x] = 1
    for _ in range(int(GRID * GRID * 0.02)):       # lone pillars
        g[rng.randint(2, GRID - 3)][rng.randint(2, GRID - 3)] = 1
    # guarantee the spawn area is open
    for z in range(GRID // 2 - 2, GRID // 2 + 3):
        for x in range(GRID // 2 - 2, GRID // 2 + 3):
            g[z][x] = 0
    # flood-fill from spawn; open up unreachable pockets
    seen = [[False] * GRID for _ in range(GRID)]
    stack = [(GRID // 2, GRID // 2)]
    while stack:
        cx, cz = stack.pop()
        if cx < 0 or cz < 0 or cx >= GRID or cz >= GRID:
            continue
        if seen[cz][cx] or g[cz][cx] == 1:
            continue
        seen[cz][cx] = True
        stack += [(cx + 1, cz), (cx - 1, cz), (cx, cz + 1), (cx, cz - 1)]
    for z in range(1, GRID - 1):
        for x in range(1, GRID - 1):
            if g[z][x] == 0 and not seen[z][x]:
                g[z][x] = 1                        # wall off dead pockets
    return g


MAP = generate_map()


def cell_to_world(cx, cz):
    return (cx - GRID / 2) * CELL, (cz - GRID / 2) * CELL


def world_to_cell(x, z):
    return int(round(x / CELL + GRID / 2)), int(round(z / CELL + GRID / 2))


def is_open(cx, cz):
    return 0 <= cx < GRID and 0 <= cz < GRID and MAP[cz][cx] == 0


# ---------------------------- build the world -------------------------------
SIZE = GRID * CELL

floor = Entity(model="plane", scale=(SIZE, 1, SIZE),
               texture=TEX("carpet.png"), texture_scale=(GRID, GRID),
               collider="box", color=color.rgb32(215, 205, 170))

ceiling = Entity(model="plane", scale=(SIZE, 1, SIZE), rotation_x=180,
                 y=WALL_H, texture=TEX("ceiling.png"),
                 texture_scale=(GRID * 2, GRID * 2),
                 color=color.rgb32(205, 200, 178))

# merge horizontal runs of wall cells into single entities (performance)
wall_entities = []
for z in range(GRID):
    x = 0
    while x < GRID:
        if MAP[z][x] == 1:
            start = x
            while x < GRID and MAP[z][x] == 1:
                x += 1
            run = x - start
            wx, wz = cell_to_world(start + (run - 1) / 2, z)
            wall_entities.append(Entity(
                model="cube", collider="box",
                position=(wx, WALL_H / 2, wz),
                scale=(run * CELL, WALL_H, CELL),
                texture=TEX("wallpaper.png"),
                texture_scale=(run * 2, 1.6),
                color=color.rgb32(225, 210, 158)))
        else:
            x += 1

# fluorescent light panels on the ceiling — most work; some don't
class LightPanel(Entity):
    BRIGHT = color.rgb32(255, 255, 235)
    DIM = color.rgb32(92, 86, 70)
    DEAD = color.rgb32(48, 44, 38)

    def __init__(self, cell, **kwargs):
        super().__init__(model="cube", scale=(1.9, 0.06, 0.9),
                         texture=TEX("lightpanel.png"),
                         color=self.BRIGHT, **kwargs)
        self.cell = cell
        self.mode = "on"                 # on | flicker | dead
        self.lit = True
        self.t = random.uniform(0, 2)

    def set_mode(self, mode):
        self.mode = mode
        if mode == "dead":
            self.color = self.DEAD
            self.lit = False

    def tick(self, dt, blackout):
        if self.mode == "dead":
            return
        if blackout:
            if self.lit:
                self.lit = False
                self.color = self.DIM
            return
        if self.mode == "flicker":
            self.t -= dt
            if self.t <= 0:
                self.lit = not self.lit
                # brief stutters off, longer stretches on — a dying tube
                self.t = (random.uniform(0.04, 0.20) if not self.lit
                          else random.uniform(0.3, 2.6))
                self.color = self.BRIGHT if self.lit else self.DIM
        elif not self.lit:               # blackout just ended
            self.lit = True
            self.color = self.BRIGHT


panels = []
light_cells = []
for z in range(2, GRID - 2, 3):
    for x in range(2, GRID - 2, 3):
        if is_open(x, z):
            wx, wz = cell_to_world(x, z)
            panels.append(LightPanel((x, z),
                                     position=(wx, WALL_H - 0.03, wz)))
            light_cells.append((x, z))

# dark zones — clusters of dead lights that swallow whole rooms, with a
# flickering fringe around each so you see the failure coming
dark_zones = []
_zrng = random.Random()
_cands = [c for c in light_cells
          if abs(c[0] - GRID // 2) + abs(c[1] - GRID // 2) > 9]
_zrng.shuffle(_cands)
for c in _cands:
    if len(dark_zones) >= 3:
        break
    if all(abs(c[0] - d[0]) + abs(c[1] - d[1]) > 12 for d in dark_zones):
        dark_zones.append(c)
if not dark_zones:                       # tiny maps: just pick something
    dark_zones.append(_cands[0] if _cands else (2, 2))

DARK_R = 4.5      # cells: lights fully dead
EDGE_R = 7.5      # cells: flickering fringe
for p in panels:
    dmin = min(math.dist(p.cell, dz) for dz in dark_zones)
    if dmin < DARK_R:
        p.set_mode("dead")
    elif dmin < EDGE_R:
        p.set_mode("flicker")
    elif random.random() < 0.10:
        p.set_mode("flicker")            # the odd faulty tube anywhere
    elif random.random() < 0.04:
        p.set_mode("dead")

# fog — the key to the liminal look
scene.fog_color = color.rgb32(52, 46, 20)
scene.fog_density = 0.048

# ---------------------------- player ----------------------------------------
# The FPC only handles gravity; rotation and translation are done manually in
# update() so the body has inertia and the head lags the mouse — human, not
# turret. speed=0 and sensitivity=0 disable the FPC's own handling.
player = FirstPersonController(y=1.2, speed=0, mouse_sensitivity=Vec3(0, 0, 0))
player.cursor.visible = False
player.gravity = 0.6
camera.fov = 82

BASE_SPEED, SPRINT_SPEED = 5.0, 8.2
LOOK_SENS = 40
stamina = 100.0

vel = Vec3(0, 0, 0)          # smoothed horizontal velocity (world space)
yaw_t = 0.0                  # where the mouse wants to look;
pitch_t = 0.0                # the head eases toward it with a slight lag

# ---------------------------- almond water pickups --------------------------
bottles = []


def spawn_bottles():
    rng = random.Random()
    placed = 0
    tries = 0
    while placed < BOTTLES_TO_WIN and tries < 4000:
        tries += 1
        cx, cz = rng.randint(2, GRID - 3), rng.randint(2, GRID - 3)
        if not is_open(cx, cz):
            continue
        if abs(cx - GRID // 2) + abs(cz - GRID // 2) < 6:
            continue                                # not too close to spawn
        wx, wz = cell_to_world(cx, cz)
        b = Entity(model="cube", position=(wx, 0.55, wz),
                   scale=(0.22, 0.5, 0.22),
                   color=color.rgb32(240, 235, 200))
        Entity(parent=b, model="cube", y=0.62, scale=(0.5, 0.25, 0.5),
               color=color.rgb32(90, 70, 30))  # cap
        bottles.append(b)
        placed += 1


spawn_bottles()

# ---------------------------- the entity ------------------------------------
class Wanderer(Entity):
    """A dark figure that roams the halls and chases on line of sight."""

    def __init__(self):
        super().__init__(model="cube", scale=(0.7, 2.6, 0.7),
                         color=color.rgb32(12, 10, 6))
        Entity(parent=self, model="sphere", y=0.55, scale=(0.9, 0.35, 0.9),
               color=color.rgb32(6, 5, 3))
        self.speed_wander = 2.2
        self.speed_chase = 6.4
        self.state = "wander"
        self.dir = Vec3(1, 0, 0)
        self.repick_t = 0
        self.respawn_far()

    def respawn_far(self):
        rng = random.Random()
        while True:
            cx, cz = rng.randint(2, GRID - 3), rng.randint(2, GRID - 3)
            if is_open(cx, cz) and abs(cx - GRID // 2) + abs(cz - GRID // 2) > 18:
                wx, wz = cell_to_world(cx, cz)
                self.position = Vec3(wx, 1.3, wz)
                return

    def can_see_player(self):
        to_p = player.position - self.position
        dist = to_p.length()
        if dist > 26:
            return False
        hit = raycast(self.world_position + Vec3(0, 0.5, 0),
                      to_p.normalized(), distance=dist,
                      ignore=[self, *self.children, *bottles], debug=False)
        return not hit.hit or hit.entity == player

    def update(self):
        if game_state["mode"] != "play":
            return
        dt = time.dt
        if self.can_see_player():
            self.state = "chase"
        elif self.state == "chase" and not self.can_see_player():
            self.state = "wander"

        if self.state == "chase":
            d = (player.position - self.position)
            d.y = 0
            if d.length() > 0.1:
                step = d.normalized() * self.speed_chase * dt
                self._move(step)
        else:
            self.repick_t -= dt
            if self.repick_t <= 0:
                self.repick_t = random.uniform(1.5, 4.0)
                choices = [Vec3(1, 0, 0), Vec3(-1, 0, 0),
                           Vec3(0, 0, 1), Vec3(0, 0, -1)]
                self.dir = random.choice(choices)
            self._move(self.dir * self.speed_wander * dt)

        # caught the player?
        flat = player.position - self.position
        flat.y = 0
        if flat.length() < 1.0:
            end_game(False)

    def _move(self, step):
        ahead = raycast(self.world_position + Vec3(0, 0.2, 0),
                        step.normalized(), distance=0.9,
                        ignore=[self, *self.children, player, *bottles])
        if ahead.hit:
            self.repick_t = 0                       # pick a new direction
            if self.state == "chase":               # slide along walls
                for alt in (Vec3(step.z, 0, -step.x), Vec3(-step.z, 0, step.x)):
                    a = raycast(self.world_position + Vec3(0, 0.2, 0),
                                alt.normalized(), distance=0.9,
                                ignore=[self, *self.children, player, *bottles])
                    if not a.hit:
                        self.position += alt
                        return
            return
        self.position += step


wanderer = Wanderer()

# ---------------------------- UI --------------------------------------------
game_state = {"mode": "play", "collected": 0}

counter = Text(text="", origin=(0.5, -0.5), position=(0.62, -0.44),
               scale=1.1, color=color.rgb32(235, 220, 160))
stamina_bg = Entity(parent=camera.ui, model="quad", scale=(0.26, 0.018),
                    position=(-0.62, -0.45), color=color.rgb32(30, 28, 14))
stamina_bar = Entity(parent=camera.ui, model="quad", scale=(0.26, 0.018),
                     position=(-0.62, -0.45), color=color.rgb32(210, 190, 110))
hint = Text(text="find the almond water  ·  do not let it see you",
            origin=(0, 0), y=0.42, scale=0.85,
            color=color.rgb32(180, 165, 110))
invoke(setattr, hint, "enabled", False, delay=7)

vignette = Entity(parent=camera.ui, model="quad", scale=(2.5, 1.5),
                  color=color.rgba32(0, 0, 0, 60))

danger_flash = Entity(parent=camera.ui, model="quad", scale=(2.5, 1.5),
                      color=color.rgba32(120, 0, 0, 0))

# fallback darkness overlay, only used if the CRT shader isn't running
dark_overlay = Entity(parent=camera.ui, model="quad", scale=(2.5, 1.5),
                      color=color.rgba32(0, 0, 0, 0))

# ---- camcorder OSD (drawn on top of the CRT image, like a real viewfinder) --
UI_INK = color.rgba32(235, 235, 235, 215)
UI_DIM = color.rgba32(220, 220, 220, 110)

rec_dot = Entity(parent=camera.ui, model="circle", scale=0.016,
                 position=(-0.72, 0.432), color=color.rgb32(255, 45, 30))
rec_text = Text(text="REC", position=(-0.70, 0.447), scale=1.1, color=UI_INK)
timecode = Text(text="00:00:00:00", position=(0.47, 0.447), scale=1.0,
                color=UI_INK)
date_text = Text(text="JUL 19 2026", position=(-0.72, -0.395), scale=0.85,
                 color=UI_INK)
mode_text = Text(text="SP  AUTO EXP", position=(0.47, -0.395), scale=0.8,
                 color=UI_DIM)

# battery: shell + tip + two of three bars left
Entity(parent=camera.ui, model="quad", scale=(0.062, 0.028),
       position=(0.68, 0.398), z=-0.1, color=color.rgba32(15, 15, 15, 160))
Entity(parent=camera.ui, model="quad", scale=(0.006, 0.014),
       position=(0.715, 0.398), z=-0.1, color=color.rgba32(15, 15, 15, 160))
for i in range(2):
    Entity(parent=camera.ui, model="quad", scale=(0.015, 0.02),
           position=(0.68 - 0.018 + i * 0.018, 0.398), z=-0.105,
           color=color.rgba32(235, 235, 235, 200))

# viewfinder corner brackets
for sx in (-1, 1):
    for sy in (-1, 1):
        bx, by = 0.78 * sx, 0.40 * sy
        Entity(parent=camera.ui, model="quad", scale=(0.06, 0.0035),
               position=(bx - sx * 0.03, by), z=-0.1, color=UI_DIM)
        Entity(parent=camera.ui, model="quad", scale=(0.0035, 0.06),
               position=(bx, by - sy * 0.03), z=-0.1, color=UI_DIM)

rec_time = random.uniform(600, 4200)     # the tape has been rolling a while
blink_t = 0.0

# explicit UI depth layers: full-screen tints behind, HUD/OSD in front
# (same-z ui quads z-fight on macOS — the stamina bar vanished behind its bg)
vignette.z = -0.01
danger_flash.z = -0.02
dark_overlay.z = -0.03
for _e in (counter, hint,
           rec_dot, rec_text, timecode, date_text, mode_text):
    _e.z = -0.1
stamina_bg.z = -0.09
stamina_bar.z = -0.095

end_text = Text(text="", origin=(0, 0), scale=1.6, enabled=False)
sub_text = Text(text="", origin=(0, 0), y=-0.1, scale=0.9, enabled=False)
end_text.z = sub_text.z = -0.1


def update_counter():
    counter.text = f"almond water  {game_state['collected']} / {BOTTLES_TO_WIN}"


update_counter()

# ambient hum
try:
    hum = Audio("hum", loop=True, autoplay=True, volume=0.35)
    if not hum.clip:
        hum = None
except Exception:
    hum = None

# footsteps
try:
    step_snd = Audio("step", loop=False, autoplay=False, volume=0.4)
    if not step_snd.clip:
        step_snd = None
except Exception:
    step_snd = None


def end_game(won):
    game_state["mode"] = "end"
    player.enabled = False
    mouse.locked = False
    end_text.enabled = sub_text.enabled = True
    if won:
        end_text.text = "YOU NO-CLIPPED OUT"
        end_text.color = color.rgb32(230, 220, 170)
        sub_text.text = "reality accepted you back  ·  press R to descend again  ·  Esc to quit"
    else:
        end_text.text = "IT FOUND YOU"
        end_text.color = color.rgb32(200, 40, 30)
        sub_text.text = f"almond water found: {game_state['collected']}  ·  press R to wake up on the carpet again  ·  Esc to quit"
        danger_flash.color = color.rgba32(120, 0, 0, 90)


def restart():
    game_state["mode"] = "play"
    game_state["collected"] = 0
    update_counter()
    global stamina, vel, yaw_t, pitch_t
    stamina = 100
    vel = Vec3(0, 0, 0)
    yaw_t = pitch_t = 0.0
    player.rotation_y = 0
    player.camera_pivot.rotation_x = 0
    for b in bottles[:]:
        destroy(b)
    bottles.clear()
    spawn_bottles()
    player.position = Vec3(0, 1.2, 0)
    player.enabled = True
    mouse.locked = True
    wanderer.state = "wander"
    wanderer.respawn_far()
    end_text.enabled = sub_text.enabled = False
    danger_flash.color = color.rgba32(120, 0, 0, 0)


bob_t = 0.0
breathe_t = 0.0
last_bob = 0.0
darkness_now = 0.0
blackout_until = 0.0
next_blackout = random.uniform(18, 35)
game_t = 0.0


def update():
    global stamina, bob_t, breathe_t, last_bob, vel, yaw_t, pitch_t
    global darkness_now, blackout_until, next_blackout, game_t
    global rec_time, blink_t

    dt = time.dt
    game_t += dt
    if held_keys["escape"]:
        application.quit()

    # camcorder OSD: blinking REC dot + running timecode (HH:MM:SS:FF)
    rec_time += dt
    blink_t += dt
    if blink_t >= 0.55:
        blink_t = 0.0
        rec_dot.enabled = not rec_dot.enabled
    mm, ss = divmod(int(rec_time), 60)
    hh, mm = divmod(mm, 60)
    timecode.text = f"{hh:02d}:{mm:02d}:{ss:02d}:{int((rec_time % 1) * 30):02d}"

    if game_state["mode"] == "end":
        if held_keys["r"]:
            restart()
        return

    # ---- lights: flicker, dead zones, random blackouts ---------------------
    blackout = game_t < blackout_until
    if not blackout and game_t >= next_blackout:
        blackout_until = game_t + random.uniform(0.7, 2.2)
        next_blackout = blackout_until + random.uniform(20, 42)
        blackout = True
        if random.random() < 0.35:
            wanderer.respawn_far()      # when the lights come back, it's moved
    for p in panels:
        p.tick(dt, blackout)

    # how dark is it where the player stands?
    pcx = player.x / CELL + GRID / 2
    pcz = player.z / CELL + GRID / 2
    zone_d = min(math.dist((pcx, pcz), z) for z in dark_zones)
    target_dark = max(0.0, min(1.0, (EDGE_R - zone_d) / (EDGE_R - 2.0))) * 0.72
    if blackout:
        target_dark = max(target_dark, random.uniform(0.55, 0.8))
    darkness_now = lerp(darkness_now, target_dark, min(1, 5 * dt))
    if crt_ok:
        camera.set_shader_input("darkness", darkness_now)
    else:
        dark_overlay.color = color.rgba32(0, 0, 0, int(darkness_now * 195))

    # ---- look: the head eases toward the mouse instead of snapping ---------
    yaw_t += mouse.velocity[0] * LOOK_SENS
    pitch_t -= mouse.velocity[1] * LOOK_SENS
    pitch_t = max(-88, min(88, pitch_t))
    player.rotation_y = lerp(player.rotation_y, yaw_t, min(1, 14 * dt))
    player.camera_pivot.rotation_x = lerp(player.camera_pivot.rotation_x,
                                          pitch_t, min(1, 14 * dt))

    # ---- movement: acceleration, momentum, wall sliding ---------------------
    fwd = ((held_keys["w"] or held_keys["up arrow"])
           - (held_keys["s"] or held_keys["down arrow"]))
    strafe = ((held_keys["d"] or held_keys["right arrow"])
              - (held_keys["a"] or held_keys["left arrow"]))
    wish = player.forward * fwd + player.right * strafe
    wish.y = 0
    moving = wish.length() > 0.01
    if moving:
        wish = wish.normalized()
    sprinting = held_keys["left shift"] and moving and stamina > 0

    target_vel = wish * (SPRINT_SPEED if sprinting else BASE_SPEED) \
        if moving else Vec3(0, 0, 0)
    vel = lerp(vel, target_vel, min(1, (6.5 if moving else 9.0) * dt))
    speed_now = vel.length()
    if speed_now > 0.05:
        d = vel / speed_now
        origin = player.world_position + Vec3(0, 0.5, 0)
        hit = raycast(origin, d, distance=speed_now * dt + 0.35,
                      ignore=[player])
        if hit.hit:
            n = Vec3(hit.world_normal)
            n.y = 0
            if n.length() > 0.01:
                n = n.normalized()
                vel -= n * vel.dot(n)   # slide along the wall
                speed_now = vel.length()
                if speed_now > 0.05:
                    d = vel / speed_now
                    if raycast(origin, d, distance=speed_now * dt + 0.35,
                               ignore=[player]).hit:
                        vel = Vec3(0, 0, 0)
                        speed_now = 0.0
            else:
                vel = Vec3(0, 0, 0)
                speed_now = 0.0
        player.position += vel * dt

    stamina += (-26 if sprinting else 14) * dt
    stamina = max(0, min(100, stamina))
    stamina_bar.scale_x = 0.26 * (stamina / 100)
    stamina_bar.x = -0.62 - (0.26 - stamina_bar.scale_x) / 2

    # the world widens slightly when you run
    camera.fov = lerp(camera.fov, 88 if sprinting else 82, min(1, 4 * dt))

    # ---- head: bob, lateral sway, lean, breathing ---------------------------
    breathe_t += dt
    amp = min(1.0, speed_now / BASE_SPEED)
    if speed_now > 0.4:
        bob_t += dt * (7.5 + 7.5 * speed_now / SPRINT_SPEED)
    vert = math.sin(bob_t * 2.0)
    lat = math.sin(bob_t)
    camera.y = vert * 0.045 * amp + math.sin(breathe_t * 1.3) * 0.010
    camera.x = lat * 0.03 * amp
    turn_lag = max(-3.0, min(3.0, (yaw_t - player.rotation_y) * 0.10))
    camera.rotation_z = lerp(camera.rotation_z,
                             lat * 0.8 * amp + strafe * 1.2 * amp + turn_lag,
                             min(1, 8 * dt))
    # a footstep lands at the bottom of each bob cycle
    if step_snd and amp > 0.25 and vert < -0.86 and last_bob >= -0.86:
        step_snd.pitch = random.uniform(0.85, 1.15)
        step_snd.volume = 0.25 + 0.3 * (speed_now / SPRINT_SPEED)
        step_snd.play()
    last_bob = vert

    # bottle pickup
    for b in bottles[:]:
        d = player.position - b.position
        d.y = 0
        if d.length() < 1.1:
            bottles.remove(b)
            destroy(b)
            game_state["collected"] += 1
            update_counter()
            if game_state["collected"] >= BOTTLES_TO_WIN:
                end_game(True)
        else:
            b.rotation_y += 40 * dt

    # danger tint when the entity is close / chasing
    flat = player.position - wanderer.position
    flat.y = 0
    d = flat.length()
    if wanderer.state == "chase":
        a = max(0, min(90, (26 - d) * 5))
        danger_flash.color = color.rgba32(120, 0, 0, int(a))
        hum_base = 0.5
    else:
        danger_flash.color = color.rgba32(120, 0, 0, 0)
        hum_base = 0.35
    if hum:
        # the hum thins out where the lights are dead — worse than the noise
        hum.volume = hum_base * (1 - 0.6 * darkness_now)


# debug: BR_DEBUG_SHOT=/path/out.png -> save a framebuffer screenshot and quit
if os.environ.get("BR_DEBUG_SHOT"):
    def _debug_snap():
        application.base.screenshot(os.environ["BR_DEBUG_SHOT"],
                                    defaultFilename=False)
        application.quit()
    invoke(_debug_snap, delay=float(os.environ.get("BR_DEBUG_SHOT_DELAY", 6)))

app.run()
