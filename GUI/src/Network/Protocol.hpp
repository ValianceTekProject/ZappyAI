/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Protocol.hpp
*/

#pragma once

#include "NetworkManager.hpp"
#include "GameState.hpp"

#include <memory>
#include <sstream>
#include <chrono>
#include <thread>

namespace zappy {
    namespace network {
        class Protocol {
            public:
                explicit Protocol(std::shared_ptr<game::GameState> gameState);
                ~Protocol();

                bool connectToServer(const std::string& host, int port);
                void disconnect();
                bool isConnected() const;
                void update(); // À appeler dans la boucle principale

                void requestMapSize();
                void requestTileContent(int x, int y);
                void requestMapContent();
                void requestTeamNames();
                void requestPlayerPosition(int playerId);
                void requestPlayerLevel(int playerId);
                void requestPlayerInventory(int playerId);
                void requestTimeUnit();
                void setTimeUnit(int timeUnit);

            private:
                std::unique_ptr<NetworkManager> _network;
                std::shared_ptr<game::GameState> _gameState;
                bool _authenticated;

                // Message handlers
                void handleMapSize(const std::vector<std::string>& params);
                void handleTileContent(const std::vector<std::string>& params);
                void handleMapContent(const std::vector<std::string>& params);
                void handleTeamNames(const std::vector<std::string>& params);
                void handleNewPlayer(const std::vector<std::string>& params);
                void handlePlayerPosition(const std::vector<std::string>& params);
                void handlePlayerLevel(const std::vector<std::string>& params);
                void handlePlayerInventory(const std::vector<std::string>& params);
                void handlePlayerExpulsion(const std::vector<std::string>& params);
                void handlePlayerBroadcast(const std::vector<std::string>& params);
                void handleIncantationStart(const std::vector<std::string>& params);
                void handleIncantationEnd(const std::vector<std::string>& params);
                void handleEggLaying(const std::vector<std::string>& params);
                void handleResourceDrop(const std::vector<std::string>& params);
                void handleResourceCollect(const std::vector<std::string>& params);
                void handlePlayerDeath(const std::vector<std::string>& params);
                void handleEggCreated(const std::vector<std::string>& params);
                void handleEggHatch(const std::vector<std::string>& params);
                void handleEggDeath(const std::vector<std::string>& params);
                void handleTimeUnit(const std::vector<std::string>& params);
                void handleGameEnd(const std::vector<std::string>& params);
                void handleServerMessage(const std::vector<std::string>& params);
        };
    } // namespace network
} // namespace zappy
