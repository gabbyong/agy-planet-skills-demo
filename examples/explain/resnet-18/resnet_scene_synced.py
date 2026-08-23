from manim import *

class ResNetWalkthrough(Scene):
    def construct(self):
        self.camera.background_color = "#0e0e0e"

        # -------------------------------------------------------------
        # SEGMENT 1: Macro Architecture (~12.80s total)
        # -------------------------------------------------------------
        title = Text("ResNet-18 Architecture & Mechanics", font_size=28, color=WHITE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)

        stage_names = ["Stem\n3x3", "Stage 1\n64-d", "Stage 2\n128-d (↓2)", "Stage 3\n256-d (↓2)", "Stage 4\n512-d (↓2)", "GAP\n+ FC"]
        colors = [BLUE_D, BLUE_C, TEAL_C, GREEN_C, YELLOW_C, RED_C]
        boxes = VGroup()
        
        for i, (name, col) in enumerate(zip(stage_names, colors)):
            box = RoundedRectangle(corner_radius=0.1, height=1.05, width=1.55, color=col, fill_color=col, fill_opacity=0.25, stroke_width=2)
            lbl = Text(name, font_size=13, color=WHITE)
            lbl.move_to(box.get_center())
            boxes.add(VGroup(box, lbl))
            
        boxes.arrange(RIGHT, buff=0.25)
        boxes.shift(UP * 1.65)

        arrows = VGroup()
        for i in range(len(boxes) - 1):
            arr = Arrow(boxes[i].get_right(), boxes[i+1].get_left(), buff=0.05, color=GRAY_B, stroke_width=2.2, max_tip_length_to_length_ratio=0.3)
            arrows.add(arr)

        pipeline_lbl = Text("18-Layer Macro Topology (Stem + 8 Basic Blocks + Linear)", font_size=15, color=GRAY_A)
        pipeline_lbl.next_to(boxes, UP, buff=0.15)

        self.play(FadeIn(pipeline_lbl), LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.15), run_time=2.0)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.15), run_time=1.5)
        
        # Highlight channels doubling
        self.play(boxes[1:5].animate.set_stroke(YELLOW, width=3), run_time=1.5)
        self.play(boxes[1:5].animate.set_stroke(width=2), run_time=1.0)
        self.wait(5.80)

        # -------------------------------------------------------------
        # SEGMENT 2: Basic Block & Residual Mapping (~12.36s total)
        # -------------------------------------------------------------
        block_header = Text("Inside the Basic Residual Block: F(x) + x", font_size=20, color=YELLOW)
        block_header.shift(UP * 0.45)
        self.play(FadeIn(block_header), run_time=1.0)

        x_dot = Dot(LEFT * 4.6 + DOWN * 1.3, radius=0.1, color=BLUE)
        x_label = Text("x", font_size=20, color=BLUE).next_to(x_dot, LEFT, buff=0.12)

        conv1 = RoundedRectangle(corner_radius=0.1, height=0.85, width=1.55, color=BLUE_B, fill_color=BLUE_E, fill_opacity=0.4, stroke_width=2)
        conv1.move_to(LEFT * 2.0 + DOWN * 1.3)
        conv1_lbl = Text("Conv 3x3\n+ BN + ReLU", font_size=12, color=WHITE).move_to(conv1.get_center())
        arr_in_c1 = Arrow(x_dot.get_right(), conv1.get_left(), buff=0.06, color=WHITE, stroke_width=2.2)

        self.play(
            FadeIn(x_dot), FadeIn(x_label),
            Create(conv1), FadeIn(conv1_lbl), GrowArrow(arr_in_c1),
            run_time=2.0
        )

        conv2 = RoundedRectangle(corner_radius=0.1, height=0.85, width=1.55, color=BLUE_B, fill_color=BLUE_E, fill_opacity=0.4, stroke_width=2)
        conv2.move_to(RIGHT * 0.8 + DOWN * 1.3)
        conv2_lbl = Text("Conv 3x3\n+ BN", font_size=12, color=WHITE).move_to(conv2.get_center())
        arr_c1_c2 = Arrow(conv1.get_right(), conv2.get_left(), buff=0.06, color=WHITE, stroke_width=2.2)
        fx_lbl = Text("F(x) (Learned Residual Delta)", font_size=14, color=BLUE_C).next_to(conv2, DOWN, buff=0.22)

        self.play(
            Create(conv2), FadeIn(conv2_lbl), GrowArrow(arr_c1_c2),
            FadeIn(fx_lbl),
            run_time=2.5
        )
        self.wait(6.86)

        # -------------------------------------------------------------
        # SEGMENT 3: Identity Shortcut (~11.80s total)
        # -------------------------------------------------------------
        shortcut_start = x_dot.get_center()
        add_circle = Circle(radius=0.25, color=ORANGE, fill_color=ORANGE, fill_opacity=0.3, stroke_width=2.5)
        add_circle.move_to(RIGHT * 3.1 + DOWN * 1.3)
        add_sym = Text("+", font_size=22, color=ORANGE).move_to(add_circle.get_center())
        arr_c2_add = Arrow(conv2.get_right(), add_circle.get_left(), buff=0.06, color=WHITE, stroke_width=2.2)

        shortcut_end = add_circle.get_top()
        shortcut_path = ArcBetweenPoints(
            shortcut_start + UP * 0.12,
            shortcut_end,
            angle=-TAU/5.2,
            color=YELLOW,
            stroke_width=2.8
        )
        shortcut_lbl = Text("Identity Shortcut (x)", font_size=13, color=YELLOW).next_to(shortcut_path, UP, buff=0.08)

        self.play(
            Create(shortcut_path), FadeIn(shortcut_lbl),
            run_time=2.5
        )

        self.play(
            Create(add_circle), FadeIn(add_sym),
            GrowArrow(arr_c2_add),
            run_time=2.0
        )

        out_dot = Dot(RIGHT * 4.8 + DOWN * 1.3, radius=0.1, color=GREEN)
        out_label = Text("F(x) + x", font_size=18, color=GREEN).next_to(out_dot, RIGHT, buff=0.12)
        arr_add_out = Arrow(add_circle.get_right(), out_dot.get_left(), buff=0.06, color=GREEN, stroke_width=2.2)

        self.play(
            GrowArrow(arr_add_out), FadeIn(out_dot), FadeIn(out_label),
            run_time=1.5
        )
        self.wait(5.80)

        # -------------------------------------------------------------
        # SEGMENT 4: Unbroken Gradient Highway (~11.52s total)
        # -------------------------------------------------------------
        grad_highlight = Text("Backpropagation Highway: dLoss/dx = (dLoss/dOut) * (dF/dx + 1)", font_size=14, color=GREEN_B)
        grad_highlight.shift(DOWN * 2.8)
        self.play(Write(grad_highlight), run_time=2.0)

        # Pulsing the shortcut gradient flow
        self.play(
            shortcut_path.animate.set_color(GREEN_A).set_stroke_width(4.5),
            out_label.animate.set_color(YELLOW),
            run_time=2.5
        )
        
        note_lbl = Text("The +1 term guarantees error signals never vanish in deep layers.", font_size=13, color=GRAY_A)
        note_lbl.next_to(grad_highlight, DOWN, buff=0.2)
        self.play(FadeIn(note_lbl), run_time=1.5)
        self.wait(5.52)
