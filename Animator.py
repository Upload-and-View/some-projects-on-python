# Big Test Animation with Table-like Data
import tkinter as tk
import time
import random

FPS = 240
WIDTH = 800
HEIGHT = 600
NUM_DOTS = 500
ANIMATION_LENGTH = 1000

def wait(seconds):
    time.sleep(seconds)

def generate_big_animation_data(num_dots, animation_length):
    animation_data = {}
    colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]
    for i in range(num_dots):
        dot_name = f"Dot {i+1}"
        animation_data[dot_name] = {}
        color = random.choice(colors)
        initial_x = random.randint(50, WIDTH - 50)
        initial_y = random.randint(50, HEIGHT - 50)
        initial_size = random.randint(10, 30)

        for tick in range(1, animation_length + 1):
            delta_x = random.randint(-1, 1)
            delta_y = random.randint(-1, 1)
            delta_size = random.randint(-1, 1)
            color_change_chance = 0.1  # 10% chance to change color

            prev_tick = animation_data[dot_name].get(f"Tick {tick-1}")
            if prev_tick:
                prev_x = prev_tick["Position"]["X"]
                prev_y = prev_tick["Position"]["Y"]
                prev_size_x = prev_tick["Size"]["X"]
                prev_size_y = prev_tick["Size"]["Y"]
                prev_color = prev_tick.get("Color", color)
            else:
                prev_x = initial_x
                prev_y = initial_y
                prev_size_x = initial_size
                prev_size_y = initial_size
                prev_color = color

            new_x = max(5, min(WIDTH - 5, prev_x + delta_x))
            new_y = max(5, min(HEIGHT - 5, prev_y + delta_y))
            new_size = max(5, min(50, prev_size_x + delta_size))
            new_color = random.choice(colors) if random.random() < color_change_chance else prev_color

            animation_data[dot_name][f"Tick {tick}"] = {
                "Position": {"X": new_x, "Y": new_y},
                "Size": {"X": new_size, "Y": new_size},
                "Color": new_color
            }
    return animation_data

def animate(animation_data):
    dot_names = list(animation_data.keys())
    dot_objects = {}

    window = tk.Tk()
    window.title("Big Animator")
    canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="white")
    canvas.pack()

    # Create initial dots
    for name in dot_names:
        first_tick = animation_data[name].get("Tick 1")
        if first_tick:
            x = first_tick["Position"]["X"]
            y = first_tick["Position"]["Y"]
            size = first_tick["Size"]["X"]
            color = first_tick.get("Color", "black")
            dot = canvas.create_oval(x - size/2, y - size/2, x + size/2, y + size/2, fill=color)
            dot_objects[name] = dot

    # Determine the maximum number of ticks
    num_ticks = 0
    for name in dot_names:
        num_ticks = max(num_ticks, len(animation_data[name]))

    # Animation loop
    for i in range(1, num_ticks + 1):
        tick_name = f"Tick {i}"
        for name in dot_names:
            if tick_name in animation_data[name]:
                data = animation_data[name][tick_name]
                x = data["Position"]["X"]
                y = data["Position"]["Y"]
                size = data["Size"]["X"]
                color = data.get("Color", canvas.itemcget(dot_objects[name], "fill"))

                if name in dot_objects:
                    canvas.coords(dot_objects[name], x - size/2, y - size/2, x + size/2, y + size/2)
                    canvas.itemconfig(dot_objects[name], fill=color)

        window.update()
        wait(1 / FPS)

    window.mainloop()

if __name__ == "__main__":
    big_animation_data = generate_big_animation_data(NUM_DOTS, ANIMATION_LENGTH)
    animate(big_animation_data)