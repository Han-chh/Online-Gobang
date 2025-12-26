## English Introduction

### Project Overview
This is a network-based Gobang (Five-in-a-Row) game project built with Python and pygame, supporting real-time multiplayer battles over LAN. The project implements complete Gobang game logic including network connectivity, chat functionality, sound effects, player statistics, and more. While primarily using pygame as the graphics library, due to pygame's limitations in UI components, the developer had to implement numerous custom UI components from scratch.

### Feature List
1. **Network Multiplayer**:
   - LAN player discovery and connection
   - UDP broadcast protocol for automatic room discovery
   - Real-time game state synchronization

2. **Core Game Logic**:
   - Standard Gobang rules (15x15 board)
   - Automatic win/loss detection (five in a row or full board draw)
   - Turn-based piece placement

3. **Chat System**:
   - Real-time text chat
   - Message exchange between players
   - Chat history display with scrolling

4. **Sound Control**:
   - Background music playback
   - Piece placement sound effects
   - Win/lose/draw sound effects
   - Volume control toggle

5. **Timer System**:
   - Time limit per move
   - Automatic loss on timeout
   - Real-time countdown display

6. **Player Profile System**:
   - Player statistics (win rate, streak records, etc.)
   - Game history records
   - Profile management (using tkinter interface)

7. **Custom UI Components**:
   - Buttons, input boxes, dialogs, etc.
   - Circular avatar cropping functionality
   - Responsive interface design

### Network Architecture and Custom Communication Protocol
**Network Architecture**:
- P2P (Peer-to-Peer) architecture, no central server required
- UDP protocol for communication, suitable for real-time gaming
- Broadcast mechanism for room discovery

**Custom Communication Protocol**:
- Message format: JSON
- Main message types:
  - `lost_ping`: Connection keep-alive detection
  - `chat`: Chat messages
  - `move`: Piece placement actions (includes x,y coordinates and player info)
  - `win`: Game end notification
- Protocol features:
  - Lightweight and easy to parse
  - Supports timestamps and player identification
  - Includes error handling and connection loss detection

### Usage Instructions
1. **Environment Setup**:
   - Install Python 3.x
   - Install dependencies: `pip install pygame
   - Ensure firewall allows UDP port 5000 communication

2. **Starting the Game**:
   - Run `python main.py`
   - Choose "Create Room" or "Join Room" from the main interface

3. **Creating a Room**:
   - Set room ID, move time limit, choose piece color
   - Wait for opponent to join

4. **Joining a Room**:
   - Enter room ID
   - Automatically connect to the room

5. **Gameplay**:
   - Take turns placing pieces on the board
   - Use chat box to communicate with opponent
   - Pay attention to time limits

6. **Game End**:
   - System automatically determines winner
   - Statistics automatically saved

### Detailed Game Flow
Below is a complete description of the game flow, from startup to completion:

#### 1. Game Startup Phase
- **Program Initialization**: Run `main.py`, the program first checks if `player_data/player_data.txt` file exists
- **Player Data Loading**: If the file exists, load player ID, statistics, and preference settings; if not, create default player data
- **Network Connection Initialization**: Create Connection object, initialize UDP socket, bind to local port 5000
- **Main Interface Display**: Display the game main interface, providing "Create Room" and "Join Room" options

#### 2. Room Creation Flow
- **Room Settings Dialog**: After clicking "Create Room", a settings dialog appears
  - Enter room ID (unique identifier)
  - Set time limit per move (default 30 seconds)
  - Choose piece color (black or white)
- **Room Verification**: System checks if room ID is already in use via UDP broadcast detection
- **Broadcast Room Information**: If verification passes, start UDP broadcasting room information, waiting for other players to join
- **Waiting State**: Display "Waiting for opponent to join..." interface while maintaining broadcast

#### 3. Room Joining Flow
- **Room Search**: After clicking "Join Room", the program starts listening for UDP broadcasts to search for available rooms
- **Room List Display**: Display the list of discovered rooms (if any)
- **Manual Room ID Input**: If no rooms found or specific room needed, manually enter room ID
- **Connection Establishment**: After entering room ID, program attempts to connect to the specified room
  - Send connection request to opponent's IP and port
  - Wait for opponent to confirm connection
- **Connection Verification**: Both parties establish P2P connection, start connection keep-alive detection (ping every 10 seconds)

#### 4. Game Preparation Phase
- **Board Initialization**: After connection established, initialize 15x15 Gobang board
- **Player Assignment**: Assign black and white pieces based on room creation choice
  - Room creator usually gets black pieces (first move)
  - Room joiner gets white pieces (second move)
- **Interface Switch**: Switch from main interface to game interface, including board, chat box, info panel
- **Timer Start**: Set move time limit, start countdown (starting with black piece player)

#### 5. Gameplay Phase
- **Turn-based Piece Placement**:
  - Current player clicks on board to place piece
  - System validates if placement position is valid (must be empty)
  - After successful placement, send `move` message to opponent via network
  - Play piece placement sound effect
- **Real-time Synchronization**: Opponent receives `move` message and displays opponent's piece on local board
- **Win/Loss Check**: After each move, check for five-in-a-row
  - Check four directions: horizontal, vertical, diagonal
  - If five in a row, end game immediately
  - If board is full with no winner, declare draw
- **Chat Function**: Players can input messages in chat box at any time
  - Send `chat` message to opponent
  - Messages display in real-time in chat history
- **Timer Management**:
  - Countdown for each move
  - When time reaches 0, current player loses
  - After placing piece, reset opponent's time and start own countdown

#### 6. Game End Phase
- **Win/Loss Determination**:
  - Five in a row: Connected player wins
  - Timeout: Timed-out player loses
  - Full board: Draw
- **End Notification**: Send `win` message to notify opponent of game result
- **Sound Effects**: Play win/lose/draw sound effects based on result
- **Interface Update**: Display game result, disable board operations
- **Data Saving**: Call `save_game_data()` function to save game record

#### 7. Profile Update Phase
- **Statistics Update**:
  - Total games played +1
  - Update win/loss/draw counts based on result
  - Update win streak (increment on win, reset to 0 on loss)
  - Update highest win streak record
  - Accumulate total moves and total play time
- **Game History Records**:
  - Add new game record to `game_history` list
  - Record opponent ID, result, move count, timestamp
- **Data Persistence**: Write updated data to `player_data/player_data.txt` file
- **Profile Interface**: Players can view personal profile window anytime (implemented with tkinter)
  - Display statistics
  - Display game history
  - Manage preferences (theme, sound effects, etc.)

#### 8. Game Restart or Exit
- **Continue Playing**: Players can choose to create new room or join other rooms
- **Exit Game**: Close program, save final data
- **Connection Lost**: If network connection lost, display disconnection prompt, return to main interface

The entire flow demonstrates the characteristics of P2P network architecture: decentralized, no server required, direct peer-to-peer communication. Meanwhile, the detailed timer and statistics system enhance the game's competitiveness and data tracking capabilities.

### Third-party Python Packages
- **pygame**: Game graphics interface and event handling

### Complaints About pygame
Although this project is primarily implemented with pygame, pygame as a game development library has significant inconveniences for developers:

1. **Lack of UI Components**: pygame has no built-in UI component library, forcing developers to implement buttons, input boxes, dialogs, and other basic components from scratch. This greatly increases development time and complexity.

2. **Complex Event Handling**: pygame's event system is relatively low-level, requiring manual handling of mouse and keyboard events, lacking high-level UI event abstractions.

3. **Difficult Layout Management**: No built-in layout managers, requiring manual coordinate and size calculations, making responsive design exceptionally complex.

4. **Text Rendering Limitations**: Basic text rendering, but advanced features like multi-line text and rich text require substantial additional code.

5. **Cross-platform Consistency**: While pygame supports cross-platform development, behavior may vary across different systems.

Because of these inconveniences, I implemented numerous custom UI components in this project, including Button, InputBox, Dialog classes, etc., defined in UIComponents.py. Although this improves code reusability, it also reflects pygame's shortcomings in modern GUI development.

### Request for Suggestions and Bug Reports
Welcome developers to provide suggestions and report bugs for this project! There may be many shortcomings in the code.

**Suggestion Channels**:
- Submit issues on GitHub's Issues page
- Contribute code improvements via Pull Request

**Particularly Hopeful Suggestions**:
- Network protocol security improvements
- Code structure optimization
- UI/UX improvement suggestions
- Performance optimization
- Cross-platform compatibility

**Known Issues**:
- Network connection stability needs improvement
- UI component adaptation on high-resolution screens
- Copyright issues with sound files (currently using free sound effects)

Thank you for your attention and support!