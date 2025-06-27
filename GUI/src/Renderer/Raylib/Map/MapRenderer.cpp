/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** MapRenderer.cpp
*/

#include "MapRenderer.hpp"
#include "PlayerActions/PlayerIncantation.hpp"
#include <memory>
#include <raylib.h>

zappy::gui::raylib::MapRenderer::MapRenderer(const std::shared_ptr<game::Map> map) :
    _map(map),
    _floor(nullptr),
    _broadcastType(EffectType::WAVE_BROADCAST),
    _broadcastColor(BLUE),
    _incantationType(EffectType::SPIRAL_INCANTATION),
    _incantationColor(BLUE),
    _eggs(),
    _players()
{}

void zappy::gui::raylib::MapRenderer::init()
{
    // Init la carte
    this->_floor = std::make_shared<FlatFloor>(_map->getWidth(), _map->getHeight(), 1);
    this->_floor->init();

    this->_lastTime = std::chrono::steady_clock::now();
}

void zappy::gui::raylib::MapRenderer::update(const int &frequency)
{
    // Mettre à jour la carte
    this->_floor->update();

    // Mettre à jour les players
    if (!this->_players.empty()) {
        for (auto &player : this->_players)
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

    _updateActions(deltaUnits);
}

void zappy::gui::raylib::MapRenderer::render()
{
    // Dessiner la carte
    this->_floor->render();

    _renderPlayersAndEggs();

    _renderResources();

    _renderAnimActions();
}

void zappy::gui::raylib::MapRenderer::setBroadcastType(const zappy::gui::raylib::EffectType &type)
{
    this->_broadcastType = type;
}

void zappy::gui::raylib::MapRenderer::setIncantationType(const zappy::gui::raylib::EffectType &type)
{
    this->_incantationType = type;
}

void zappy::gui::raylib::MapRenderer::setIncantationColor(const Color &color)
{
    this->_incantationColor = color;
}

void zappy::gui::raylib::MapRenderer::addEgg(std::unique_ptr<AEggModel> egg)
{
    egg->init();

    _eggs.push_back(std::move(egg));
}

void zappy::gui::raylib::MapRenderer::addPlayer(std::unique_ptr<APlayerModel> player)
{
    player->init();

    this->_players.push_back(std::move(player));
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
    Vector3 position3D = this->_floor->get3DCoords(x, y);

    egg.setPosition(position3D);
}

void zappy::gui::raylib::MapRenderer::setPlayerPosition(const int &id, const int &x, const int &y, const game::Orientation &orientation)
{

    if (this->_players.empty())
        return;

    auto &player = this->_getPlayer(id);
    Vector3 postion3D = this->_floor->get3DCoords(x, y);

    player.setPosition(postion3D);

    player.setGamePosition(Vector2{
        static_cast<float>(x),
        static_cast<float>(y)
    });
    player.look(orientation);
}

void zappy::gui::raylib::MapRenderer::playerLook(const int &id, const game::Orientation &orientation)
{
    if (this->_players.empty())
        return;

    auto &player = this->_getPlayer(id);

    player.look(orientation);
}

void zappy::gui::raylib::MapRenderer::playerLookLeft(const int &id)
{
    if (this->_players.empty())
        return;

    auto &player = _getPlayer(id);
    player.lookLeft();

    constexpr float rotationAngle = 90.0f;

    _addRotation(player, rotationAngle);
}

void zappy::gui::raylib::MapRenderer::playerLookRight(const int &id)
{
    if (this->_players.empty())
        return;

    auto &player = _getPlayer(id);
    player.lookRight();

    constexpr float rotationAngle = -90.0f;

    _addRotation(player, rotationAngle);
}

void zappy::gui::raylib::MapRenderer::playerForward(const int &id, const int &x, const int &y)
{
    if (this->_players.empty())
        return;

    APlayerModel &player = _getPlayer(id);
    Translation translation = this->_floor->createTranslation(player, x, y, FORWARD_TIME);

    std::shared_ptr<IPlayerAction> action = PlayerActionFactory::createTranslation(
        id,
        translation,
        this->_floor,
        FORWARD_TIME
    );

    this->_playerActionQueues[id].push(std::move(action));

    player.setGamePosition(Vector2{ static_cast<float>(x), static_cast<float>(y) });
}

void zappy::gui::raylib::MapRenderer::playerExpulsion(const int &id, const int &x, const int &y)
{
    if (this->_players.empty())
        return;

    APlayerModel &player = _getPlayer(id);
    Translation translation = this->_floor->createTranslation(player, x, y, EXPULSION_TIME);

    std::shared_ptr<IPlayerAction> action = PlayerActionFactory::createTranslation(
        id,
        translation,
        this->_floor,
        EXPULSION_TIME
    );

    this->_playerActionQueues[id].push(std::move(action));

    player.setGamePosition(Vector2{ static_cast<float>(x), static_cast<float>(y) });
}

void zappy::gui::raylib::MapRenderer::playerBroadcast(const int &id)
{
    std::shared_ptr<IPlayerAction> action = PlayerActionFactory::createBroadcast(
        id,
        this->_broadcastType,
        this->_broadcastColor,
        BROADCAST_TIME
    );

    this->_playerActionQueues[id].push(action);
    this->_playerAnimAction.push_back(std::move(std::dynamic_pointer_cast<APlayerAnimAction>(action)));
}

void zappy::gui::raylib::MapRenderer::startIncantation(const int &x, const int &y, const std::vector<int> &playerIds)
{
    Vector2 incantationPos = Vector2{static_cast<float>(x), static_cast<float>(y)};

    std::shared_ptr<IPlayerAction> action = PlayerActionFactory::createIncantation(
        playerIds[0],
        this->_incantationType,
        this->_incantationColor,
        incantationPos,
        INCANTATION_TIME
    );

    for (auto id : playerIds)
        this->_playerActionQueues[id].push(action);

    this->_playerAnimAction.push_back(std::move(std::dynamic_pointer_cast<APlayerAnimAction>(action)));

    APlayerAnimAction &animAction = static_cast<APlayerAnimAction &>(*action);
    this->_incantationMap[animAction.getAnimationId()] = incantationPos;
}

void zappy::gui::raylib::MapRenderer::endIncantation(const int &x, const int &y, const bool &result)
{
    Vector2 targetPos = Vector2{static_cast<float>(x), static_cast<float>(y)};
    ssize_t animationIdToRemove = -1;
    (void)result;

    for (const auto &[animationId, pos] : _incantationMap) {
        if (pos.x == targetPos.x && pos.y == targetPos.y) {
            animationIdToRemove = animationId;
            break;
        }
    }

    if (animationIdToRemove == -1)
        return;

    std::shared_ptr<PlayerIncantation> incantation = nullptr;

    for (auto &action : _playerAnimAction) {
        if (action && action->getAnimationId() == animationIdToRemove) {
            // Recup shared ptr de playerIncantation
            incantation = std::dynamic_pointer_cast<PlayerIncantation>(action);
            break;
        }
    }

    // Supprimer l'action de la queue des joueurs
    int playerId = incantation->getPlayerId();

    for (auto &[id, queue] : _playerActionQueues)
        if (!queue.empty() && queue.front()->getPlayerId() == playerId &&
        queue.front()->getActionType() == ActionType::INCANTATION)
            queue.pop();

    // Appeller IncantationResult();
    incantation->incantationResult(result);

    _incantationMap.erase(animationIdToRemove);

    if (!incantation->hasActionStarted())
        incantation->startAction();
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
    for (auto it = this->_players.begin(); it != this->_players.end(); it++) {
        if ((*it)->getId() == id) {
            this->_players.erase(it);
            break;
        }
    }
}

zappy::gui::raylib::APlayerModel &zappy::gui::raylib::MapRenderer::_getPlayer(const int &id)
{
    for (auto &player : this->_players) {
        if (player->getId() == id)
            return *player;
    }
    throw RendererError("Player " + std::to_string(id) + " not found", "MapRenderer");
}

const zappy::gui::raylib::APlayerModel &zappy::gui::raylib::MapRenderer::_getPlayer(const int &id) const
{
    for (const auto &player : this->_players) {
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
        destination,
        perStep
    };

    auto action = PlayerActionFactory::createRotation(
        player.getId(),
        rotation,
        ROTATION_TIME
    );

    this->_playerActionQueues[player.getId()].push(std::move(action));
}

void zappy::gui::raylib::MapRenderer::_updateActions(const float &deltaUnits)
{
    for (auto it = this->_playerActionQueues.begin(); it != this->_playerActionQueues.end(); ) {
        auto &queue = it->second;
        if (queue.empty()) {
            it = this->_playerActionQueues.erase(it);
            continue;
        }

        auto &action = queue.front();
        APlayerModel &player = _getPlayer(action->getPlayerId());

        if (!action->hasActionStarted())
            action->startAction();

        if (action->ActionWillEnd(deltaUnits)) {
            action->finishAction(deltaUnits, player);
            queue.pop();
        } else
            action->update(deltaUnits, player);
        ++it;
    }

    this->_updateAnimActions(deltaUnits);
}

void zappy::gui::raylib::MapRenderer::_updateAnimActions(const float &deltaUnits)
{
    for (auto it = this->_playerAnimAction.begin(); it != this->_playerAnimAction.end(); ++it) {
        if (it->use_count() > 1)
            continue;

        auto action = (*it);
        APlayerModel &player = _getPlayer(action->getPlayerId());

        action->update(deltaUnits, player);
    }
}

void zappy::gui::raylib::MapRenderer::_renderPlayersAndEggs()
{
    for (auto &player : this->_players)
        player->render();

    for (auto &egg : _eggs)
        egg->render();
}

void zappy::gui::raylib::MapRenderer::_renderResources()
{
    constexpr float uniformHeight = 0.1f;
    float spacing = 0.2f;

    for (size_t y = 0; y < _map->getHeight(); ++y) {
        for (size_t x = 0; x < _map->getWidth(); ++x) {
            const auto &tile = _map->getTile(x, y);
            const auto &resources = tile.getResources();
            Vector3 basePos = this->_floor->get3DCoords(x, y);
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

void zappy::gui::raylib::MapRenderer::_renderAnimActions()
{
    auto it = _playerAnimAction.begin();
    while (it != _playerAnimAction.end()) {
        const auto &action = *it;
        if (!action || action->hasEffectEnded()) {
            it = _playerAnimAction.erase(it);
            continue;
        }

        if (!action->hasActionStarted()) {
            ++it;
            continue;
        }

        auto &player = _getPlayer(action->getPlayerId());
        action->render(player.getPosition());
        ++it;
    }
}
