/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** MapRenderer.cpp
*/

#include "MapRenderer.hpp"

zappy::gui::raylib::MapRenderer::MapRenderer(const std::shared_ptr<game::Map> map) :
    _map(map) {}

void zappy::gui::raylib::MapRenderer::init()
{
    // Init la carte
    _floor = std::make_unique<FlatFloor>(_map->getWidth(), _map->getHeight(), 1);
    _floor->init();
}

void zappy::gui::raylib::MapRenderer::update()
{
    // Mettre à jour la carte
    _floor->update();

    // Mettre à jour les players
    if (!_players.empty()) {
        for (const auto &player : _players)
            player->update();
    }

    // Mettre à jour les oeufs
    if (!_eggs.empty()) {
        for (const auto &egg : _eggs)
            egg->update();
    }
}

void zappy::gui::raylib::MapRenderer::render()
{
    // Dessiner la carte
    _floor->render();

    // Dessiner les players
    if (!_players.empty()) {
        for (const auto &player : _players)
            player->render();
    }

    // Dessiner les oeufs
    if (!_eggs.empty()) {
        for (const auto &egg : _eggs)
            egg->render();
    }
}

void zappy::gui::raylib::MapRenderer::addEgg(std::unique_ptr<IEggModel> egg)
{
    _eggs.push_back(std::move(egg));
}

void zappy::gui::raylib::MapRenderer::addPlayer(std::unique_ptr<IPlayerModel> player)
{
    _players.push_back(std::move(player));
}

void zappy::gui::raylib::MapRenderer::removeEgg(const int &id)
{
    for (auto it = _eggs.begin(); it != _eggs.end(); it++) {
        if ((*it)->getId() == id) {
            _eggs.erase(it);
            break;
        }
    }
}

void zappy::gui::raylib::MapRenderer::removePlayer(const int &id)
{
    for (auto it = _players.begin(); it != _players.end(); it++) {
        if ((*it)->getId() == id) {
            _players.erase(it);
            break;
        }
    }
}

void zappy::gui::raylib::MapRenderer::setEggPosition(const int &id, const size_t &x, const size_t &y)
{
    for (auto &egg : _eggs) {
        if (egg->getId() == id) {
            egg->setPosition(_floor->get3DCoords(x, y));
            break;
        }
    }
}

void zappy::gui::raylib::MapRenderer::setPlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation)
{
    for (auto &player : _players) {
        if (player->getId() == id) {
            player->setPosition(_floor->get3DCoords(x, y));
            player->look(orientation);
            break;
        }
    }
}
