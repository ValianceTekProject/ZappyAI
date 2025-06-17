/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** MapRenderer.cpp
*/

#include "MapRenderer.hpp"
#include <memory>
#include <utility>

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
    _floor->update();
    if (!_players.empty()) {
        for (const auto &player : _players)
            player->update();
    }
    // Mettre à jour la carte
}

void zappy::gui::raylib::MapRenderer::render()
{
    // Dessiner la carte
    _floor->render();
    if (!_players.empty()) {
        for (const auto &player : _players)
            player->render();
    }
}

void zappy::gui::raylib::MapRenderer::addPlayer(std::unique_ptr<IPlayerModel> player)
{
    _players.push_back(std::move(player));
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
