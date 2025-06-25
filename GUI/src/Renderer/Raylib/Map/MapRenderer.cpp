/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** MapRenderer.cpp
*/

#include "MapRenderer.hpp"
#include "Resource.hpp"
#include <rlgl.h>

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

    _updateTranslations(deltaUnits);
    _updateRotations(deltaUnits);
    _updateIncantationAnimation(deltaSec);
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

    // Dessiner les ressources
    renderResources();

    // Dessiner les incantations
    renderIncantations();
}

void zappy::gui::raylib::MapRenderer::renderResources()
{
    constexpr float uniformHeight = 0.1f;
    float spacing = 0.2f;

    for (size_t y = 0; y < _map->getHeight(); ++y) {
        for (size_t x = 0; x < _map->getWidth(); ++x) {
            const auto &tile = _map->getTile(x, y);
            const auto &resources = tile.getResources();
            Vector3 basePos = _floor->get3DCoords(x, y);
            int typeIndex = 0;

            for (size_t i = 0; i < zappy::game::RESOURCE_QUANTITY; ++i) {
                size_t quantity = resources[i];
                if (quantity == 0 || !_resourceModels[i])
                    continue;

                for (size_t q = 0; q < quantity; ++q) {
                    Vector3 pos = {
                        basePos.x + (q % 2) * spacing + (typeIndex % 3) * spacing,
                        uniformHeight,
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

void zappy::gui::raylib::MapRenderer::renderIncantations()
{
    for (const auto& incantation : _incantations)
        incantation->render(_floor.get());
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

void zappy::gui::raylib::MapRenderer::addResourceModel(const zappy::game::Resource &type, std::unique_ptr<AResourceModel> model)
{
    if (model)
        model->init();
    _resourceModels[static_cast<size_t>(type)] = std::move(model);
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

    for (auto &t : _translations) {
        if (t.id == player.getId()) {
            t = translation;
            player.setGamePosition(Vector2{ static_cast<float>(x), static_cast<float>(y) });
            return;
        }
    }

    _translations.push_back(translation);
    player.setGamePosition(Vector2{ static_cast<float>(x), static_cast<float>(y) });
}

void zappy::gui::raylib::MapRenderer::playerExpulsion(const int &id, const int &x, const int &y)
{
    if (_players.empty())
        return;

    auto &player = _getPlayer(id);

    Translation translation = _floor->createTranslation(player, x, y, EXPULSION_TIME);

    for (auto &t : _translations) {
        if (t.id == id) {
            t = translation;
            player.setGamePosition(Vector2{ static_cast<float>(x), static_cast<float>(y) });
            return;
        }
    }

    _translations.push_back(translation);
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

void zappy::gui::raylib::MapRenderer::_updateTranslations(const float &deltaUnits)
{
    auto it = _translations.begin();
    while (it != _translations.end()) {
        auto &T = *it;
        auto &player = _getPlayer(T.id);

        if (T.elapsedTime + deltaUnits >= T.timeUnits) {
            player.setPosition(T.destination);
            it = _translations.erase(it);
        } else {
            _floor->translate(deltaUnits, T.translationVector, T.destination, player);
            T.elapsedTime += deltaUnits;
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

void zappy::gui::raylib::MapRenderer::setIncantationTile(const int &x, const int &y)
{
    for (const auto& inc : _incantations) {
        if (inc->isAt(x, y))
            return;
    }

    _incantations.push_back(std::make_unique<Incantation>(Vector2{static_cast<float>(x), static_cast<float>(y)}));
}

void zappy::gui::raylib::MapRenderer::clearIncantationTile(const int &x, const int &y)
{
    _incantations.erase(
        std::remove_if(_incantations.begin(), _incantations.end(),
            [x, y](const std::unique_ptr<Incantation>& inc) {
                return inc->isAt(x, y);
            }),
        _incantations.end()
    );
}

void zappy::gui::raylib::MapRenderer::_updateIncantationAnimation(float deltaTime)
{
    for (auto& incantation : _incantations)
        incantation->update(deltaTime);
}
