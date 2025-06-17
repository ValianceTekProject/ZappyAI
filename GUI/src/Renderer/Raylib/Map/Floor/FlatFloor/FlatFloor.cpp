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

zappy::gui::raylib::FlatFloor::FlatFloor(size_t width, size_t height, size_t tileSize) :
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
    for (size_t i = 0; i <= getWidth(); i++) {
        float x = startX + i * tileSize;
        Vector3 start = {x, 0.01f, startZ};
        Vector3 end = {x, 0.01f, startZ + getHeight() * tileSize};
        DrawLine3D(start, end, GRAY);
    }

    for (size_t j = 0; j <= getHeight(); j++) {
        float z = startZ + j * tileSize;
        Vector3 start = {startX, 0.01f, z};
        Vector3 end = {startX + getWidth() * tileSize, 0.01f, z};
        DrawLine3D(start, end, GRAY);
    }
}

