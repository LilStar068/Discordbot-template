import random

import discord
from discord.utils import MISSING, cached_property


BoardState = []


STATES = (
    "\N{REGIONAL INDICATOR SYMBOL LETTER X}",
    "\N{REGIONAL INDICATOR SYMBOL LETTER O}",
)


class Board:
    def __init__(self, state: BoardState, current_player: bool = False):
        self.state = state
        self.current_player = current_player
        self.winner = MISSING

    @property
    def legal_moves(self):
        for c in range(3):
            for r in range(3):
                if self.state[r][c] is None:
                    yield (r, c)

    @cached_property
    def over(self):

        # vertical
        for c in range(3):
            token = self.state[0][c]
            if token is None:
                continue
            if self.state[1][c] == token and self.state[2][c] == token:
                self.winner = token
                return True

        # horizontal
        for r in range(3):
            token = self.state[r][0]
            if token is None:
                continue
            if self.state[r][1] == token and self.state[r][2] == token:
                self.winner = token
                return True

        # descending diag
        if self.state[0][0] is not None:
            token = self.state[0][0]
            if self.state[1][1] == token and self.state[2][2] == token:
                self.winner = token
                return True

        # ascending diag
        if self.state[0][2] is not None:
            token = self.state[0][2]
            if self.state[1][1] == token and self.state[2][0] == token:
                self.winner = token
                return True

        # Check if board is empty
        for _ in self.legal_moves:
            break
        else:
            self.winner = None
            return True

        return False

    def move(self, r: int, c: int):
        if (r, c) not in self.legal_moves:
            raise ValueError("Illegal Move")

        new_state = [[self.state[r][c] for c in range(3)] for r in range(3)]
        new_state[r][c] = self.current_player

        return Board(new_state, not self.current_player)

    @classmethod
    def new_game(cls):
        state: BoardState = [[None for _ in range(3)] for _ in range(3)]
        return cls(state)


class AI:
    def __init__(self, player: bool):
        self.player = player

    def move(self, game: Board):
        column = random.choice(tuple(game.legal_moves))
        return game.move(*column)


class NegamaxAI(AI):
    def __init__(self, player: bool):
        super().__init__(player)

    def heuristic(self, game: Board, sign: int):
        if sign == -1:
            player = not self.player
        else:
            player = self.player

        if game.over:
            if game.winner is None:
                return 0
            if game.winner == player:
                return 1_000_000
            return -1_000_000

        return random.randint(-10, 10)

    def negamax(
        self,
        game,
        depth: int = 0,
        alpha: float = float("-inf"),
        beta: float = float("inf"),
        sign: int = 1,
    ):
        if game.over:
            return sign * self.heuristic(game, sign)

        move = MISSING

        score = float("-inf")
        for c in game.legal_moves:
            move_score = -self.negamax(game.move(*c), depth + 1, -beta, -alpha, -sign)

            if move_score > score:
                score = move_score
                move = c

            alpha = max(alpha, score)
            if alpha >= beta:
                break

        if depth == 0:
            return move
        else:
            return score

    def move(self, game: Board):
        return game.move(*self.negamax(game))


class Button(discord.ui.Button["Game"]):
    def __init__(self, r: int, c: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=c)
        self.r = r
        self.c = c

    def update(self):
        cell = self.view.board.state[self.r][self.c]

        if cell is not None or self.view.board.over:
            self.disabled = True

        if cell == True:
            self.style = discord.ButtonStyle.success
            self.label = "O"
        if cell == False:
            self.style = discord.ButtonStyle.danger
            self.label = "X"

    async def callback(self, interaction: discord.Interaction):

        self.view.board = self.view.board.move(self.r, self.c)
        self.view.update()

        if self.view.board.over:
            await self.view.game_over(interaction)
            return

        if self.view.current_player.bot:
            self.view.make_ai_move()
            self.view.update()

        if self.view.board.over:
            await self.view.game_over(interaction)
            return

        await interaction.response.edit_message(
            content=f"{self.view.current_player.mention}'s' ({STATES[self.view.board.current_player]}) turn!",
            view=self.view,
        )


class Game(discord.ui.View):
    children: list

    def __init__(self, players):
        self.players = list(players)
        random.shuffle(self.players)

        super().__init__(timeout=None)
        self.board = Board.new_game()

        if self.current_player.bot:
            self.make_ai_move()

        for r in range(3):
            for c in range(3):
                self.add_item(Button(r, c))

        self.update()

    def update(self):
        for child in self.children:
            child.update()

    async def game_over(self, interaction: discord.Interaction):
        if self.board.winner is not None:
            content = f"{self.players[self.board.winner].mention} ({STATES[self.board.winner]}) wins!"
        else:
            content = "Draw!"

        for child in self.children:
            child.disabled = True  # type: ignore

        self.stop()
        return await interaction.response.edit_message(content=content, view=self)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user not in self.players:
            await interaction.response.send_message(
                "Sorry, you are not playing", ephemeral=True
            )
            return False
        elif interaction.user != self.current_player:
            await interaction.response.send_message(
                "Sorry, it is not your turn!", ephemeral=True
            )
        return True

    def make_ai_move(self):
        ai = NegamaxAI(self.board.current_player)
        self.board = ai.move(self.board)

    @property
    def current_player(self):
        return self.players[self.board.current_player]
