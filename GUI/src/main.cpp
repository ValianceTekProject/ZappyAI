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
        gui::ZappyGui gui;
        gui.parseArgs(argc, argv);
        gui.run();
    }
    catch(const gui::GUIError& e) {
        std::cerr << e.where() << " Error: " << e.what() << std::endl;
    }
    return 0;
}
