from GameConfig import BLACK_PLAYER, WHITE_PLAYER
import BoardWindow


def check_win(board, x, y,BOARD_SIZE):
    player = board[y][x]
    directions = [(1,0), (0,1), (1,1), (1,-1)]
    for dx, dy in directions:
        count = 1
        nx, ny = x + dx, y + dy
        while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == player:
            count += 1
            nx += dx
            ny += dy
        nx, ny = x - dx, y - dy
        while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[ny][nx] == player:
            count += 1
            nx -= dx
            ny -= dy
        if count >= 5:
            return player
        
    for a in range(15):
        for b in range(15):
            if board[a][b] == 0:
                return 0

    return 3


