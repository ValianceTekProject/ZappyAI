/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** FlatFloor.cpp
*/

#include "FlatFloor.hpp"
#include "raylib.h"
#include <algorithm>
#include "raymath.h"

zappy::gui::raylib::FlatFloor::FlatFloor(const size_t &width, const size_t &height, const float &tileSize) :
    AFloor::AFloor(width, height, tileSize)
{}

void zappy::gui::raylib::FlatFloor::init()
{
    AFloor::init();
    _texture = LoadTexture(assets::FLOOR_PATH.c_str());

    TraceLog(LOG_INFO, "Texture ID: %d", _texture.id);
    TraceLog(LOG_INFO, "Texture size: %dx%d", _texture.width, _texture.height);

    Mesh mesh = GenMeshPlane(1.0f, 1.0f, 1, 1);
    _model = LoadModelFromMesh(mesh);
    _model.materials[0].maps[MATERIAL_MAP_DIFFUSE].texture = _texture;
}

void zappy::gui::raylib::FlatFloor::update() const {}

void zappy::gui::raylib::FlatFloor::render() const
{
    float tileSize = static_cast<float>(getTileSize());
    float startX = -(getWidth() * tileSize) / 2.0f;
    float startZ = -(getHeight() * tileSize) / 2.0f;

    for (size_t x = 0; x < getWidth(); ++x) {
        for (size_t z = 0; z < getHeight(); ++z) {
            float posX = startX + x * tileSize + tileSize / 2.0f;
            float posZ = startZ + z * tileSize + tileSize / 2.0f;

            Vector3 position = {posX, 0.0f, posZ};
            Vector3 scale = {tileSize, 1.0f, tileSize};
            DrawModelEx(_model, position, {0.0f, 1.0f, 0.0f}, 0.0f, scale, WHITE);
        }
    }
}

Vector3 zappy::gui::raylib::FlatFloor::get3DCoords(const size_t &x, const size_t &y) const
{
    size_t tileSize = getTileSize();
    Vector3 vector;

    vector.x = x * tileSize;
    vector.z = (-y) * tileSize;
    return vector;
}
