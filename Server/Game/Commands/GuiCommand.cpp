/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** GuiCommand
*/

#include "GuiCommand.hpp"

void zappy::game::CommandHandlerGui::handleMsz(zappy::game::ServerPlayer &player)
{
    std::string msg = "msz " + std::to_string(this->_widthMap) + " " + std::to_string(this->_heightMap) + "\n";
    player.getClient().sendMessage(msg);
}

void zappy::game::CommandHandlerGui::handleBct(zappy::game::ServerPlayer &player, const std::string &arg)
{
    std::istringstream iss(arg);
    int x;
    int y;
    std::string leftover;
    std::string msg = "bct ";


    if (iss >> x >> y && !(iss >> leftover) && (x <= this->_widthMap && x >= 0) && (y <= this->_heightMap && y >= 0)) {
        msg += std::to_string(x) + " " + std::to_string(y);
        for (auto resource :this->_map.getTile(x, y).getResources())
            msg += " " + std::to_string(resource);
        msg += "\n";
        player.getClient().sendMessage(msg);
    } else
        player.getClient().sendMessage("ko\n");
}

void zappy::game::CommandHandlerGui::handleMct(zappy::game::ServerPlayer &player)
{
    for (int x = 0; x < this->_widthMap; x += 1) {
        for (int y = 0; y < this->_heightMap; y += 1)
            this->handleBct(player, std::string(std::to_string(x) + " " + std::to_string(y)));
    } 
}

void zappy::game::CommandHandlerGui::handleTna(zappy::game::ServerPlayer &player)
{
    for (auto &team : this->_teamList)
        player.getClient().sendMessage(std::string("tna " + team->getName() + "\n"));
}

void zappy::game::CommandHandlerGui::handlePpo(zappy::game::ServerPlayer &player, const std::string &arg)
{
    std::stringstream stream;
    int playerId;
    std::string msg = "ppo ";

    stream << arg;
    stream >> playerId;

    for (auto &team : this->_teamList) {
        for (auto &p : team->getPlayerList()) {
            if (p->getId() == playerId) {
                std::ostringstream orientationStream;
                orientationStream << p->orientation;
                std::string msg = std::to_string(playerId) + " " + 
                                  std::to_string(p->x) + " " + 
                                  std::to_string(p->y) + " " + 
                                  orientationStream.str() + "\n";

                player.getClient().sendMessage(msg);
                return;
            }
        }
    }
    player.getClient().sendMessage("ko\n");
}

void zappy::game::CommandHandlerGui::handlePlv(zappy::game::ServerPlayer &player, const std::string &arg)
{
    std::stringstream stream;
    int playerId;
    std::string msg = "plv ";

    stream << arg;
    stream >> playerId;

    for (auto &team : this->_teamList) {
        for (auto &p : team->getPlayerList()) {
            if (p->getId() == playerId) {
                msg += std::to_string(playerId) + " " + std::to_string(p->level) + "\n";
                player.getClient().sendMessage(msg);
                return;
            }
        }
    }
    player.getClient().sendMessage("ko\n");
}

void zappy::game::CommandHandlerGui::handlePin(zappy::game::ServerPlayer &player, const std::string &arg)
{
    std::stringstream stream;
    int playerId;
    std::string msg = "pin ";

    stream << arg;
    stream >> playerId;

    for (auto &team : this->_teamList) {
        for (auto &p : team->getPlayerList()) {
            if (p->getId() == playerId) {
                msg += std::to_string(playerId) + " " + std::to_string(p->x) + " " + std::to_string(p->y) + " ";
                zappy::game::Inventory playerInv = p->getInventory();
                for (auto foodName : names)
                    msg += std::to_string(playerInv.getResourceQuantity(getResource(foodName))) + " ";
                msg.pop_back();
                msg += "\n";
                player.getClient().sendMessage(msg);
                return;
            }
        }
    }
    player.getClient().sendMessage("ko\n");
}

void zappy::game::CommandHandlerGui::handleSgt(zappy::game::ServerPlayer &player)
{
    player.getClient().sendMessage(std::string("sgt ") + std::to_string(this->_freq) + "\n");
}

void zappy::game::CommandHandlerGui::handleSst(zappy::game::ServerPlayer &player, const std::string &arg)
{
    std::stringstream stream;
    int freq;
    std::string msg = "sst ";

    stream << arg;
    stream >> freq;

    this->_freq = freq;

    player.getClient().sendMessage(std::string("sgt ") + std::to_string(this->_freq) + "\n");
}

void zappy::game::CommandHandlerGui::initCommandMap()
{
    this->_commandMapGui = {
        {"msz", [this](ServerPlayer &player, const std::string &) { handleMsz(player); }},
        {"bct", [this](ServerPlayer &player, const std::string &arg) { handleBct(player, arg); }},
        {"mct", [this](ServerPlayer &player, const std::string &) { handleMct(player); }},
        {"tna", [this](ServerPlayer &player, const std::string &) { handleTna(player); }},
        {"ppo", [this](ServerPlayer &player, const std::string &arg) { handlePpo(player, arg); }},
        {"plv", [this](ServerPlayer &player, const std::string &arg) { handlePlv(player, arg); }},
        {"pin", [this](ServerPlayer &player, const std::string &arg) { handlePin(player, arg); }},
        {"sgt", [this](ServerPlayer &player, const std::string &) { handleSgt(player); }},
        {"sst", [this](ServerPlayer &player, const std::string &arg) { handleSst(player, arg); }}
    };
}

void zappy::game::CommandHandlerGui::processClientInput(const std::string &input, zappy::game::ServerPlayer &player)
{
    if (this->_commandMapGui.empty())
        this->initCommandMap();

    auto spacePos = input.find(' ');
    std::string cmd = input.substr(0, spacePos);
    std::string args = (spacePos != std::string::npos) ? input.substr(spacePos + 1) : "";

    if (!args.empty() && args.back() == '\n')
        args.pop_back();


    auto it = this->_commandMapGui.find(cmd);
    if (it != this->_commandMapGui.end()) {
        it->second(player, args);
    } else
        player.getClient().sendMessage("suc\n");
}