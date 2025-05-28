/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** main
*/

#include "GUI.hpp"

int main(int argc, char const *argv[])
{
    try {
        zappy::gui::GUI gui;
        gui.parseArgs(argc, argv);
        gui.run();
    }
    catch(const zappy::gui::IError& e) {
        std::cerr << e.where() << " Error: " << e.what() << std::endl;
    }
    return 0;
}
