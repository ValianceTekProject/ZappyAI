/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** BasicScene.cpp
*/

#include "BasicScene.hpp"

zappy::gui::raylib::BasicScene::BasicScene(const std::shared_ptr<game::GameState> &gameState) :
    AScene::AScene(gameState)
{}

void zappy::gui::raylib::BasicScene::init()
{
    AScene::init();
}

void zappy::gui::raylib::BasicScene::handleInput(InputManager &inputManager)
{
    AScene::handleInput(inputManager);
}

void zappy::gui::raylib::BasicScene::update()
{
    AScene::update();
}

void zappy::gui::raylib::BasicScene::render() const
{
    if (!_gameState || !_gameState->getMap())
        return;

    const auto &map = _gameState->getMap();

    for (size_t x = 0; x < map->getWidth(); ++x) {
        for (size_t y = 0; y < map->getHeight(); ++y) {
            // Coordonnées du coin haut-gauche de la case
            Vector2 pos = {(float)x * 40.0f, (float)y * 40.0f};

            // Sol en bleu clair
            DrawRectangleV(pos, {40, 40}, SKYBLUE);

            // Bordure de case
            DrawRectangleLines(pos.x, pos.y, 40, 40, DARKBLUE);

            // Dessiner les joueurs comme des cercles bleus
            if (!_gameState->getPlayers().empty()) {
                for (const auto &player : _gameState->getPlayers()) {
                    if (player.x == (int)x && player.y == (int)y) {
                        DrawCircle(pos.x + 20, pos.y + 20, 10, BLUE); // cercle centré
                    }
                }
            }

            // Dessiner les œufs comme des petits cercles violets
            if (!_gameState->getEggs().empty()) {
                for (const auto &egg : _gameState->getEggs()) {
                    if (egg.x == (int)x && egg.y == (int)y) {
                        DrawCircle(pos.x + 20, pos.y + 20, 5, PURPLE);
                    }
                }
            }
        }
    }
}

bool zappy::gui::raylib::BasicScene::shouldClose() const
{
    return WindowShouldClose();
}

void zappy::gui::raylib::BasicScene::addEgg(const int &id)
{
    AScene::addEgg(id);
}

void zappy::gui::raylib::BasicScene::addPlayer(const int &id)
{
    AScene::addPlayer(id);
}

void zappy::gui::raylib::BasicScene::updatePlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation)
{
    AScene::updatePlayerPosition(id, x, y, orientation);
}

void zappy::gui::raylib::BasicScene::updatePlayerLevel(const int &id, const size_t &level)
{
    AScene::updatePlayerLevel(id, level);
}

void zappy::gui::raylib::BasicScene::updatePlayerInventory(const int &id, const game::Inventory &inventory)
{
    AScene::updatePlayerInventory(id, inventory);
}

void zappy::gui::raylib::BasicScene::hatchEgg(const int &id)
{
    AScene::hatchEgg(id);
}

void zappy::gui::raylib::BasicScene::removeEgg(const int &id)
{
    AScene::removeEgg(id);
}

void zappy::gui::raylib::BasicScene::removePlayer(const int &id)
{
    AScene::removePlayer(id);
}

void zappy::gui::raylib::BasicScene::endGame(const std::string &teamName)
{
    DrawText(TextFormat("Team %s wins!", teamName.c_str()), 10, 10, 20, GREEN);
}
