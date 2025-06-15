/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** BasicScene.cpp
*/

#include "BasicScene.hpp"

void zappy::gui::raylib::BasicScene::init(const std::shared_ptr<game::GameState> &gameState)
{
    AScene::init(gameState);
}

void zappy::gui::raylib::BasicScene::update()
{}

void zappy::gui::raylib::BasicScene::render() const
{
    if (!_gameState)
        return;

    const auto &map = _gameState->getMap();
    for (size_t x = 0; x < map->getWidth(); ++x) {
        for (size_t y = 0; y < map->getHeight(); ++y) {
            Vector2 pos = {(float)x * 40.0f, (float)y * 40.0f};
            DrawRectangleV(pos, {38, 38}, LIGHTGRAY);

            // Draw number of players
            size_t count = 0;
            for (const auto &player : _gameState->getPlayers()) {
                if (player.x == x && player.y == y)
                    ++count;
            }
            if (count > 0) {
                DrawText(TextFormat("P:%d", (int)count), pos.x + 4, pos.y + 4, 10, DARKBLUE);
            }

            // Draw number of eggs
            size_t eggCount = 0;
            for (const auto &egg : _gameState->getEggs()) {
                if (egg.x == x && egg.y == y)
                    ++eggCount;
            }
            if (eggCount > 0) {
                DrawText(TextFormat("E:%d", (int)eggCount), pos.x + 4, pos.y + 16, 10, DARKPURPLE);
            }
        }
    }
}

void zappy::gui::raylib::BasicScene::handleInput(InputManager &inputManager)
{
    // Gérer les entrées de l'utilisateur
}

void zappy::gui::raylib::BasicScene::addEgg(const int &id)
{}

void zappy::gui::raylib::BasicScene::addPlayer(const int &id)
{}

void zappy::gui::raylib::BasicScene::updatePlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation)
{}

void zappy::gui::raylib::BasicScene::updatePlayerLevel(const int &id, const size_t &level)
{}

void zappy::gui::raylib::BasicScene::updatePlayerInventory(const int &id, const game::Inventory &inventory)
{}

void zappy::gui::raylib::BasicScene::hatchEgg(const int &id)
{}

void zappy::gui::raylib::BasicScene::removeEgg(const int &id)
{}

void zappy::gui::raylib::BasicScene::removePlayer(const int &id)
{}

void zappy::gui::raylib::BasicScene::endGame(const std::string &teamName)
{
    DrawText(TextFormat("Team %s wins!", teamName.c_str()), 10, 10, 20, GREEN);
}
