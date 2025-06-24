/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** AScene.cpp
*/

#include "AScene.hpp"

zappy::gui::raylib::AScene::AScene(const std::shared_ptr<game::GameState> &gameState) :
    _camera(Camera()),
    _gameState(gameState),
    _mapRenderer(std::make_unique<MapRenderer>(_gameState->getMap()))
{}

void zappy::gui::raylib::AScene::init()
{
    // Initialize Camera
    _camera.position = Vector3{ 10.0f, 10.0f, 10.0f };
    _camera.target = Vector3{ 0.0f, 0.0f, 0.0f };
    _camera.up = Vector3{ 0.0f, 0.9f, 0.0f };
    _camera.fovy = 45.0f;
    _camera.projection = CAMERA_PERSPECTIVE;

    _mapRenderer->init();
}

void zappy::gui::raylib::AScene::update()
{
    _mapRenderer->update(_gameState->getFrequency());
}

void zappy::gui::raylib::AScene::handleInput(InputManager &inputManager)
{
    // Gérer les entrées de l'utilisateur
    (void)inputManager;
}

void zappy::gui::raylib::AScene::addEgg(const int &id)
{
    // Egg supposed to be added to the map
    game::Egg egg = _gameState->getEggById(id);

    _mapRenderer->setEggPosition(id, egg.x, egg.y);
}

void zappy::gui::raylib::AScene::addPlayer(const int &id)
{
    // Player supposed to be added to the map
    game::Player player = _gameState->getPlayerById(id);

    _mapRenderer->setPlayerPosition(id, player.x, player.y, player.orientation);
}

void zappy::gui::raylib::AScene::updatePlayerPosition(const int &id, const int &x, const int &y, const game::Orientation &orientation)
{
    game::Player player = _gameState->getPlayerById(id);

    if (player.orientation != orientation) {
        if (orientation == player.orientation - 1)
            _mapRenderer->playerLookLeft(player.getId());
        else if (orientation == player.orientation + 1)
            _mapRenderer->playerLookRight(player.getId());
        else
            _mapRenderer->playerLook(player.getId(), orientation);
    } else {
        // determine if the player go forward
        if (player.x == x && player.y == y)
            return;
        int mapWidth = static_cast<int>(_gameState->getMap()->getWidth());
        int mapHeight = static_cast<int>(_gameState->getMap()->getHeight());
        if (player.x == x) {
            if ((y == (player.y + 1) % mapHeight && player.orientation == game::Orientation::NORTH) ||
                (y == (player.y - 1) % mapHeight && player.orientation == game::Orientation::SOUTH)) {
                    _mapRenderer->playerForward(player.getId(), x, y);
            }
        } else if (player.y == y) {
            if ((x == (player.x + 1) % mapWidth && player.orientation == game::Orientation::EAST) ||
                (x == (player.x - 1) % mapWidth && player.orientation == game::Orientation::WEST)) {
                    _mapRenderer->playerForward(player.getId(), x, y);
            }
        }
    }
}

void zappy::gui::raylib::AScene::updatePlayerLevel(const int &id, const size_t &level)
{
    // Mettre à jour le niveau d'un joueur
    (void)id;
    (void)level;
}

void zappy::gui::raylib::AScene::updatePlayerInventory(const int &id, const game::Inventory &inventory)
{
    // Mettre à jour l'inventaire d'un joueur
    (void)id;
    (void)inventory;
}

void zappy::gui::raylib::AScene::PlayerExpulsion(const int &id)
{
    game::Player &playerThatExpelled = _gameState->getPlayerById(id);
    game::Orientation orientation = playerThatExpelled.orientation;

    auto expelledPlayers = _gameState->getPlayersByCoord(
        playerThatExpelled.x, playerThatExpelled.y
    );

    for (auto &player : expelledPlayers) {
        game::Player &p = player.get();
        if (player.get().getId() == id)
            continue;

        int newX = (playerThatExpelled.x + (1 * (orientation == game::Orientation::WEST ? -1 : 1)))
            % _gameState->getMap()->getWidth();
        int newY = (playerThatExpelled.y + (1 * (orientation == game::Orientation::SOUTH ? -1 : 1)))
            % _gameState->getMap()->getHeight();

        _mapRenderer->playerExpulsion(p.getId(), newX, newY);
    }
}

void zappy::gui::raylib::AScene::PlayerBroadcast(const int &id, const std::string &message)
{
    // Envoyer un message à un joueur
    (void)id;
    (void)message;
}

void zappy::gui::raylib::AScene::StartIncantation(
    const int &x, const int &y,
    const int &level,
    const std::vector<int> &playerIds
) {
    // Démarrer une incantation
    (void)x;
    (void)y;
    (void)level;
    (void)playerIds;
}

void zappy::gui::raylib::AScene::EndIncantation(const int &x, const int &y, const bool &result)
{
    // Terminer une incantation
    (void)x;
    (void)y;
    (void)result;
}

void zappy::gui::raylib::AScene::hatchEgg(const int &id)
{
    // Incuber un œuf
    (void)id;
}

void zappy::gui::raylib::AScene::removeEgg(const int &id)
{
    // Supprimer un œuf
    (void)id;
}

void zappy::gui::raylib::AScene::removePlayer(const int &id)
{
    // Supprimer un joueur
    (void)id;
}
