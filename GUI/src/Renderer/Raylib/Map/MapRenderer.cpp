/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** MapRenderer.cpp
*/

#include "MapRenderer.hpp"
#include "Resource.hpp"

zappy::gui::raylib::MapRenderer::MapRenderer(const std::shared_ptr<game::Map> map) :
    _map(map),
    _lastTime(std::chrono::steady_clock::now()),
    _floor(nullptr),
    _eggs(),
    _players()
{}

void zappy::gui::raylib::MapRenderer::init()
{
    // Init la carte
    _floor = std::make_unique<FlatFloor>(_map->getWidth(), _map->getHeight(), 1);
    _floor->init();

    // Init les resources
    for (size_t i = 0; i < zappy::game::RESOURCE_QUANTITY; ++i) {
        auto type = static_cast<zappy::game::Resource>(i);
        auto model = std::make_unique<zappy::gui::raylib::BasicResourceModel>(-1, type);
        model->init();
        _resourceModels[i] = std::move(model);
    }
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

    _updateMovements(deltaUnits);
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

    // Dessiner les resources
    for (size_t y = 0; y < _map->getHeight(); ++y) {
        for (size_t x = 0; x < _map->getWidth(); ++x) {
            const auto &tile = _map->getTile(x, y);
            const auto &resources = tile.getResources();
            Vector3 basePos = _floor->get3DCoords(x, y);
            float spacing = 0.2f;
            int typeIndex = 0;

            for (size_t i = 0; i < zappy::game::RESOURCE_QUANTITY; ++i) {
                size_t quantity = resources[i];
                if (quantity == 0 || !_resourceModels[i])
                    continue;

                for (size_t q = 0; q < quantity; ++q) {
                    Vector3 pos = {
                        basePos.x + (q % 2) * spacing + (typeIndex % 3) * spacing,
                        basePos.y,
                        basePos.z + (q / 2) * spacing + (typeIndex / 3) * spacing
                    };

                    _resourceModels[i]->setPosition(pos);
                    _resourceModels[i]->render();
                }

                typeIndex++;
            }
        }
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
    Translation translation = _floor->createTranslation(player, x, y, FORWARD_TIME);

    _movementQueues[id].push(translation);

    player.setGamePosition(Vector2{ static_cast<float>(x), static_cast<float>(y) });
}

void zappy::gui::raylib::MapRenderer::playerExpulsion(const int &id, const int &x, const int &y)
{
    if (_players.empty())
        return;

    auto &player = _getPlayer(id);

    Translation translation = _floor->createTranslation(player, x, y, EXPULSION_TIME);

    _movementQueues[id].push(translation);

    player.setGamePosition(Vector2{ static_cast<float>(x), static_cast<float>(y) });
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

    Rotation rotation = {
        player.getId(),
        MovementType::ROTATION,
        destination,
        perStep,
        ROTATION_TIME,
        0
    };

    _movementQueues[player.getId()].push(rotation);
}

void zappy::gui::raylib::MapRenderer::_updateMovements(const float &deltaUnits)
{
    for (auto it = _movementQueues.begin(); it != _movementQueues.end(); ) {
        auto &queue = it->second;
        if (queue.empty()) {
            it = _movementQueues.erase(it);
            continue;
        }

        Movement &m = queue.front();
        APlayerModel &p = _getPlayer(m.id);

        if (m.elapsedTime + deltaUnits >= m.timeUnits) {
            if (m.type == MovementType::TRANSLATION)
                p.setPosition(m.destination);
            else if (m.type == MovementType::ROTATION)
                p.rotate(Vector3Subtract(m.destination, p.getRotation()));
            queue.pop();
        } else {
            if (m.type == MovementType::TRANSLATION)
                _floor->translate(deltaUnits, m.movementVector, m.destination, p);
            else if (m.type == MovementType::ROTATION)
                p.rotate(Vector3Scale(m.movementVector, deltaUnits));
            m.elapsedTime += deltaUnits;
        }
        ++it;
    }
}
