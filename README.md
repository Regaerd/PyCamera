# PyCamera
Webcam terminal viewer.

### What
Dynamic webcam display for the terminal. Webcam footage is rendered using an ascii palette.

### Requires
`ncurses` and `opencv`

### Install
```
python setup.py install
```

### Run
```
python pycamera.py
```
If installed:
```
pycamera
```

### Controls

Keys  | Actions
----- | -------
<kbd>q</kbd> or <kbd>Q</kbd> or <kbd>Esc</kbd> | quit
<kbd>p</kbd> or <kbd>P</kbd> | pause camera output
<kbd>l</kbd> or <kbd>L</kbd> | switch to next ascii palette
<kbd>a</kbd> or <kbd>A</kbd> | toggle ascii display
<kbd>c</kbd> or <kbd>C</kbd> | toggle color display

### Extras
PyCamera supports real time resizing thanks to `ncurses`! Oooh! Ahhh!

### Support

- [x] Works on Linux completely

- [x] Works on OSX completely

- [ ] Windows not supported
