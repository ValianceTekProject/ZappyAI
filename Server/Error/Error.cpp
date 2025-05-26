/*
** EPITECH PROJECT, 2025
** B-NWP-400-BDX-4-1-jetpack-baptiste.blambert
** File description:
** Error
*/

#include "Error.hpp"

// Fonction d'erreur, retour message
char const *ZappyServer::error::Error::getMessage() const
{
    return this->_errorMsg.c_str();
}

// Retourne le contexte de l'erreur
const char *ZappyServer::error::Error::what() const throw()
{
    return getMessage();
}
