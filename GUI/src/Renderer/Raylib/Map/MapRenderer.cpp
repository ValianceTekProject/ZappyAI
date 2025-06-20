/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** MapRenderer.cpp
*/

#include "MapRenderer.hpp"

zappy::gui::raylib::MapRenderer::MapRenderer(const std::shared_ptr<game::Map> map) :
    _map(map),
    _lastTime(std::chrono::steady_clock::now()),
    _floor(nullptr),
    _eggs(),
    _players(),
    _translations(),
    _rotations()
{}

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

    auto now = std::chrono::steady_clock::now();
    float deltaSec = std::chrono::duration<float>(now - _lastTime).count();
    _lastTime = now;

    // Convertit en “unités d’action” : (secondes écoulées) * fréquence
    float deltaUnits = deltaSec * frequency;

    _updateTranslations(frequency);
    _updateRotations(deltaUnits);
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

    auto &player = _getPlayer(id);
    player.lookLeft();

    constexpr float rotationAngle = 90.0f;

    _addRotation(player, rotationAngle);
}

void zappy::gui::raylib::MapRenderer::playerLookRight(const int &id)
{
    if (_players.empty())
        return;

    auto &player = _getPlayer(id);
    player.lookRight();

    constexpr float rotationAngle = -90.0f;

    _addRotation(player, rotationAngle);
}

void zappy::gui::raylib::MapRenderer::playerForward(const int &id, const int &x, const int &y)
{
    if (_players.empty())
        return;

    auto &player = _getPlayer(id);
    Vector3 dest = _floor->get3DCoords(x, y);
    Vector3 cur = player.getPosition();
    Vector3 direction = Vector3Subtract(dest, cur);

    Vector3 step = Vector3Scale(direction, 1.0f / static_cast<float>(FORWARD_TIME));

    Translation t;
    t.id = id;
    t.destination = dest;
    t.translationVector = step;
    t.timeUnit = FORWARD_TIME;
    _translations.push_back(t);

    player.setGamePosition(Vector2{ static_cast<float>(x), static_cast<float>(y) });
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

void zappy::gui::raylib::MapRenderer::_addRotation(const APlayerModel &player, const float &angle)
{
    Vector3 current = player.getRotation();
    Vector3 destination = {current.x, current.y + angle, current.z};

    Vector3 totalDelta = Vector3Subtract(destination, current);
    Vector3 perStep = Vector3Scale(totalDelta, 1.0f / static_cast<float>(ROTATION_TIME));

    // check if there is no rotation so put ROTATION_TIME to 0
    for (auto &rotation : _rotations) {
        if (rotation.id == player.getId()) {
            rotation.destination = destination;
            rotation.deltaPerStep = perStep;
            rotation.timeUnits = ROTATION_TIME;
            rotation.elapsedTime = 0;
            return;
        }
    }

    _rotations.push_back(Rotation{
        player.getId(),
        destination,
        perStep,
        ROTATION_TIME,
        0
    });
}

void zappy::gui::raylib::MapRenderer::_updateTranslations(const int &frequency)
{
    auto it = _translations.begin();

    while (it != _translations.end()) {
        auto &T = *it;
        auto &player = _getPlayer(T.id);

        Vector3 delta = Vector3Scale(T.translationVector, frequency);

        Vector3 cur = player.getPosition();
        Vector3 dest = T.destination;
        Vector3 remaining = Vector3Subtract(dest, cur);

        bool readyX = std::fabs(remaining.x) <= std::fabs(delta.x);
        bool readyY = std::fabs(remaining.y) <= std::fabs(delta.y);
        bool readyZ = std::fabs(remaining.z) <= std::fabs(delta.z);

        if (readyX && readyY && readyZ) {
            player.setPosition(dest);
            it = _translations.erase(it);
        } else {
            player.translate(delta);
            ++it;
        }
    }
}

void zappy::gui::raylib::MapRenderer::_updateRotations(const float &deltaUnits)
{
    if (_rotations.empty()) return;

    auto it = _rotations.begin();
    while (it != _rotations.end()) {
        auto &R = *it;
        auto &player = _getPlayer(R.id);

        if (R.elapsedTime + deltaUnits >= R.timeUnits) {
            Vector3 cur = player.getRotation();
            Vector3 remaining = Vector3Subtract(R.destination, cur);
            player.rotate(remaining);
            it = _rotations.erase(it);
        } else {
            Vector3 step = Vector3Scale(R.deltaPerStep, deltaUnits);
            player.rotate(step);
            R.elapsedTime += deltaUnits;
            ++it;
        }
    }
}
