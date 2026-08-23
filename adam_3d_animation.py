from manim import *
import numpy as np

class Adam3DScene(ThreeDScene):
    def construct(self):
        self.camera.background_color = "#0e0e0e"

        # 3D Camera initial angle
        self.set_camera_orientation(phi=68 * DEGREES, theta=-55 * DEGREES, zoom=1.1)

        # 3D Coordinate Axes
        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            z_range=[0, 5, 1],
            x_length=6.5,
            y_length=5.0,
            z_length=2.8,
            axis_config={"color": "#4a6572", "stroke_width": 1.5},
        )
        axes.shift(DOWN * 0.4)

        # Ravine function: steep in y, gentle in x
        def loss_func(u, v):
            z = 0.12 * (u ** 2) + 0.85 * (v ** 2)
            return np.array([u, v, z])

        # 3D Surface Mesh
        surface = Surface(
            lambda u, v: axes.c2p(*loss_func(u, v)),
            u_range=[-3.6, 3.6],
            v_range=[-2.3, 2.3],
            resolution=(20, 20),
            should_make_jagged=False,
            stroke_color="#3498db",
            stroke_width=0.8,
            stroke_opacity=0.7,
            fill_color="#1a365d",
            fill_opacity=0.5,
        )

        target_star = Dot3D(point=axes.c2p(0, 0, 0), color=YELLOW, radius=0.14, resolution=(8, 8))

        # Pinned 2D HUD text (stays permanently fixed in screen space)
        title = Text("3D Loss Surface: Adam vs. SGD Dynamics", font="Helvetica", font_size=22, color=WHITE)
        title.to_edge(UP, buff=0.35)

        sgd_tag = Text("● Standard SGD (Violent Ravine Oscillation)", font="Helvetica", font_size=13, color="#e74c3c")
        adam_tag = Text("● Adam (Adaptive Ridge Descent)", font="Helvetica", font_size=13, color="#2ecc71")
        legend = VGroup(sgd_tag, adam_tag).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        legend.to_corner(UL, buff=0.45).shift(DOWN * 0.45)

        self.add_fixed_in_frame_mobjects(title, legend)

        # Reveal 3D landscape
        self.play(Create(axes), Create(surface), FadeIn(target_star), run_time=2.0)

        # 1. SGD trajectory with sharp, prominent wall-to-wall zig-zag bounce
        start_x, start_y = -3.4, 2.1
        sgd_x, sgd_y = start_x, start_y
        sgd_coords = []
        for i in range(24):
            z = loss_func(sgd_x, sgd_y)[2]
            sgd_coords.append(axes.c2p(sgd_x, sgd_y, z))
            sgd_x += 0.16
            sgd_y = -0.87 * sgd_y  # Alternating violent oscillation across the steep ravine

        # 2. Adam trajectory (damps y-axis variance rapidly, glides smoothly down center)
        adam_x, adam_y = start_x, start_y
        m_x, m_y = 0.0, 0.0
        v_x, v_y = 0.0, 0.0
        b1, b2, eps = 0.9, 0.999, 1e-8
        adam_lr = 0.28
        adam_coords = []
        for step in range(1, 38):
            z = loss_func(adam_x, adam_y)[2]
            adam_coords.append(axes.c2p(adam_x, adam_y, z))
            gx = 0.24 * adam_x
            gy = 1.70 * adam_y

            m_x = b1 * m_x + (1 - b1) * gx
            m_y = b1 * m_y + (1 - b1) * gy
            v_x = b2 * v_x + (1 - b2) * (gx ** 2)
            v_y = b2 * v_y + (1 - b2) * (gy ** 2)

            m_x_hat = m_x / (1 - b1 ** step)
            m_y_hat = m_y / (1 - b1 ** step)
            v_x_hat = v_x / (1 - b2 ** step)
            v_y_hat = v_y / (1 - b2 ** step)

            adam_x -= adam_lr * m_x_hat / (np.sqrt(v_x_hat) + eps)
            adam_y -= adam_lr * m_y_hat / (np.sqrt(v_y_hat) + eps)

        # 3D Sphere Particles
        sgd_sphere = Dot3D(point=sgd_coords[0], color="#e74c3c", radius=0.13, resolution=(8, 8))
        adam_sphere = Dot3D(point=adam_coords[0], color="#2ecc71", radius=0.13, resolution=(8, 8))

        sgd_3d_path = VMobject(color="#e74c3c", stroke_width=3.4, stroke_opacity=0.95)
        sgd_3d_path.set_points_as_corners(sgd_coords)

        adam_3d_path = VMobject(color="#2ecc71", stroke_width=4.0, stroke_opacity=0.95)
        adam_3d_path.set_points_as_corners(adam_coords)

        self.play(FadeIn(sgd_sphere), FadeIn(adam_sphere), run_time=0.8)

        # Start 3D camera rotation around the surface
        self.begin_ambient_camera_rotation(rate=0.12)

        # Animate particles descending the 3D surface
        self.play(
            MoveAlongPath(sgd_sphere, sgd_3d_path, rate_func=linear, run_time=12.0),
            Create(sgd_3d_path, rate_func=linear, run_time=12.0),
            MoveAlongPath(adam_sphere, adam_3d_path, rate_func=linear, run_time=12.0),
            Create(adam_3d_path, rate_func=linear, run_time=12.0),
        )

        self.stop_ambient_camera_rotation()
        self.wait(2.0)
