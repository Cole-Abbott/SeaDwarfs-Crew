import json, sys, copy, requests
import pysvg.structure
import pysvg.builders
from math import cos, sin, pi
from random import randint, choice, uniform

WIDTH, HEIGHT = 1000, 1000

def main(total):
  with open('options.json', 'r') as file:
    options = json.load(file)
  for count in range(total):
    shape = {
    'sides' : choice(options['sides']),
    'zoom' : randint(150, 500),
    'colors' : choice(options['colors']),
    'background' : choice(options['background']),
    'pattern' : choice(options['pattern']),
    'angle' : uniform(0, 6.28),
    'x' : randint(0, 500),
    'y' : randint(0, 500),
    'radius' : None,
    'color' : None,
    'strokewidth' : 1,
    }

    image = drawing(shape, count)
    image.drawFull()
    image.save()
    del image

class drawing:
  def __init__(self, shape, count):
    #initalises stuff, creates svg document, sets lambdas for rotation, fills background
    self.shape = shape
    self.count = count
    self.svg_document = pysvg.structure.Svg(width=WIDTH, height=HEIGHT)
    self.shape_builder = pysvg.builders.ShapeBuilder()

    for key in shape:
      setattr(self, key, shape[key])

    if self.sides == 3:
      self.setAngle = lambda a: a +  0.046778
      self.setRadius = lambda a: a * 0.92601
      self.setStrokewidth = lambda a: a * 0.97

    if self.sides == 6:
      self.setAngle = lambda a: a + 0.053517
      self.setRadius = lambda a: a * 0.97139
      self.setStrokewidth = lambda a: a * 0.98

    if self.sides == 4:
      self.setAngle = lambda a: a + 0.030918
      self.setRadius = lambda a: a * 0.97046
      self.setStrokewidth = lambda a: a * 0.98

    self.svg_document.addElement(self.shape_builder.createRect(0, 0, WIDTH, HEIGHT, fill=self.background))

  def drawFull(self):
    ##initalises grid for squares
    if self.sides == 4:
      points = [] #list of tuples containing xy cords and color
      a = self.angle
      for column in range(-3 * int(WIDTH / self.zoom) - 1, 2 * int(WIDTH / self.zoom) + 1):
        for row in range(-3 * int(HEIGHT / self.zoom) - 1, 2 * int(HEIGHT / self.zoom) + 1):
          x = column * self.zoom
          y = row * self.zoom
          points.append((
            x*cos(self.angle) - y*sin(self.angle) + self.x,
            x*sin(self.angle) + y*cos(self.angle) + self.y,
            self.colors[int(  self.pattern [row % len(self.pattern)] [column % len(self.pattern[row % len(self.pattern)])] )],
            self.angle + pi/4
            ))

      #sets radius and rotates shapes
      self.radius = self.zoom * .55

    #initalises grid for hexagons
    if self.sides == 6:
      points = [] #list of tuples containing xy cords and color
      for column in range(-3 * int(WIDTH / self.zoom) - 1, 3 * int(WIDTH / self.zoom) + 1):
        for row in range(-3 * int(HEIGHT / self.zoom) - 1, 3 * int(HEIGHT / self.zoom) + 1):
          if row % 2 == 0:
            x = column * self.zoom * 1.5
          else:
            x = column * self.zoom * 1.5 + (self.zoom * .75)
          y = row * self.zoom * 0.866 / 2
          points.append((
            x*cos(self.angle) - y*sin(self.angle) + self.x,
            x*sin(self.angle) + y*cos(self.angle) + self.y,
            self.colors[int(  self.pattern [row % len(self.pattern)] [column % len(self.pattern[row % len(self.pattern)])] )],
            self.angle
            ))
      #sets raduis
      self.radius = self.zoom * .42

    if self.sides == 3:
      points = [] #list of tuples containing xy cords and color
      for column in range(-3 * int(WIDTH / self.zoom) - 1, 3 * int(WIDTH / self.zoom)):
        for row in range(-3 * int(HEIGHT / self.zoom) - 1, 3 * int(HEIGHT / self.zoom)):
          if column % 2 == 0:
            y = row * self.zoom * 1.8
            a = self.angle + pi/2
          else:
            y = row * self.zoom * 1.8 + (0.5 * self.zoom)
            a = self.angle + 3 * pi / 2
          if row % 2 == 0:
            x = column * self.zoom * 1.2
          else:
            x = column * self.zoom * 1.2 + (self.zoom * 1.2)
          points.append((
            x*cos(self.angle) - y*sin(self.angle) + self.x,
            x*sin(self.angle) + y*cos(self.angle) + self.y,
            self.colors[int(  self.pattern [row % len(self.pattern)] [column % len(self.pattern[row % len(self.pattern)])] )],
            a
            ))
      #sets raduis
      self.radius = self.zoom

    #draw section if on screen
    for point in points:
      if -self.radius < point[0] < WIDTH + self.radius:
        if -self.radius < point[1] < HEIGHT + self.radius:
          self.x, self.y, self.color, self.angle = point
          self.drawSection()

  def drawSection(self):
    #draws muitiple shapes rotated within each other
    for key in self.shape: #saves inital attrs b/c they will be changed and need to be reset to inital values
      self.shape[key] = getattr(self, key)
    for i in range(150): #each loop draws a slightly smaller shape rotated acordingly
        self.drawShape('none')
        self.angle = self.setAngle(self.angle)
        self.radius = self.setRadius(self.radius)
        self.strokewidth = self.setStrokewidth(self.strokewidth)
    self.drawShape(self.color)
    for key in self.shape: #resets attrs
      setattr(self, key, self.shape[key])

  def drawShape(self, fill):
    #draws a regular polygon centered at self.x, self.y
    a = self.angle
    l = self.radius
    x, y, n = (self.x, self.y, self.sides)
    points = ''
    for i in range(n):
        points = f"{points}{cos(a) * l + x},{sin(a) * l + y} "
        a += 2 * pi / n
    self.svg_document.addElement(self.shape_builder.createPolygon(points, strokewidth=self.strokewidth, stroke=self.color, fill=fill))

  def save(self):
    self.svg_document.save(f"images/img#{self.count}.svg")
    with open(f"metadata/{self.count}.json", "w") as file:
      json.dump(self.metadata(), file)

  def metadata(self):
    shapes = ['', '', '', 'Triangles', 'Squares', '', 'Hexagons']
    descriptions = [
      'Try selling THAT to your grandma!',
      'This is the day you will always remember as the day you almost caught Captain Jack Sparrow.',
      "Not all treasure's silver and gold, mate.",
      "Two fish are in a tank. One says, ‘How do you drive this thing?’",
      'Communist jokes aren’t funny unless everyone gets them.'
      ]
    data = {
      "Shape" : shapes[self.sides],
      "Colors" : f'{getColor(self.colors[0])} and {getColor(self.colors[1])}',
      "Background color" : getColor(self.background),
      "description" : choice(descriptions)
    }
    return(data)

def getColor(color):
  color = color.replace("#", '')
  url = f"https://www.thecolorapi.com/id?hex={color}"
  response = requests.request("GET", url, headers={}, data={})
  name = json.loads(response.text)
  return(name["name"]["value"])

if __name__ == '__main__':
  main(int(sys.argv[1]))
