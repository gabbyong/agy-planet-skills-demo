from manim import *
import numpy as np

class AdamOptimizerScene(Scene):
    def construct(self):
        self.camera.background_color = "#0e0e0e"

        # Title
        title = Text("Adam vs. SGD: Navigating Loss Landscapes", font="Helvetica", font_size=26, color=WHITE)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.8)

        # Coordinate plane for 2D loss ravine: f(x, y) = 0.1 * x^2 + 1.5 * y^2
        plane = NumberPlane(
            x_range=[-6, 6, 2],
            y_range=[-3, 3, 1],
            x_length=6.2,
            y_length=4.0,
            background_line_style={"stroke_color": "#2c3e50", "stroke_width": 1, "stroke_opacity": 0.4},
            axis_config={"color": "#7f8c8d", "stroke_width": 1.5},
        )
        plane.shift(LEFT * 3.3 + DOWN * 0.3)

        # Elliptical Contours of the ravine
        contours = VGroup()
        for c in [0.6, 1.3, 2.4, 3.8, 5.5]:
            rx = np.sqrt(c / 0.1) * (6.2 / 12)
            ry = np.sqrt(c / 1.5) * (4.0 / 6)
            ellipse = Ellipse(width=2*rx, height=2*ry, color="#34495e", stroke_width=1.2)
            ellipse.move_to(plane.c2p(0, 0))
            contours.add(ellipse)

        min_star = Star(n=5, outer_radius=0.15, inner_radius=0.07, color=YELLOW, fill_color=YELLOW, fill_opacity=1.0)
        min_star.move_to(plane.c2p(0, 0))

        landscape_label = Text("Loss Surface: f(x,y) = 0.1x² + 1.5y²", font="Helvetica", font_size=13, color="#95a5a6")
        landscape_label.next_to(plane, DOWN, buff=0.15)

        self.play(Create(plane), Create(contours), FadeIn(min_star), Write(landscape_label), run_time=1.0)

        # Formula Card on the right
        formula_box = RoundedRectangle(corner_radius=0.15, height=4.0, width=5.6, color="#2c3e50", stroke_width=1.5, fill_color="#161616", fill_opacity=0.95)
        formula_box.shift(RIGHT * 3.4 + DOWN * 0.3)

        box_title = Text("Adam Adaptive Scaling", font="Helvetica", font_size=17, color="#5dade2")

        m_eq = Text("m_t = β₁·m_{t-1} + (1 - β₁)·g_t", font="Helvetica", font_size=14, color="#f39c12")
        m_desc = Text("Momentum: Smooths oscillations", font="Helvetica", font_size=11, color="#bdc3c7")

        v_eq = Text("v_t = β₂·v_{t-1} + (1 - β₂)·g_t²", font="Helvetica", font_size=14, color="#2ecc71")
        v_desc = Text("Variance: Tracks gradient scale", font="Helvetica", font_size=11, color="#bdc3c7")

        update_eq = Text("θ_{t+1} = θ_t - η · m_t / (√v_t + ε)", font="Helvetica", font_size=15, color=WHITE)
        update_desc = Text("Damps steep y-axis, accelerates shallow x-axis", font="Helvetica", font_size=11, color="#1abc9c")

        math_group = VGroup(
            box_title,
            m_eq, m_desc,
            v_eq, v_desc,
            update_eq, update_desc
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        math_group.move_to(formula_box.get_center())

        self.play(FadeIn(formula_box), FadeIn(math_group), run_time=0.9)

        # Legend
        sgd_dot_icon = Dot(color="#e74c3c", radius=0.07)
        sgd_text = Text("Standard SGD (Oscillates violently)", font="Helvetica", font_size=12, color="#e74c3c")
        sgd_legend = VGroup(sgd_dot_icon, sgd_text).arrange(RIGHT, buff=0.12)

        adam_dot_icon = Dot(color="#2ecc71", radius=0.07)
        adam_text = Text("Adam (Direct glide to minimum)", font="Helvetica", font_size=12, color="#2ecc71")
        adam_legend = VGroup(adam_dot_icon, adam_text).arrange(RIGHT, buff=0.12)

        legend = VGroup(sgd_legend, adam_legend).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        legend.next_to(title, DOWN, buff=0.15).align_to(plane, LEFT)
        self.play(FadeIn(legend), run_time=0.6)

        # Compute trajectories
        start_x, start_y = -4.6, 2.3

        # SGD trajectory (large oscillations on steep y-axis)
        sgd_x, sgd_y = start_x, start_y
        sgd_lr = 0.58
        sgd_pts = [plane.c2p(sgd_x, sgd_y)]
        for _ in range(16):
            gx = 0.2 * sgd_x
            gy = 3.0 * sgd_y
            sgd_x -= sgd_lr * gx
            sgd_y -= sgd_lr * gy
            sgd_pts.append(plane.c2p(sgd_x, sgd_y))

        # Adam trajectory (smooth adaptive descent)
        adam_x, adam_y = start_x, start_y
        m_x, m_y = 0.0, 0.0
        v_x, v_y = 0.0, 0.0
        b1, b2, eps = 0.9, 0.999, 1e-8
        adam_lr = 0.38
        adam_pts = [plane.c2p(adam_x, adam_y)]
        for step in range(1, 20):
            gx = 0.2 * adam_x
            gy = 3.0 * adam_y

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
            adam_pts.append(plane.c2p(adam_x, adam_y))

        # Animated dots and paths
        sgd_dot = Dot(point=plane.c2p(start_x, start_y), color="#e74c3c", radius=0.1)
        adam_dot = Dot(point=plane.c2p(start_x, start_y), color="#2ecc71", radius=0.1)

        sgd_path = VMobject(color="#e74c3c", stroke_width=2.5, stroke_opacity=0.85)
        sgd_path.set_points_as_corners(sgd_pts)

        adam_path = VMobject(color="#2ecc71", stroke_width=3.0, stroke_opacity=0.95)
        adam_path.set_points_as_corners(adam_pts)

        self.play(FadeIn(sgd_dot), FadeIn(adam_dot), run_time=0.4)

        # Animate both running simultaneously
        self.play(
            MoveAlongPath(sgd_dot, sgd_path, rate_func=linear, run_time=4.0),
            Create(sgd_path, rate_func=linear, run_time=4.0),
            MoveAlongPath(adam_dot, adam_path, rate_func=linear, run_time=4.0),
            Create(adam_path, rate_func=linear, run_time=4.0),
        )

        callout = Text("Adam reaches the global minimum in 5 epochs!", font="Helvetica", font_size=13, color="#2ecc71")
        callout.next_to(min_star, UP, buff=0.2)
        self.play(FadeIn(callout), Flash(min_star, color=YELLOW, line_length=0.15), run_time=0.8)
        self.wait(1.5)
