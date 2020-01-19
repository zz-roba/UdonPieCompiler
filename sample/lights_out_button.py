def _start():
  red_color = UnityEngineColor.ctor(1.0, 0.0, 0.0)

def _onMouseDown():
  this_renda = UnityEngineRenderer(this_gameObj.GetComponent('Renderer'))
  this_renda.get_material().set_color(red_color)
