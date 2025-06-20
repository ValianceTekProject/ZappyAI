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

void zappy::gui::raylib::MapRenderer::update(const int &frequency)
{
    // Mettre à jour la carte
    _floor->update();

    // Mettre à jour les players
    if (!_players.empty()) {
        for (auto &player : _players)
            player->update();
    }

    // Mettre à jour les oeufs
    if (!_eggs.empty()) {
        for (auto &egg : _eggs)
            egg->update();
    }

    _updateTranslations(frequency);
    _updateRotations(frequency);
}

void zappy::gui::raylib::MapRenderer::render()
{
    // Dessiner la carte
    _floor->render();

    // Dessiner les players
    if (!_players.empty()) {
        for (auto &player : _players) {
            player->render();
        }
    }

    // Dessiner les oeufs
    if (!_eggs.empty()) {
        for (auto &egg : _eggs)
            egg->render();
    }
}

void zappy::gui::raylib::MapRenderer::addEgg(std::unique_ptr<AEggModel> egg)
{
    egg->init();

    _eggs.push_back(std::move(egg));
}

void zappy::gui::raylib::MapRenderer::addPlayer(std::unique_ptr<APlayerModel> player)
{
    player->init();

    _players.push_back(std::move(player));
}

void zappy::gui::raylib::MapRenderer::setEggPosition(const int &id, const int &x, const int &y)
{
    if (_eggs.empty())
        return;

    auto &egg = this->_getEgg(id);
    Vector3 position3D = _floor->get3DCoords(x, y);

    egg.setPosition(position3D);
}

void zappy::gui::raylib::MapRenderer::setPlayerPosition(const int &id, const int &x, const int &y, const game::Orientation &orientation)
{

    if (_players.empty())
        return;

    auto &player = this->_getPlayer(id);
    Vector3 postion3D = _floor->get3DCoords(x, y);

    player.setPosition(postion3D);

    player.setGamePosition(Vector2{
        static_cast<float>(x),
        static_cast<float>(y)
    });
    player.look(orientation);
}

void zappy::gui::raylib::MapRenderer::playerLook(const int &id, const game::Orientation &orientation)
{
    if (_players.empty())
        return;

    auto &player = this->_getPlayer(id);

    player.look(orientation);
}

void zappy::gui::raylib::MapRenderer::playerLookLeft(const int &id)
{
    if (_players.empty())
        return;

    auto &player = this->_getPlayer(id);
    constexpr Vector3 rotationVector = {0.0f, -90.0f, 0.0f};

    Vector3 playerRotation = player.getRotation();
    Vector3 destination = Vector3Add(playerRotation, rotationVector);
    Vector3 Vector = Vector3Subtract(destination, playerRotation);

    player.lookLeft();

    _rotations.push_back(Rotation{
        id,
        destination,
        Vector,
        ROTATION_TIME
    });
}

void zappy::gui::raylib::MapRenderer::playerLookRight(const int &id)
{
    if (_players.empty())
        return;

    auto &player = _getPlayer(id);
    constexpr Vector3 rotationVector = {0.0f, -90.0f, 0.0f};

    Vector3 playerRotation = player.getRotation();
    Vector3 destination = Vector3Add(playerRotation, rotationVector);
    Vector3 Vector = Vector3Subtract(destination, playerRotation);

    player.lookRight();

    _rotations.push_back(Rotation{
        id,
        destination,
        Vector,
        ROTATION_TIME
    });
}

void zappy::gui::raylib::MapRenderer::playerForward(const int &id, const int &x, const int &y)
{
    if (_players.empty())
        return;

    // Mettre à jour la position d'un joueur
    (void)id;
    (void)x;
    (void)y;
}

void zappy::gui::raylib::MapRenderer::playerExpulsion(const int &id, const int &x, const int &y)
{
    if (_players.empty())
        return;

    // Mettre à jour la position d'un joueur
    (void)id;
    (void)x;
    (void)y;
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

zappy::gui::raylib::APlayerModel &zappy::gui::raylib::MapRenderer::_getPlayer(const int &id)
{
    for (auto &player : _players) {
        if (player->getId() == id)
            return *player;
    }
    throw RendererError("Player " + std::to_string(id) + " not found", "MapRenderer");
}

const zappy::gui::raylib::APlayerModel &zappy::gui::raylib::MapRenderer::_getPlayer(const int &id) const
{
    for (const auto &player : _players) {
        if (player->getId() == id)
            return *player;
    }
    throw RendererError("Player " + std::to_string(id) + " not found", "MapRenderer");
}

zappy::gui::raylib::AEggModel &zappy::gui::raylib::MapRenderer::_getEgg(const int &id)
{
    for (auto &egg : _eggs) {
        if (egg->getId() == id)
            return *egg;
    }
    throw RendererError("Egg " + std::to_string(id) + " not found", "MapRenderer");
}

const zappy::gui::raylib::AEggModel &zappy::gui::raylib::MapRenderer::_getEgg(const int &id) const
{
    for (const auto &egg : _eggs) {
        if (egg->getId() == id)
            return *egg;
    }
    throw RendererError("Egg " + std::to_string(id) + " not found", "MapRenderer");
}

void zappy::gui::raylib::MapRenderer::_updateTranslations(const int &frequency)
{
    if (_translations.empty())
        return;

    // Mettre à jour la position d'un joueur
    (void)frequency;
}

void zappy::gui::raylib::MapRenderer::_updateRotations(const int &frequency)
{
    auto it = _rotations.begin();

    while (it != _rotations.end()) {
        const auto &R = *it;
        auto &player = _getPlayer(R.id);

        // calculate delta time
        Vector3 delta = Vector3Scale(R.rotationVector, frequency);

        Vector3 cur       = player.getRotation();
        Vector3 dest      = R.destination;
        Vector3 remaining = {
            dest.x - cur.x,
            dest.y - cur.y,
            dest.z - cur.z
        };

        // check over rotation and stop rotation
        bool readyX = std::fabs(remaining.x) <= std::fabs(delta.x);
        bool readyY = std::fabs(remaining.y) <= std::fabs(delta.y);
        bool readyZ = std::fabs(remaining.z) <= std::fabs(delta.z);

        if (readyX && readyY && readyZ) {
            player.rotate(remaining);
            it = _rotations.erase(it);
        } else {
            player.rotate(delta);
            ++it;
        }
    }
}
