/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** AScene.cpp
*/

#include "AScene.hpp"

zappy::gui::raylib::AScene::AScene(const std::shared_ptr<game::GameState> &gameState) :
    _gameState(gameState)
{}

void zappy::gui::raylib::AScene::init()
{
    // Initialiser la scène
}

void zappy::gui::raylib::AScene::update()
{
    // Mettre à jour la logique de la scène
}

void zappy::gui::raylib::AScene::handleInput(InputManager &inputManager)
{
    // Gérer les entrées de l'utilisateur
    (void)inputManager;
}

void zappy::gui::raylib::AScene::addEgg(const int &eggId)
{
    // Ajouter un œuf à la scène
    (void)eggId;
}

void zappy::gui::raylib::AScene::addPlayer(const int &id)
{
    // Ajouter un joueur à la scène
    (void)id;
}

void zappy::gui::raylib::AScene::updatePlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation)
{
    // Mettre à jour la position d'un joueur
    (void)id;
    (void)x;
    (void)y;
    (void)orientation;
}

void zappy::gui::raylib::AScene::updatePlayerLevel(const int &id, const size_t &level)
{
    // Mettre à jour le niveau d'un joueur
    (void)id;
    (void)level;
}

void zappy::gui::raylib::AScene::updatePlayerInventory(const int &id, const game::Inventory &inventory)
{
    // Mettre à jour l'inventaire d'un joueur
    (void)id;
    (void)inventory;
}

void zappy::gui::raylib::AScene::hatchEgg(const int &id)
{
    // Incuber un œuf
    (void)id;
}

void zappy::gui::raylib::AScene::removeEgg(const int &id)
{
    // Supprimer un œuf
    (void)id;
}

void zappy::gui::raylib::AScene::removePlayer(const int &id)
{
    // Supprimer un joueur
    (void)id;
}
