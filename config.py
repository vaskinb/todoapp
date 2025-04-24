#!/usr/bin/env python
# coding: utf-8
import configparser

# -----------------------------------------------------------------------------
# --- Flask ---
# -----------------------------------------------------------------------------
from flask import Flask


class ConfigPath:
    development = "conf/development.conf"
    production = "conf/production.conf"
    pytest = "conf/pytests.conf"
    docker = "conf/docker.conf"


class Config:
    def __init__(self, app: Flask, config_path: str, section: str = "config"):
        self.app = app

        # ---------------------------------------------------------------------
        # --- Read params from config file ---
        # ---------------------------------------------------------------------
        config = configparser.ConfigParser()
        config.read(config_path)
        for key, value in config[section].items():
            if value in ['True', 'False']:
                # -------------------------------------------------------------
                # --- Read boolean values ---
                # -------------------------------------------------------------
                self.app.config[key.upper()] = config[section].getboolean(key)
            else:
                self.app.config[key.upper()] = value
