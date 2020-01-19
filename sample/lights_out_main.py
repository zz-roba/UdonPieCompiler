def init_vars()->SystemVoid:
  n_w = 5
  n_h = 5
  n_level = 4
  red_color = UnityEngineColor.ctor(1.0, 0.0, 0.0)
  white_color = UnityEngineColor.ctor(1.0, 1.0, 1.0)
  black_color = UnityEngineColor.ctor(0.5, 0.0, 0.5)
  button = UnityEngineGameObject.Find('button')
  buttons = UnityEngineGameObjectArray.ctor(n_w * n_h)
  flip_flags = SystemBooleanArray.ctor(n_w * n_h)
  return

def flip(arg_x:SystemInt32, arg_y:SystemInt32)->SystemVoid:
  if (0 <= arg_x and arg_x < n_w) and (0 <= arg_y and arg_y < n_h):
    button_id = n_w * arg_y + arg_x
    if flip_flags.Get(button_id):
      flip_flags.Set(button_id, False)
    else:
      flip_flags.Set(button_id, True)
  return

def _start():
  init_vars()
  y_i = 0
  while y_i < n_h:
    x_i = 0
    while x_i < n_w:
      button_obj = instantiate(button)
      button_insta = UnityEngineTransform(button_obj.GetComponent('Transform'))
      tmp_x = SystemConvert.ToSingle(x_i)
      tmp_y = SystemConvert.ToSingle(y_i)
      button_insta.set_position(
        UnityEngineVector3.ctor(tmp_x, 0.0, tmp_y)
      )
      button_id = n_w * y_i + x_i
      buttons.Set(button_id, button_obj)
      x_i = x_i + 1
    y_i = y_i + 1 

def _onMouseDown():
  flip_flags = SystemBooleanArray.ctor(n_w * n_h)
  tmp_count = 0
  while tmp_count < n_level:
    flip_rand_x = UnityEngineRandom.Range(0, n_w)
    flip_rand_y = UnityEngineRandom.Range(0, n_h)
    flip(flip_rand_x, flip_rand_y)
    flip(flip_rand_x + 1, flip_rand_y)
    flip(flip_rand_x - 1, flip_rand_y)
    flip(flip_rand_x, flip_rand_y + 1)
    flip(flip_rand_x, flip_rand_y - 1)
    tmp_count = tmp_count + 1

def _update():
  y_i = 0
  while y_i < n_h:
    x_i = 0
    while x_i < n_w:
      button_id = n_h * y_i + x_i
      button_obj = buttons.Get(button_id)
      flip_flag = flip_flags.Get(button_id)
      button_renda = UnityEngineRenderer(button_obj.GetComponent('Renderer'))
      if button_renda.get_material().get_color().Equals(red_color):
        flip(x_i, y_i)
        flip(x_i + 1, y_i)
        flip(x_i - 1, y_i)
        flip(x_i, y_i + 1)
        flip(x_i, y_i - 1)
      if flip_flag:
        button_renda.get_material().set_color(white_color)
      else:
        button_renda.get_material().set_color(black_color)
      x_i = x_i + 1
    y_i = y_i + 1 
