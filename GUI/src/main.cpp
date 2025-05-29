/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** main
*/

#include "Gui.hpp"

int main(int argc, char const *argv[])
{
    try {
        zappy::gui::Gui gui;
        gui.parseArgs(argc, argv);
        gui.run();
    }
    catch(const zappy::IError &e) {
        std::cerr << e.where() << " Error: " << e.what() << std::endl;
    }
    return 0;
}
