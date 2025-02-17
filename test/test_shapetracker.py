#!/usr/bin/env python
import unittest
import numpy as np
from tinygrad.helpers import prod
from tinygrad.shapetracker import ShapeTracker

class DumbShapeTracker:
  def __init__(self, *shape):
    self.t = np.arange(prod(shape), dtype=np.uint8).reshape(shape)

  @property
  def shape(self):
    return self.t.shape

  def reshape(self, *new_shape):
    self.t = self.t.reshape(new_shape)

  def permute(self, *axis):
    self.t = np.transpose(self.t, axis)

  def expand(self, *new_shape):
    self.t = np.broadcast_to(self.t, new_shape)

  def flip(self, *axis):
    self.t = np.flip(self.t, axis)

  def slice(self, *arg):
    self.t = self.t[tuple([slice(x[0], x[1]) for x in arg])]

  def stride(self, *arg):
    self.t = self.t[tuple([slice(None, None, x) for x in arg])]

  def __getitem__(self, val):
    return self.t.flatten()[val]

# Tensor.zeros(2, 4).permute(1,0).reshape(2, 4)
# (d1*4 + d0%4), d1=x//4, d0=x%4 = ((x//4)*4) + (x%4)%4

class TestShapeTracker(unittest.TestCase):
  def setUp(self):
    self.st = ShapeTracker(2,4)
    self.dt = DumbShapeTracker(2,4)
    self.apply = lambda fxn: [fxn(x) for x in [self.st, self.dt]]

  def tearDown(self):
    x = [self.st[i] for i in range(prod(self.st.shape))]
    y = [self.dt[i] for i in range(prod(self.dt.shape))]
    print(x,y, self.st.shape, self.dt.shape, self.st.expr())
    assert self.st.shape == self.dt.shape
    assert x == y

  def test_noop(self):
    pass

  def test_simple_split(self):
    self.test_permute()
    self.apply(lambda x: x.reshape(8))

  def test_reshape(self):
    assert self.st.shape == self.dt.shape
    new_shape = self.st.shape[::-1]
    self.apply(lambda x: x.reshape(*new_shape))

  def test_permute(self):
    assert self.st.shape == self.dt.shape
    if len(self.st.shape) == 2: self.apply(lambda x: x.permute(1,0))
    elif len(self.st.shape) == 3: self.apply(lambda x: x.permute(2,0,1))

  def test_reshape_with_1(self):
    assert self.st.shape == self.dt.shape
    new_shape = [self.st.shape[0], 1, self.st.shape[1]]
    self.apply(lambda x: x.reshape(*new_shape))

  def test_expand(self):
    self.test_reshape_with_1()
    new_shape = list(self.st.shape)
    new_shape[1] = 2
    self.apply(lambda x: x.expand(*new_shape))

  def test_flip_0(self):
    self.apply(lambda x: x.flip(0))

  def test_flip_1(self):
    self.apply(lambda x: x.flip(1))

  def test_flip_01(self):
    self.apply(lambda x: x.flip(0,1))

  def test_slice_0(self):
    self.apply(lambda x: x.slice((1, x.shape[0]), (0, x.shape[1])))

  def test_slice_1(self):
    self.apply(lambda x: x.slice((0, x.shape[0]), (1, x.shape[1])))

  def test_slice_1c1(self):
    self.apply(lambda x: x.slice((0, 1), (0, 1)))

  def test_slice_1c2(self):
    self.apply(lambda x: x.slice((1, 2), (1, 2)))

  def test_stride(self): self.apply(lambda x: x.stride(2,1))
  def test_stride_int(self): self.apply(lambda x: x.stride(1,2))
  def test_stride_2(self): self.apply(lambda x: x.stride(2,2))
  def test_stride_n(self): self.apply(lambda x: x.stride(-2,1))
  def test_stride_int_n(self): self.apply(lambda x: x.stride(-1,2))
  def test_stride_2_n(self): self.apply(lambda x: x.stride(-2,-2))

  def test_reshape_then_permute(self):
    self.test_reshape()
    self.test_permute()

  def test_reshape_then_expand(self):
    self.test_reshape()
    self.test_expand()

  def test_permute_then_reshape(self):
    self.test_permute()
    self.test_reshape()

  def test_expand_then_reshape(self):
    self.test_expand()
    self.test_reshape()

  def test_combo(self):
    self.test_permute()
    self.test_reshape()
    self.test_slice_1()
    self.test_expand()
    self.test_permute()

if __name__ == '__main__':
  unittest.main()
