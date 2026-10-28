"""
MicroPython max7219 cascadable 8x8 LED matrix driver
https://github.com/mcauser/micropython-max7219

MIT License
Copyright (c) 2017 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Edits to enable rotation of the display and to implement the ability to work
with patterns/matrices made by Nick Goris (2025)

Rotation bug fix made by Claude (Anthropic), 2026:
  show() used to write the rotated image back into the main buffer, so every
  call to show() rotated the picture again. It now renders the rotated image
  into a separate output buffer and leaves the main buffer untouched.
  Also removed the unused/incorrect pixel_rotated() and text_rotated(), and
  90/270 degree rotation is now rejected when more than one matrix is chained
  (the 8 x 8*num image cannot be rotated into the same shape).
"""

__version__ = "1.0.1"  # 1.0.0 = Nick Goris edits, 1.0.1 = rotation bugfix

from micropython import const
import framebuf

_NOOP = const(0)
_DIGIT0 = const(1)
_DECODEMODE = const(9)
_INTENSITY = const(10)
_SCANLIMIT = const(11)
_SHUTDOWN = const(12)
_DISPLAYTEST = const(15)

class Matrix8x8:
    def __init__(self, spi, cs, num):
        """
        Driver for cascading MAX7219 8x8 LED matrices.

        >>> import max7219
        >>> from machine import Pin, SPI
        >>> spi = SPI(1)
        >>> display = max7219.Matrix8x8(spi, Pin('X5'), 4)
        >>> display.text('1234',0,0,1)
        >>> display.show()

        """
        self.spi = spi
        self.cs = cs
        self.cs.init(cs.OUT, True)
        self.buffer = bytearray(8 * num)
        self.num = num
        fb = framebuf.FrameBuffer(self.buffer, 8 * num, 8, framebuf.MONO_HLSB)
        self.framebuf = fb
        # Provide methods for accessing FrameBuffer graphics primitives. This is a workround
        # because inheritance from a native class is currently unsupported.
        # http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
        self.fill = fb.fill  # (col)
        self.pixel = fb.pixel # (x, y[, c])
        self.hline = fb.hline  # (x, y, w, col)
        self.vline = fb.vline  # (x, y, h, col)
        self.line = fb.line  # (x1, y1, x2, y2, col)
        self.rect = fb.rect  # (x, y, w, h, col)
        self.fill_rect = fb.fill_rect  # (x, y, w, h, col)
        self.text = fb.text  # (string, x, y, col=1)
        self.scroll = fb.scroll  # (dx, dy)
        self.blit = fb.blit  # (fbuf, x, y[, key])
        self.rotation = 0  # 0, 90, 180, 270 degrees

        # Separate output buffer used only when rotation is active.
        # The drawing buffer (self.buffer) is never modified by show().
        self._out = bytearray(8 * num)
        self._out_fb = framebuf.FrameBuffer(self._out, 8 * num, 8, framebuf.MONO_HLSB)

        self.init()

    def set_rotation(self, degrees):
        """Set rotation: 0, 90, 180, or 270 degrees"""
        if degrees not in (0, 90, 180, 270):
            raise ValueError("Rotation must be 0, 90, 180, or 270 degrees")
        if degrees in (90, 270) and self.num != 1:
            raise ValueError("90/270 degree rotation only works with a single matrix")
        self.rotation = degrees

    def _transform_coords(self, x, y):
        """Transform coordinates based on rotation"""
        width = 8 * self.num
        height = 8

        if self.rotation == 0:
            return x, y
        elif self.rotation == 90:
            return height - 1 - y, x
        elif self.rotation == 180:
            return width - 1 - x, height - 1 - y
        elif self.rotation == 270:
            return y, width - 1 - x

    def _write(self, command, data):
        self.cs(0)
        for m in range(self.num):
            self.spi.write(bytearray([command, data]))
        self.cs(1)

    def init(self):
        for command, data in (
            (_SHUTDOWN, 0),
            (_DISPLAYTEST, 0),
            (_SCANLIMIT, 7),
            (_DECODEMODE, 0),
            (_SHUTDOWN, 1),
        ):
            self._write(command, data)

    def brightness(self, value):
        if not 0 <= value <= 15:
            raise ValueError("Brightness out of range")
        self._write(_INTENSITY, value)

    def _send(self, buf):
        """Push a buffer to the MAX7219 chips"""
        for y in range(8):
            self.cs(0)
            for m in range(self.num):
                self.spi.write(bytearray([_DIGIT0 + y, buf[(y * self.num) + m]]))
            self.cs(1)

    def show(self):
        """Send the framebuffer to the display, with rotation applied.
        The drawing buffer is never modified, so show() can be called
        any number of times without the image rotating further."""
        if self.rotation == 0:
            self._send(self.buffer)
            return

        out = self._out_fb
        out.fill(0)
        src = self.framebuf
        width = 8 * self.num
        for x in range(width):
            for y in range(8):
                if src.pixel(x, y):
                    tx, ty = self._transform_coords(x, y)
                    if 0 <= tx < width and 0 <= ty < 8:
                        out.pixel(tx, ty, 1)
        self._send(self._out)

    def write_matrix(self, matrix):
        """
        Write a 2D matrix of booleans/integers to the framebuffer

        Example:
            # Create a simple pattern
            pattern = [
                [1,0,1,0,1,0,1,0],
                [0,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,0],
                [0,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,0],
                [0,1,0,1,0,1,0,1],
                [1,0,1,0,1,0,1,0],
                [0,1,0,1,0,1,0,1]
            ]
            display.write_matrix(pattern)
            display.show()
        """
        height = len(matrix)
        if height == 0:
            return

        width = len(matrix[0])
        max_width = 8 * self.num

        # Clear the framebuffer first
        self.fill(0)

        # Write each pixel
        for y in range(min(height, 8)):  # MAX7219 is 8 pixels high
            for x in range(min(width, max_width)):  # Width depends on number of matrices
                if matrix[y][x]:  # Treats any truthy value as 'on'
                    self.pixel(x, y, 1)

    def read_matrix(self):
        """
        Read the framebuffer as a 2D matrix of booleans
        (unrotated, i.e. exactly what you drew)
        """
        width = 8 * self.num
        height = 8

        matrix = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel_val = self.pixel(x, y)
                row.append(bool(pixel_val))
            matrix.append(row)

        return matrix

    def write_pattern(self, pattern_string, char_on='1', char_off='0'):
        """
        Write a pattern from a multi-line string (useful for ASCII art)

        Example:
            pattern = '''
            10101010
            01010101
            10101010
            01010101
            10101010
            01010101
            10101010
            01010101
            '''
            display.write_pattern(pattern)
            display.show()
        """
        lines = [line.strip() for line in pattern_string.strip().split('\n') if line.strip()]
        matrix = []

        for line in lines:
            row = []
            for char in line:
                row.append(char == char_on)
            matrix.append(row)

        self.write_matrix(matrix)