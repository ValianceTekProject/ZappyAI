/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** MapRenderer.cpp
*/

#include "MapRenderer.hpp"
#include <memory>

zappy::gui::raylib::MapRenderer::MapRenderer(const std::shared_ptr<game::Map> map) :
    _map(map) {}

void zappy::gui::raylib::MapRenderer::init()
{
    _floor = std::make_unique<FlatFloor>(_map->getWidth(), _map->getHeight(), 1);
}

void zappy::gui::raylib::MapRenderer::update()
{
    // Mettre à jour la carte
}

void zappy::gui::raylib::MapRenderer::render()
{
    // Dessiner la carte
    _floor->render();
}
