from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
import uuid
import random
from enum import Enum

app = FastAPI(title="Wall-E Game API", description="Un jeu de plateau inspiré de Wall-E")


class CaseType(Enum):
    ROBOT = "R"
    PRINCESSE = "P"
    FLEUR = "F"
    DECHET = "D"
    VIDE = "V"


class GameStatus(Enum):
    EN_COURS = "EN_COURS"
    PERDU = "PERDU"
    GAGNE = "GAGNE"


class Direction(Enum):
    HAUT = "H"
    BAS = "B"
    GAUCHE = "G"
    DROITE = "D"


class Position(BaseModel):
    x: int
    y: int


class Game:
    def __init__(self, width: int, height: int):
        self.id = str(uuid.uuid4())
        self.width = width
        self.height = height
        self.status = GameStatus.EN_COURS
        self.robot_carries_flower = False
        self.board = [[CaseType.VIDE for _ in range(width)] for _ in range(height)]
        self.robot_pos = Position(x=0, y=0)
        self.princess_pos = Position(x=0, y=0)
        self.flower_pos = Optional[Position]
        self._generate_board()

    def _generate_board(self):
        """Génère le plateau avec le robot, la princesse, la fleur et les déchets"""
        # Position du robot (coin haut-gauche)
        self.robot_pos = Position(x=0, y=0)
        self.board[0][0] = CaseType.ROBOT

        # Position de la princesse (coin bas-droite)
        self.princess_pos = Position(x=self.width - 1, y=self.height - 1)
        self.board[self.height - 1][self.width - 1] = CaseType.PRINCESSE

        # Position de la fleur (position aléatoire, mais pas sur robot ou princesse)
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in [(0, 0), (self.width - 1, self.height - 1)]:
                self.flower_pos = Position(x=x, y=y)
                self.board[y][x] = CaseType.FLEUR
                break

        # Ajouter des déchets aléatoirement (environ 30% du plateau)
        num_debris = int(self.width * self.height * 0.3)
        debris_count = 0
        while debris_count < num_debris:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.board[y][x] == CaseType.VIDE:
                self.board[y][x] = CaseType.DECHET
                debris_count += 1

    def get_board_string(self) -> str:
        """Retourne le plateau sous forme de chaîne de caractères"""
        result = []
        for row in self.board:
            row_str = "".join([cell.value for cell in row])
            result.append(row_str)
        return "\n".join(result)

    def _get_direction_offset(self, direction: Direction) -> Tuple[int, int]:
        """Convertit une direction en offset (dx, dy)"""
        offsets = {
            Direction.HAUT: (0, -1),
            Direction.BAS: (0, 1),
            Direction.GAUCHE: (-1, 0),
            Direction.DROITE: (1, 0)
        }
        return offsets[direction]

    def _is_valid_position(self, x: int, y: int) -> bool:
        """Vérifie si une position est dans les limites du plateau"""
        return 0 <= x < self.width and 0 <= y < self.height

    def _update_robot_position_on_board(self, old_pos: Position, new_pos: Position):
        """Met à jour la position du robot sur le plateau"""
        self.board[old_pos.y][old_pos.x] = CaseType.VIDE
        self.board[new_pos.y][new_pos.x] = CaseType.ROBOT

    def move_robot(self, direction: Direction) -> bool:
        """Déplace le robot dans la direction donnée"""
        if self.status != GameStatus.EN_COURS:
            return False

        dx, dy = self._get_direction_offset(direction)
        new_x = self.robot_pos.x + dx
        new_y = self.robot_pos.y + dy

        if not self._is_valid_position(new_x, new_y):
            self.status = GameStatus.PERDU
            return False

        target_cell = self.board[new_y][new_x]

        # Le robot peut se déplacer sur les cases vides ou la princesse
        if target_cell in [CaseType.VIDE, CaseType.PRINCESSE]:
            old_pos = Position(x=self.robot_pos.x, y=self.robot_pos.y)
            self.robot_pos.x = new_x
            self.robot_pos.y = new_y
            self._update_robot_position_on_board(old_pos, self.robot_pos)
            return True
        else:
            self.status = GameStatus.PERDU
            return False

    def clean_debris(self, direction: Direction) -> bool:
        """Nettoie une case de déchet dans la direction donnée"""
        if self.status != GameStatus.EN_COURS or self.robot_carries_flower:
            return False

        dx, dy = self._get_direction_offset(direction)
        target_x = self.robot_pos.x + dx
        target_y = self.robot_pos.y + dy

        if not self._is_valid_position(target_x, target_y):
            self.status = GameStatus.PERDU
            return False

        if self.board[target_y][target_x] == CaseType.DECHET:
            self.board[target_y][target_x] = CaseType.VIDE
            return True
        else:
            self.status = GameStatus.PERDU
            return False

    def pick_up_flower(self, direction: Direction) -> bool:
        """Ramasse la fleur dans la direction donnée"""
        if self.status != GameStatus.EN_COURS or self.robot_carries_flower:
            return False

        dx, dy = self._get_direction_offset(direction)
        target_x = self.robot_pos.x + dx
        target_y = self.robot_pos.y + dy

        if not self._is_valid_position(target_x, target_y):
            self.status = GameStatus.PERDU
            return False

        if self.board[target_y][target_x] == CaseType.FLEUR:
            self.board[target_y][target_x] = CaseType.VIDE
            self.robot_carries_flower = True
            self.flower_pos = None
            return True
        else:
            self.status = GameStatus.PERDU
            return False

    def drop_flower(self, direction: Direction) -> bool:
        """Dépose la fleur dans la direction donnée"""
        if self.status != GameStatus.EN_COURS or not self.robot_carries_flower:
            return False

        dx, dy = self._get_direction_offset(direction)
        target_x = self.robot_pos.x + dx
        target_y = self.robot_pos.y + dy

        if not self._is_valid_position(target_x, target_y):
            self.status = GameStatus.PERDU
            return False

        target_cell = self.board[target_y][target_x]

        if target_cell == CaseType.PRINCESSE:
            # Victoire !
            self.robot_carries_flower = False
            self.status = GameStatus.GAGNE
            return True
        elif target_cell == CaseType.VIDE:
            # Dépose la fleur sur une case vide
            self.board[target_y][target_x] = CaseType.FLEUR
            self.flower_pos = Position(x=target_x, y=target_y)
            self.robot_carries_flower = False
            return True
        else:
            self.status = GameStatus.PERDU
            return False


# Stockage des parties en mémoire
games: Dict[str, Game] = {}


class CreateGameRequest(BaseModel):
    width: int = Field(..., ge=3, le=50, description="Largeur du plateau (3-50)")
    height: int = Field(..., ge=3, le=50, description="Hauteur du plateau (3-50)")


class CreateGameResponse(BaseModel):
    game_id: str


class GameInfo(BaseModel):
    game_id: str
    width: int
    height: int
    status: GameStatus


class BoardResponse(BaseModel):
    board: str
    robot_carries_flower: bool
    status: GameStatus


class ActionRequest(BaseModel):
    direction: Direction


class ActionResponse(BaseModel):
    success: bool
    status: GameStatus
    robot_carries_flower: bool


@app.post("/games", response_model=CreateGameResponse)
async def create_game(request: CreateGameRequest):
    """Crée une nouvelle partie"""
    game = Game(request.width, request.height)
    games[game.id] = game
    return CreateGameResponse(game_id=game.id)


@app.get("/games", response_model=List[GameInfo])
async def list_games():
    """Retourne la liste de toutes les parties"""
    return [
        GameInfo(
            game_id=game.id,
            width=game.width,
            height=game.height,
            status=game.status
        )
        for game in games.values()
    ]


@app.get("/games/{game_id}/board", response_model=BoardResponse)
async def get_board(game_id: str):
    """Récupère le plateau d'une partie"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Partie non trouvée")

    game = games[game_id]
    return BoardResponse(
        board=game.get_board_string(),
        robot_carries_flower=game.robot_carries_flower,
        status=game.status
    )


@app.post("/games/{game_id}/move", response_model=ActionResponse)
async def move_robot(game_id: str, request: ActionRequest):
    """Déplace le robot"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Partie non trouvée")

    game = games[game_id]
    success = game.move_robot(request.direction)

    return ActionResponse(
        success=success,
        status=game.status,
        robot_carries_flower=game.robot_carries_flower
    )


@app.post("/games/{game_id}/clean", response_model=ActionResponse)
async def clean_debris(game_id: str, request: ActionRequest):
    """Nettoie une case de déchet"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Partie non trouvée")

    game = games[game_id]
    success = game.clean_debris(request.direction)

    return ActionResponse(
        success=success,
        status=game.status,
        robot_carries_flower=game.robot_carries_flower
    )


@app.post("/games/{game_id}/pickup", response_model=ActionResponse)
async def pickup_flower(game_id: str, request: ActionRequest):
    """Ramasse la fleur"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Partie non trouvée")

    game = games[game_id]
    success = game.pick_up_flower(request.direction)

    return ActionResponse(
        success=success,
        status=game.status,
        robot_carries_flower=game.robot_carries_flower
    )


@app.post("/games/{game_id}/drop", response_model=ActionResponse)
async def drop_flower(game_id: str, request: ActionRequest):
    """Dépose la fleur"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Partie non trouvée")

    game = games[game_id]
    success = game.drop_flower(request.direction)

    return ActionResponse(
        success=success,
        status=game.status,
        robot_carries_flower=game.robot_carries_flower
    )


@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Bienvenue dans le jeu Wall-E !",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)