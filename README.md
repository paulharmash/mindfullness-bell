# Mindfulness Bell

A silent, resonant hourly companion designed to play a low mindfulness bell automatically during the day to support your mindfulness practice.

This application runs entirely offline as a background process and uses macOS's `launchd` to optionally start automatically when you log in. The bell rings at randomized times near the top of the hour, but only when you are actively using your computer (not asleep, screen unlocked, and lid open).

## CLI Commands

To manage the Mindfulness Bell, you can use the command-line interface provided:

```bash
./mindfulness-bell [COMMAND]
```

### Available Commands:

*   **`autostart`**
    Enables auto-start on macOS login using `launchd`. This will automatically run the application in the background every time you start your computer or log in.
    *Example:* `./mindfulness-bell autostart`

*   **`disable-autostart`**
    Disables the auto-start on macOS login and stops the `launchd` background process.
    *Example:* `./mindfulness-bell disable-autostart`

*   **`volume [level]`**
    Sets the playback volume level of the bell sound.
    * `level`: A float value between `0.0` (mute) and `1.0` (maximum volume).
    *Example:* `./mindfulness-bell volume 0.5`

*   **`status`**
    Prints the current status of the legacy background daemon (if running manually) and the current volume configuration level.
    *(Note: if you are using `autostart`, this may report as stopped even when running via `launchd`)*.
    *Example:* `./mindfulness-bell status`

*   **`start`**
    Starts the background daemon manually. This is a legacy command useful if you only want to run the program temporarily and not have it start automatically on login.

*   **`stop`**
    Stops the background daemon (if started via `./mindfulness-bell start`).

*   **`run`**
    Runs the application scheduler in the foreground. This command blocks the terminal and is primarily used internally by `launchd`.

## Logs
When running via `launchd` (using `autostart`), output logs are available at:
*   Standard Output: `/tmp/mindfulness-bell.out.log`
*   Error Output: `/tmp/mindfulness-bell.err.log`
