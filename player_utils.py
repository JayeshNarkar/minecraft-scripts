import os
import random
import re

from playsound3 import playsound
import minescript as ms
import time
import math
import sys
import psutil
import requests
import os
from dotenv import load_dotenv
import queue

load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
USER_ID = os.getenv("USER_ID")

EXIT_MESSAGES = [
    "Wow, really macro checking me? Im so offended :(",
    "Can't believe I just got macro checked, actually embarrassing for you",
    "Bro really macro checking me for being too good lmao I'm done",
    "Getting macro checked even after having 300+ ping is crazy work",
    "I actually can't believe this, I'm genuinely upset rn",
    "Macro checking me but not actual cheaters on the leaderboard?? I'm going to cry",
    "Macro checking ME? My hands are shaking I'm so mad rn",
]

tiers = [
    "common",
    "uncommon",
    "rare",
    "epic",
    "legendary",
    "mythic",
    "crazy",
    "rngesus",
    "woah",
    "admin",
    "leveled",
    "autopet",
    "yuck",
    "salt",
    "overflow",
    "selling",
    "blessed",
    "low sack",
]


def key_listener_thread():
    with ms.EventQueue() as event_queue:
        event_queue.register_key_listener()
        while True:
            event = event_queue.get()
            if event.type == ms.EventType.KEY and event.key == 89:
                ms.echo("Exiting script")
                stop_movement_and_attack()
                os._exit(1)


def clean_message(msg):
    if not msg:
        return ""
    # fix mojibake: Â§ is a mangled §
    msg = msg.replace("Â§", "§").replace("Â", "")
    # strip minecraft color codes
    msg = re.sub(r"§[0-9a-fk-or]", "", msg)
    # strip remaining non-ascii garbage
    msg = re.sub(r"[^\x20-\x7E]", "", msg)
    return msg.strip()


def chat_listener_thread(chat_queue):
    with ms.EventQueue() as event_queue:
        event_queue.register_chat_listener()
        while True:
            event = event_queue.get()
            if event.type == ms.EventType.CHAT:
                cleaned = clean_message(event.message)
                msg = event.message.lower()
                try:
                    chat_queue.put(event.message)
                except queue.Full:
                    chat_queue.get_nowait()  # drop oldest
                    chat_queue.put_nowait(cleaned)
                if "[sacks]" not in msg:
                    no_mention = (
                        "[npc]" in msg
                        or "skyhanni" in msg
                        or "6cd670b7-bd10-45d6-8daa-43651b5d136d" in msg
                    )
                    if ":" in msg:
                        send_discord_message(cleaned, mention=not no_mention)
                    elif "low sack" in msg or "selling" in msg:
                        send_discord_message(cleaned)
                    elif any(tier in msg for tier in tiers):
                        send_discord_message(cleaned, mention=False)


def stop_movement_and_attack():
    ms.player_press_sneak(False)
    ms.player_press_jump(False)

    ms.player_press_left(False)
    ms.player_press_right(False)
    ms.player_press_forward(False)
    ms.player_press_backward(False)

    ms.player_press_attack(False)


def kill_game_process():
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if "javaw" in proc.info["name"].lower():
                cmdline = " ".join(proc.info["cmdline"] or [])
                if "prismlauncher" in cmdline.lower():
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def exit_fun(statement):
    stop_movement_and_attack()
    time.sleep(1.5 + random.uniform(0, 1))
    # ms.chat(random.choice(EXIT_MESSAGES))
    time.sleep(2.5 + random.uniform(0, 1))
    playsound("./minescript/gong_sound.mp3")
    send_discord_message(statement)
    ms.echo(statement)
    # kill_game_process()
    sys.exit(0)


def send_discord_message(content, mention=True):
    if mention:
        mention = f"<@{USER_ID}>"
    else:
        mention = ""
    full_content = f"{mention} {content}"
    data = {"content": full_content}

    response = requests.post(WEBHOOK_URL, json=data)

    # if response.status_code != 204:
    #     print(f"Failed to send message. Status code: {response.status_code}")


def smooth_orientation(target_yaw, target_pitch, duration=0.5, steps=20):
    """
    Smoothly rotate the player from current orientation to target orientation.

    Args:
        target_yaw: Target yaw angle in degrees (-180 to 180)
        target_pitch: Target pitch angle in degrees (-90 to 90)
        duration: Total duration of the rotation in seconds
        steps: Number of interpolation steps (higher = smoother)
    """
    # Get current orientation
    current_yaw, current_pitch = ms.player_orientation()

    # Normalize angles to handle wrap-around correctly
    def normalize_angle(angle):
        """Normalize angle to -180 to 180 range"""
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle

    def shortest_angle_difference(from_angle, to_angle):
        """Get the shortest direction to rotate"""
        diff = normalize_angle(to_angle - from_angle)
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        return diff

    current_yaw = normalize_angle(current_yaw)
    target_yaw = normalize_angle(target_yaw)

    # Calculate the shortest rotation path for yaw
    yaw_diff = shortest_angle_difference(current_yaw, target_yaw)

    # Pitch doesn't wrap around, just clamp
    target_pitch = max(-90, min(90, target_pitch))
    pitch_diff = target_pitch - current_pitch

    # Calculate step sizes
    step_delay = duration / steps

    # Interpolate
    for i in range(steps + 1):
        # Calculate interpolation factor (ease in/out for smoother motion)
        t = i / steps
        # Optional: Use easing for more natural movement
        # t = t * t * (3 - 2 * t)  # Smoothstep easing

        # Calculate intermediate angles
        interp_yaw = current_yaw + (yaw_diff * t)
        interp_pitch = current_pitch + (pitch_diff * t)

        # Apply the intermediate orientation
        ms.player_set_orientation(interp_yaw, interp_pitch)

        # Wait before next step
        time.sleep(step_delay)


def smooth_look_at(x, y, z, duration=0.5, steps=20):
    """
    Smoothly rotate the player to look at a specific position.

    Args:
        x, y, z: Target position to look at
        duration: Total duration of the rotation in seconds
        steps: Number of interpolation steps
    """
    # Get player position
    player_pos = ms.player_position()

    # Calculate direction vector
    dx = x - player_pos[0]
    dy = y - player_pos[1]
    dz = z - player_pos[2]

    # Calculate yaw and pitch
    yaw = math.degrees(math.atan2(-dx, dz))
    horizontal_distance = math.sqrt(dx * dx + dz * dz)
    pitch = math.degrees(math.atan2(-dy, horizontal_distance))

    # Clamp pitch
    pitch = max(-90, min(90, pitch))

    # Smoothly rotate to target
    smooth_orientation(yaw, pitch, duration, steps)


def smooth_rotate_to_entity(entity, duration=0.5, steps=20):
    """
    Smoothly rotate to look at an entity.

    Args:
        entity: EntityData object from ms.get_entities()
        duration: Total duration of the rotation in seconds
        steps: Number of interpolation steps
    """
    # Get entity's eye height (approximate)
    entity_height = 1.62  # Standard player eye height
    if hasattr(entity, "position"):
        target_x, target_y, target_z = entity.position
        target_y += entity_height

        smooth_look_at(target_x, target_y, target_z, duration, steps)


def smooth_pan(start_yaw, end_yaw, duration=1.0, steps=30):
    """
    Smoothly pan horizontally from start_yaw to end_yaw.
    Useful for scanning an area.

    Args:
        start_yaw: Starting yaw angle
        end_yaw: Ending yaw angle
        duration: Total duration in seconds
        steps: Number of interpolation steps
    """
    current_pitch = ms.player_orientation()[1]
    smooth_orientation(end_yaw, current_pitch, duration, steps)


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "test":
            # Test: Smoothly look left and right
            ms.echo("Looking left...")
            smooth_orientation(-90, 0, duration=0.8)

            ms.echo("Looking right...")
            smooth_orientation(90, 0, duration=0.8)

            ms.echo("Looking forward...")
            smooth_orientation(0, 0, duration=0.8)

        elif command == "lookat" and len(sys.argv) >= 5:
            # Usage: \smooth_orientation lookat x y z
            x, y, z = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
            smooth_look_at(x, y, z)

        elif command == "entity" and len(sys.argv) >= 3:
            # Usage: \smooth_orientation entity <entity_name>
            # Looks at the nearest entity with matching name
            target_name = sys.argv[2].lower()
            entities = ms.get_entities()

            closest = None
            closest_dist = float("inf")
            player_pos = ms.player_position()

            for entity in entities:
                if target_name in entity.name.lower():
                    dx = entity.position[0] - player_pos[0]
                    dz = entity.position[2] - player_pos[2]
                    dist = math.sqrt(dx * dx + dz * dz)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest = entity

            if closest:
                ms.echo(f"Looking at {closest.name}")
                smooth_rotate_to_entity(closest)
            else:
                ms.echo(f"No entity found matching '{target_name}'")

        else:
            ms.echo("Usage:")
            ms.echo("  \\smooth_orientation test")
            ms.echo("  \\smooth_orientation lookat <x> <y> <z>")
            ms.echo("  \\smooth_orientation entity <name>")
    else:
        # Default: smooth 90-degree right turn
        ms.echo("Turning right smoothly...")
        current = ms.player_orientation()
        smooth_orientation(current[0] + 90, current[1], duration=0.5)
