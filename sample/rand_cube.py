from .UdonPie import *  # IGNORE_LINE


# Place randomly colored blocks in the scene
# Demo Video https://twitter.com/zz_roba/status/1213365214135013376
# Start Event
def _start():
    # Cube to duplicate
    cube = GameObject.Find('Cube')
    # An array is realized by the method of the {TypeName} Array class. (Not implemented at language level)
    # Make 10x10 size GameObjectArray Object
    cubes = GameObjectArray.ctor(10 * 10)
    y_i = 0
    while y_i < 10:
        x_i = 0
        while x_i < 10:
            # duplicate
            cube_obj = instantiate(cube)
            # setting
            cube_insta = Transform(cube_obj.GetComponent('Transform'))
            # Cannot do implicit cast
            tmp_x = Convert.ToSingle(x_i)
            tmp_y = Convert.ToSingle(y_i)
            cube_insta.set_position(
                Vector3.ctor(tmp_x, 0.0, tmp_y)
            )
            cubes[10 * y_i + x_i] = cube_obj
            x_i = x_i + 1
        y_i = y_i + 1


# MouseDown　Event
def _onMouseDown():
    cube_i = 0
    while cube_i < 10 * 10:
        # Color change randomly
        cube_renda = Renderer(cubes[cube_i].GetComponent('Renderer'))
        cube_renda.get_material().set_color(Random.ColorHSV())
        cube_i = cube_i + 1
