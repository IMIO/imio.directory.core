# -*- coding: utf-8 -*-
import json
import os


def get_json(json_filename):
    with open(
        os.path.join(
            os.path.dirname(__file__),
            json_filename,
        ),
    ) as json_file:
        result = json.load(json_file)
        return result
