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
    addPlayer(0);
    addPlayer(1);
}

void zappy::gui::raylib::BasicScene::handleInput(InputManager &inputManager)
{
    AScene::handleInput(inputManager);
}

void zappy::gui::raylib::BasicScene::update()
{
    AScene::update();
    StartIncantation(3, 3, 2, {0, 1});
    StartIncantation(5, 5, 2, {0, 1});
    StartIncantation(6, 6, 2, {0, 1});
}

void zappy::gui::raylib::BasicScene::render() const
{
    BeginMode3D(getCamera());

    _mapRenderer->render();

    EndMode3D();
}

bool zappy::gui::raylib::BasicScene::shouldClose() const
{
    return WindowShouldClose();
}

void zappy::gui::raylib::BasicScene::addEgg(const int &id)
{
    auto egg = std::make_unique<BasicEggModel>(id);

    _mapRenderer->addEgg(std::move(egg));

    AScene::addEgg(id);
}

void zappy::gui::raylib::BasicScene::addPlayer(const int &id)
{
    auto player = std::make_unique<BasicPlayerModel>(id);

    _mapRenderer->addPlayer(std::move(player));

    AScene::addPlayer(id);
}

void zappy::gui::raylib::BasicScene::updatePlayerPosition(const int &id, const int &x, const int &y, const game::Orientation &orientation)
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

void zappy::gui::raylib::BasicScene::StartIncantation(const int &x, const int &y, const int &level, const std::vector<int> &playerIds)
{
    (void)x;
    (void)y;
    (void)level;
    (void)playerIds;
    _mapRenderer->setIncantationTile(x, y);
}

void zappy::gui::raylib::BasicScene::EndIncantation(const int &x, const int &y, const bool &result)
{
    (void)x;
    (void)y;
    (void)result;
    _mapRenderer->clearIncantationTile();
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
