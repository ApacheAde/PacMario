================================================================================
                              PAC-MARIO
                    Neon 8-Bit Pac-Man Adventure
================================================================================

A fun mashup of classic Pac-Man gameplay with a Mario twist!

Guide Mario through a glowing neon maze, chomp coins, grab power stars 
to turn the ghosts into prey, and survive as long as you can.

--------------------------------------------------------------------------------
HOW TO RUN
--------------------------------------------------------------------------------

1. Make sure Python is installed.
   Recommended on Windows:
       winget install Python.Python.3.12

   Alternatives:
   - scoop install python
   - Or download from https://python.org (check "Add python.exe to PATH")

2. Install the required library:
       pip install pygame

3. Run the game:
       cd Desktop
       python PacMario.py

   You can also double-click PacMario.py once pygame is installed.

--------------------------------------------------------------------------------
CONTROLS
--------------------------------------------------------------------------------

    Arrow Keys  or  WASD     - Move Mario
    P                        - Pause (returns to title screen)
    SPACE                    - Start game / Restart after game over
    ESC                      - Quit or return to title screen

--------------------------------------------------------------------------------
GAMEPLAY
--------------------------------------------------------------------------------

- Eat all the coins to clear the level and advance.
- Power Stars (the big pulsing yellow ones) give you temporary "Star Power".
- While powered up, the ghosts turn vulnerable — run them down for big points!
- Ghosts have different personalities and colors (Boo, Goomba, Koopa, ShyGuy).
- 3 lives per game. Lose them all = Game Over.
- Score points for coins (10), Power Stars (50), and eating ghosts (200–1600).
- Difficulty increases each level (ghosts get faster).

High score is automatically saved to:
    pacmario_highscore.txt

--------------------------------------------------------------------------------
VISUAL STYLE & FEATURES
--------------------------------------------------------------------------------

- Eye-catching neon colors: bright cyan, magenta, lime green, hot pink, 
  electric yellow, blue, red, and orange.
- 8-bit style character art for Mario (hat, mustache, overalls) and ghosts.
- Glowing neon effects on walls, characters, and power-ups.
- Classic Pac-Man maze layout with a Mario theme (coins instead of dots).
- Authentic 8-bit sound effects generated in real time:
    • Coin chomping beeps
    • Power star activation
    • Ghost stomps
    • Death jingle
    • Level up fanfare
    • Classic ghost siren

No external image or sound files required — everything is drawn and 
generated in pure Python + pygame.

--------------------------------------------------------------------------------
TIPS
--------------------------------------------------------------------------------

- Use the power stars strategically — they are your best chance to rack 
  up huge scores by eating multiple ghosts in a row.
- The ghosts get smarter and faster as levels progress. Learn their 
  movement patterns.
- Mario moves on a grid — plan your turns in advance.
- Clear the coins in one area before moving on to avoid getting trapped.
- The center "ghost house" area is dangerous — be careful near it.

--------------------------------------------------------------------------------
FILES ON YOUR DESKTOP
--------------------------------------------------------------------------------

PacMario.py            - The complete game (single file)
PacMario_README.txt    - This instruction file
pacmario_highscore.txt - Your personal high score (created automatically)

--------------------------------------------------------------------------------
TECHNICAL NOTES
--------------------------------------------------------------------------------

- Built with Python + pygame (no external assets)
- All sounds are procedurally generated 8-bit style square/saw waves
- High score persists between sessions
- Runs at 60 FPS in an 800x620 window
- Works great on Windows (and should work on macOS/Linux too)

--------------------------------------------------------------------------------
HAVE FUN!
--------------------------------------------------------------------------------

PacMario was created as a fun, self-contained retro game project.

Chomp those coins, stomp those ghosts, and chase that high score!

If you enjoy it, try beating your best score on higher levels.

================================================================================
                              Enjoy the neon maze!
================================================================================
