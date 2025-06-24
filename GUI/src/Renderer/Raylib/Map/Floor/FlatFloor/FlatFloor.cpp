/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** FlatFloor.cpp
*/

#include "FlatFloor.hpp"
#include "IFloor.hpp"
#include "Orientation.hpp"
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
    float tileSize = this->getTileSize();
    float startX = -(this->getWidth() * tileSize) / 2.0f;
    float startZ = -(this->getHeight() * tileSize) / 2.0f;

    for (size_t x = 0; x < this->getWidth(); ++x) {
        for (size_t z = 0; z < this->getHeight(); ++z) {
            float posX = startX + x * tileSize + tileSize / 2.0f;
            float posZ = startZ + z * tileSize + tileSize / 2.0f;

            Vector3 position = {posX, 0.0f, posZ};
            Vector3 scale = {tileSize, 1.0f, tileSize};
            DrawModelEx(_model, position, {0.0f, 1.0f, 0.0f}, 0.0f, scale, WHITE);
        }
    }
}

Vector3 zappy::gui::raylib::FlatFloor::getGapFromOrientation(const game::Orientation &orientation)
{
    switch (orientation) {
        case game::Orientation::NORTH:
            return {0.0f, 0.0f, 0.0f};
        case game::Orientation::EAST:
            return {0.0f, 90.0f, 0.0f};
        case game::Orientation::SOUTH:
            return {0.0f, 180.0f, 0.0f};
        case game::Orientation::WEST:
            return {0.0f, 270.0f, 0.0f};
    }
    return {0.0f, 0.0f, 0.0f};
}

Vector3 zappy::gui::raylib::FlatFloor::getNorthVector(const game::Orientation &orientation)
{
    switch (orientation) {
        case game::Orientation::NORTH:
            return {0.0f, 0.0f, 1.0f};
        case game::Orientation::EAST:
            return {1.0f, 0.0f, 0.0f};
        case game::Orientation::SOUTH:
            return {0.0f, 0.0f, -1.0f};
        case game::Orientation::WEST:
            return {-1.0f, 0.0f, 0.0f};
    }
    return {0.0f, 0.0f, 0.0f};
}

Vector3 zappy::gui::raylib::FlatFloor::get3DCoords(const int &x, const int &y) const
{
    const float tileSize = this->getTileSize();
    const float worldWidth = this->getWidth() * tileSize;
    const float worldDepth = this->getHeight() * tileSize;

    const float offsetX = -worldWidth * 0.5f + tileSize * 0.5f;
    const float offsetZ =  worldDepth * 0.5f - tileSize * 0.5f;

    Vector3 pos;
    pos.x = offsetX + x * tileSize;
    pos.y = 0.0f;
    pos.z = offsetZ - y * tileSize;
    return pos;
}

zappy::gui::raylib::Translation zappy::gui::raylib::FlatFloor::createTranslation(const APlayerModel &player, const int &x, const int &y, const int &timeUnit)
{
    const int width = static_cast<int>(this->getWidth());
    const int height = static_cast<int>(this->getHeight());

    int finalDestX = x;
    int finalDestY = y;
    Vector2 playerGamePos = player.getGamePosition();

    if (playerGamePos.x == 0 && finalDestX == width - 1) {
        finalDestX -= width;
    } else if (playerGamePos.x == width - 1 && finalDestX == 0) {
        finalDestX += width;
    } else if (playerGamePos.y == 0 && finalDestY == height - 1) {
        finalDestY -= height;
    } else if (playerGamePos.y == height - 1 && finalDestY == 0) {
        finalDestY += height;
    }

    Vector3 cur = player.getPosition();
    Vector3 dest = get3DCoords(finalDestX, finalDestY);
    Vector3 direction = Vector3Subtract(dest, cur);
    Vector3 unitStep = Vector3Scale(direction, 1.0f / static_cast<float>(timeUnit));

    Translation t;
    t.id = player.getId();
    t.destination = dest;
    t.translationVector = unitStep;
    t.timeUnits = timeUnit;
    t.elapsedTime = 0.0f;

    return t;
}

void zappy::gui::raylib::FlatFloor::translate(const float &deltaUnits, const Vector3 &translationVector, Vector3 &destination, APlayerModel &player)
{
    Vector3 step = Vector3Scale(translationVector, deltaUnits);
    player.translate(step);
    _checkOverlap(player, destination);
}

void zappy::gui::raylib::FlatFloor::_checkOverlap(APlayerModel &player, Vector3 &destination)
{
    const float tileSize = this->getTileSize();
    const size_t width = this->getWidth();
    const size_t height = this->getHeight();

    const float widthOverlap = width * tileSize / 2;
    const float heightOverlap = height * tileSize / 2;

    const float mapWidth = width * tileSize;
    const float mapHeight = height * tileSize;

    Vector3 playerPos = player.getPosition();

    if (playerPos.x >= widthOverlap) {
        player.setPosition(Vector3{playerPos.x - mapWidth, playerPos.y, playerPos.z});
        destination.x -= mapWidth;
    } else if (playerPos.x <= (widthOverlap - mapWidth)) {
        player.setPosition(Vector3{playerPos.x + mapWidth, playerPos.y, playerPos.z});
        destination.x += mapWidth;
    } else if (playerPos.z >= heightOverlap) {
        player.setPosition(Vector3{playerPos.x, playerPos.y, playerPos.z - mapHeight});
        destination.z -= mapHeight;
    } else if (playerPos.z <= (widthOverlap - mapHeight)) {
        player.setPosition(Vector3{playerPos.x, playerPos.y, playerPos.z + mapHeight});
        destination.z += mapHeight;
    }
}
