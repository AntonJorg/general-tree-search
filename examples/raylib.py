import raylibpy as rl

rl.init_window(800, 600, "Raylib Rectangles")

while not rl.window_should_close():
    rl.begin_drawing()
    rl.clear_background(rl.RAYWHITE)

    for i in range(2000):
        x, y = (i % 50) * 16, (i // 50) * 16
        rl.draw_rectangle(x, y, 15, 15, rl.BLUE)

    rl.end_drawing()

rl.close_window()
