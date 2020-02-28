from .UdonPie import *  # IGNORE_LINE


def _start():
    red_color = Color.ctor(1.0, 0.0, 0.0)


def _onMouseDown():
    this_renda = Renderer(this_gameObj.GetComponent('Renderer'))
    this_renda.get_material().set_color(red_color)
