# 🎮 CROWD CONTROL

**Fast-paced 2-player local multiplayer arena game with advanced VFX, power-ups, and replay system**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame--CE-2.5.6-green.svg)](https://pyga.me/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Features

### Core Gameplay
- ⚔️ **Intense 2-Player Combat** - Push opponents off the shrinking platform
- 🎯 **Skill-Based Mechanics** - Master dashing, positioning, and timing
- 🌊 **Dynamic Arena** - Platform shrinks over time, increasing pressure
- 🎮 **Local Multiplayer** - Perfect for party games and tournaments

### Advanced Systems
- 💫 **VFX Post-Processing** - Chromatic aberration, bloom, screen distortion
- ✨ **Particle System** - 2000+ particle pool with object pooling
- 🎁 **Power-Up System** - 8 different power-ups (speed boost, shield, triple dash, etc.)
- 🤖 **AI Opponents** - 4 difficulty levels with state-based behavior
- 📹 **Replay System** - Record and playback matches with speed control
- 📊 **Advanced HUD** - Combo tracking, kill feed, real-time stats
- 🎨 **Motion Trails** - Dynamic trail rendering for dashing players
- 💥 **Impact Effects** - Expanding collision rings and screen shake
- 🎵 **Sound System** - Dynamic audio with positional sound

---

## 🎥 Demo


[**🎮 Play Demo**](https://mega.nz/file/pKMTCLqT#Dkmdk-82chL26fgiUpI6G7opjHea7heay7ZKrE29B0s)

---

## 📸 Screenshots

![Gameplay](screenshots/gameplay1.png)
*Intense 1v1 action with VFX effects*

![Power-ups](screenshots/powerups.png)
*Strategic power-up collection*

![Victory](screenshots/victory.png)
*Victory screen with stats*

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Quick Start

```bash
# Clone repository
git clone https://github.com/ramakrishnanyadav/crowd-control-game.git
cd crowd-control-game

# Install dependencies
pip install -r requirements.txt

# Run game
python main.py
```

---

## 🎮 Controls

| Action | Player 1 | Player 2 |
|--------|----------|----------|
| **Move** | WASD | Arrow Keys |
| **Dash** | Left Shift | Right Shift |
| **Pause** | ESC | ESC |

### Special Controls
- **R** - Restart round
- **M** - Toggle sound
- **V** - Toggle VFX effects
- **F1** - Toggle replay recording

---

## 🏗️ Project Structure

```
crowd_control/
├── main.py                 # Entry point
├── config/
│   ├── settings.py         # Game configuration
│   └── controls.py         # Input mapping
├── core/
     
│   ├── physics.py          # Collision detection & spatial grid
│   └── game.py             # Game loop
├── entities/
│   ├── player.py           # Player with dash mechanics
│   ├── ai_player.py        # AI with FSM behavior
│   ├── platform.py         # Shrinking platform
│   └── powerup.py          # Power-up system
├── systems/
│   ├── particles.py        # Particle system with pooling
│   ├── screenshake.py      # Camera shake & hitstop
│   ├── vfx.py              # Post-processing effects
│   ├── sound.py            # Audio manager
│   └── replay.py           # Replay recording/playback
├── ui/
│   ├── hud.py              # Advanced HUD with combos
│   ├── menu.py             # Main menu
│   └── transitions.py      # Scene transitions
└── scenes/
    ├── scene_manager.py    # Scene system
    ├── menu_scene.py       # Menu screen
    ├── game_scene.py       # Main gameplay
    └── results_scene.py    # End screen
```

---

## 🛠️ Technical Highlights

### Performance Optimizations
- **Object Pooling** - Reuses 2000 particles to eliminate GC lag
- **Spatial Grid** - O(1) collision detection using grid partitioning
- **Dirty Rectangle** - Only redraws changed areas
- **Frame-Independent Physics** - Smooth gameplay at any FPS

### Advanced Features
- **State Machine AI** - Context-aware opponent behavior
- **Input Buffering** - 100ms buffer for responsive controls
- **Hitstop** - Frame freezing on impact for game feel
- **Combo System** - Multiplier-based scoring
- **Kill Feed** - Real-time event notifications

---

## 🧪 Technologies Used

- **Python 3.14** - Core language
- **Pygame-CE 2.5.6** - Game engine
- **NumPy** - VFX array operations
- **JSON** - Replay data serialization

---

## 🎯 Development Roadmap

### Version 1.0 (Current)
- [x] Core gameplay mechanics
- [x] Advanced VFX system
- [x] AI opponents
- [x] Power-up system
- [x] Replay system

### Version 2.0 (Planned)
- [ ] Online multiplayer
- [ ] Tournament mode
- [ ] Character customization
- [ ] Map editor
- [ ] Achievement system
- [ ] Leaderboards

---

## 🏆 Game Design Philosophy

**Crowd Control** follows the "easy to learn, hard to master" principle:

1. **Core Loop** - Simple mechanics (move, dash, push) create deep gameplay
2. **Skill Expression** - Dashing requires positioning prediction and timing
3. **Dynamic Pressure** - Shrinking platform forces aggressive play
4. **Game Feel** - Every action has satisfying visual/audio feedback

---

## 📊 Performance Metrics

- **Target FPS:** 60
- **Particle Count:** Up to 2000 active
- **Input Latency:** <16ms
- **Memory Usage:** ~50MB
- **Startup Time:** <2 seconds

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@ramakrishnanyadav](https://github.com/ramakrishnanyadav)
- DevPost: [@ramakrishnayadav2004](https://devpost.com/ramakrishnanyadav)
- Email: ramakrishnanyadav2004.com

---

## 🙏 Acknowledgments

- Pygame Community for the amazing game engine
- Indie game developers for inspiration
- Beta testers for valuable feedback

---

## 📞 Support

Having issues? [Open an issue](https://github.com/ramakrishnanyadav/crowd-control-game/issues) or contact me directly.

---

⭐ **If you enjoyed this game, please give it a star!** ⭐