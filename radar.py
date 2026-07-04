import math
import pygame
import serial
import time

SERIAL_PORT = '/dev/cu.wchusbserial1110'
BAUD_RATE = 115200
SCREEN_SIZE = (960, 480)
RECT_CORNER = (0, 0)
LINE_LENGTH = 700
CANVAS_COLOUR = (0, 0, 50)
RING_COLOUR = (0, 50, 0)
FADE_DURATION = 1000
ANGLE_INCREMENT = 0.5
DISTANCE_THRESHOLD = 20

active_lines = []
coords = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1])
angle = 0
distance_cm, servo_position = 0, 0
def main():
    global angle, distance_cm, servo_position
    pygame.init()
    canvas = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    running = True

    alpha_surf = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)

    try:
        arduino = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
        time.sleep(2)
    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except KeyboardInterrupt:
        print("\nProgram terminated.")
    except Exception as e:
        print(f"\nUnexpected Error: {e}")

    while running:
            if arduino.in_waiting > 0:
                raw_line = arduino.readline()
                line = raw_line.decode('utf-8').strip()

                try:
                    distance_cm, servo_position = line.split(',')
                    print(f"Distance: {distance_cm}, Servo position: {servo_position}")
                except ValueError:
                    print(f"Skipping malformed serial data: {line}")
            current_time = pygame.time.get_ticks()

            distance_cm = int(distance_cm)
            servo_position = int(servo_position)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Handle line on temporary surface
            rad = servo_position / 180.0 * math.pi
            if distance_cm < DISTANCE_THRESHOLD:
                line_length = int(LINE_LENGTH * (distance_cm / DISTANCE_THRESHOLD))
                colour = (70, 0, 0)
            else:
                line_length = LINE_LENGTH
                colour = (0, 70, 0)

            x_coord = math.cos(rad) * line_length
            y_coord = math.sin(rad) * line_length

            start_pos = coords
            end_pos = (coords[0] - x_coord, coords[1] - y_coord)

            # Store line data
            active_lines.append({
                'end_pos': end_pos,
                'start_time': current_time
            })

            canvas.fill(CANVAS_COLOUR)
            alpha_surf.fill((0, 0, 0, 0))

            # Radar rings
            offset = 0
            for _ in range(6):
                draw_ring(canvas, offset)
                offset += 120

            for line in active_lines[:]:
                elapsed_time = current_time - line['start_time']

                if elapsed_time >= FADE_DURATION:
                    active_lines.remove(line)
                    continue

                ratio = 1.0 - (elapsed_time/FADE_DURATION)
                current_alpha = int(255 * ratio)

                fade_colour = (*colour, current_alpha)
                print(fade_colour, line_length)
                pygame.draw.line(alpha_surf, fade_colour, start_pos, line['end_pos'], 2)

            canvas.blit(alpha_surf, (0, 0))

            angle += ANGLE_INCREMENT
            angle %= 180

            clock.tick(60)
            pygame.display.flip()

    if arduino:
        arduino.close()
    pygame.quit()


# Draw rings
def draw_ring(surface, offset) -> pygame.Rect:
    hitbox =  pygame.Rect(coords[0] - offset, coords[1] - offset,
                                    RECT_CORNER[0] + offset * 2,
                                    RECT_CORNER[1] + offset * 2)
    ring = pygame.draw.arc(surface, RING_COLOUR, hitbox, 0, math.pi, 2)
    return ring

if __name__ == "__main__":
    main()